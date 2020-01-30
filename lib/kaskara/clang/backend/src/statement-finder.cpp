// https://clang.llvm.org/docs/LibASTMatchersReference.html
// https://github.com/eschulte/clang-mutate/blob/master/ASTMutate.cpp
#include <vector>
#include <unordered_set>
#include <sstream>

#include <fmt/format.h>

#include <clang/Frontend/CompilerInstance.h>
#include <clang/Frontend/FrontendAction.h>
#include <clang/Frontend/FrontendActions.h>
#include <clang/Tooling/Tooling.h>
#include <clang/Tooling/CommonOptionsParser.h>

#include <clang/AST/ASTTypeTraits.h>
#include <clang/AST/DeclBase.h>
#include <clang/AST/DeclLookups.h>
#include <clang/AST/Decl.h>
#include <clang/AST/RecursiveASTVisitor.h>

#include "util.h"
#include "StatementDB.h"

using namespace kaskara;

using namespace clang;
using namespace clang::tooling;
using namespace clang::ast_type_traits;

static llvm::cl::OptionCategory MyToolCategory("kaskara-statement-finder options");
static llvm::cl::extrahelp CommonHelp(clang::tooling::CommonOptionsParser::HelpMessage);


// FIXME hide this class; expose StatementDB::build(*ctx)
// https://clang.llvm.org/doxygen/classclang_1_1LexicallyOrderedRecursiveASTVisitor.html
class StatementVisitor
  : public clang::RecursiveASTVisitor<StatementVisitor>
{
public:
  explicit StatementVisitor(clang::ASTContext *ctx,
                            StatementDB *db)
    : ctx(ctx),
      SM(ctx->getSourceManager()),
      current_decl_ctx(nullptr),
      db(db),
      visible(),
      liveness(nullptr)
  { }

  // https://stackoverflow.com/questions/10454075/avoid-traversing-included-system-libraries
  bool TraverseDecl(clang::Decl *decl)
  {
    if (!decl)
      return true;

    // FIXME this is awful
    if (ctx->getSourceManager().isInMainFile(decl->getLocation()) || std::string(decl->getDeclKindName()) == "TranslationUnit") {
      return clang::RecursiveASTVisitor<StatementVisitor>::TraverseDecl(decl);
    } else {
      return true;
    }
  }

  bool is_inside_array_subscript(const DynTypedNode &n)
  {
    std::string kind = n.getNodeKind().asStringRef();
    if (kind == "ArraySubscriptExpr")
      return true;
    if (kind == "CompoundStmt")
      return false;
    for (auto const &p : ctx->getParents(n))
      if (is_inside_array_subscript(p))
        return true;
    return false;
  }

  bool is_inside_loop_header(clang::Stmt *stmt)
  {
    const DynTypedNode n = DynTypedNode::create(*stmt);
    auto const parents = ctx->getParents(n);
    if (parents.empty())
      return false;

    if (auto const p = parents[0].get<clang::WhileStmt>()) {
      if (p->getCond() == stmt)
        return true;
    } else if (auto const p = parents[0].get<clang::ForStmt>()) {
      if (p->getBody() != stmt)
        return true;
    }

    return false;
  }

  bool VisitStmt(clang::Stmt *stmt)
  {
    if (!stmt || stmt->getSourceRange().isInvalid())
      return true;

    if (!SM.isInMainFile(stmt->getLocStart()))
        return true;

    if (!SM.getFileEntryForID(SM.getFileID(stmt->getLocStart())))
      return true;

    // determine the node type
    std::string kind = ASTNodeKind::getFromNode(*stmt).asStringRef();
    if (kind == "CompoundStmt" ||
        kind == "BreakStmt" ||
        kind == "DefaultStmt" ||
        kind == "ContinueStmt" ||
        kind == "CaseStmt" ||
        kind == "ImplicitCastExpr" ||
        kind == "CXXCatchStmt" ||
        kind == "InitListExpr" ||
        kind == "IntegerLiteral" ||
        kind == "FloatingLiteral" ||
        kind == "StringLiteral" ||
        kind == "NullStmt") {
      return true;
    }

    // only visit "top-level" statements
    auto const parents = ctx->getParents(*stmt);
    for (auto const &p : parents) {
      if (p.get<clang::ReturnStmt>() ||
          p.get<clang::Expr>() ||
          p.get<clang::IfStmt>() ||
          p.get<clang::CaseStmt>() ||
          p.get<clang::Decl>() ||
          p.get<clang::SwitchStmt>() ||
          p.get<clang::DeclStmt>())
        return true;
    }

    // llvm::outs() << "NODE:\n";
    // stmt->dump(llvm::outs(), SM);
    // llvm::outs() << "PARENTS:\n";
    // for (auto const &p : parents) {
    //   p.dump(llvm::outs(), SM);
    // }

    if (is_inside_array_subscript(DynTypedNode::create(*stmt)))
      return true;
    if (is_inside_loop_header(stmt))
      return true;

    // llvm::outs() << "STMT [" << kind << "]: ";
    // stmt->dumpPretty(*ctx);
    // llvm::outs() << "\n";

    db->add(ctx, stmt, visible, liveness.get());
    return true;
  }

  void CollectVisibleDecls(clang::DeclContext const *dctx)
  {
    if (!dctx)
      return;

    for (clang::Decl const *d : dctx->decls()) {
      if (!d)
        continue;

      DynTypedNode node = DynTypedNode::create(*d);
      if (clang::VarDecl const *vd = node.get<clang::VarDecl>()) {
        if (vd->getIdentifier())
          visible.emplace(vd);
      }
      if (clang::FieldDecl const *fd = node.get<clang::FieldDecl>()) {
        if (fd->getIdentifier())
          visible.emplace(fd);
      }
    }

    CollectVisibleDecls(dctx->getParent());
  }

  // Upon visiting a function, we compute its liveness information.
  bool VisitFunctionDecl(clang::FunctionDecl *decl)
  {
    // std::string name = decl->getNameInfo().getAsString();
    // llvm::outs() << "computing liveness for function: " << name << "\n";
    std::unique_ptr<clang::AnalysisDeclContext> adc =
      std::unique_ptr<clang::AnalysisDeclContext>(new clang::AnalysisDeclContext(NULL, decl));
    liveness =
      std::unique_ptr<clang::LiveVariables>(clang::LiveVariables::create(*adc));
    return VisitDecl(decl);
  }

  bool VisitDecl(clang::Decl *decl)
  {
    // avoid rebuilding the same context multiple times
    clang::DeclContext const *decl_ctx = decl->getDeclContext();
    if (!decl_ctx || decl_ctx == current_decl_ctx) {
      return true;
    }
    current_decl_ctx = decl_ctx;
    visible.clear();
    CollectVisibleDecls(decl_ctx);

    return true;
  }

private:
  clang::ASTContext *ctx;
  clang::SourceManager &SM;
  clang::DeclContext const *current_decl_ctx;
  std::unique_ptr<clang::LiveVariables> liveness;
  StatementDB *db;
  std::unordered_set<clang::NamedDecl const *> visible;
};

class StatementConsumer : public clang::ASTConsumer
{
public:
  explicit StatementConsumer(clang::ASTContext *ctx,
                             StatementDB *db,
                             std::string &filename,
                             std::unordered_set<std::string> &visited_files)
    : visitor(ctx, db), filename(filename), visited_files(visited_files)
  { }

  virtual void HandleTranslationUnit(clang::ASTContext &ctx)
  {
    clang::SourceManager const &SM = ctx.getSourceManager();
    clang::Decl *decl = ctx.getTranslationUnitDecl();

    if (visited_files.find(filename) != visited_files.end()) {
      llvm::outs() << "ignoring file: " << filename << "\n";
    } else {
      llvm::outs() << "visiting file: " << filename << "\n";
      visited_files.emplace(filename);
      visitor.TraverseDecl(decl);
    }
  }

private:
  StatementVisitor visitor;
  std::string filename;
  std::unordered_set<std::string> &visited_files;
};

class StatementAction : public clang::ASTFrontendAction
{
public:
  StatementAction(StatementDB *db,
                  std::unordered_set<std::string> &visited_files)
    : db(db), visited_files(visited_files), clang::ASTFrontendAction()
  { }

  virtual std::unique_ptr<clang::ASTConsumer> CreateASTConsumer(
    clang::CompilerInstance &compiler, llvm::StringRef in_file)
  {
    const FileEntry *fe = compiler.getFileManager().getFile(in_file);
    if (!fe) {
      llvm::errs() << "failed to obtain file\n";
      exit(1);
    }
    std::string filename = fe->tryGetRealPathName();

    return std::unique_ptr<clang::ASTConsumer>(
        new StatementConsumer(&compiler.getASTContext(), db, filename, visited_files));
  }

private:
  StatementDB *db;
  std::unordered_set<std::string> &visited_files;
};

std::unique_ptr<clang::tooling::FrontendActionFactory> functionFinderFactory(
  StatementDB *db)
{
  class StatementActionFactory
    : public clang::tooling::FrontendActionFactory
  {
  public:
    StatementActionFactory(StatementDB *db)
      : db(db), visited_files(), clang::tooling::FrontendActionFactory()
    { }

    clang::FrontendAction *create() override
    {
      return new StatementAction(db, visited_files);
    }

  private:
    StatementDB *db;
    std::unordered_set<std::string> visited_files;
  };

  return std::unique_ptr<clang::tooling::FrontendActionFactory>(
      new StatementActionFactory(db));
};

int main(int argc, const char **argv)
{
  CommonOptionsParser OptionsParser(argc, argv, MyToolCategory);
  ClangTool Tool(OptionsParser.getCompilations(),
                 OptionsParser.getSourcePathList());

  std::unique_ptr<StatementDB> db(new StatementDB);
  int res = Tool.run(functionFinderFactory(db.get()).get());
  db->to_file("statements.json");
  return res;
}
