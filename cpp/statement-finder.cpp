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
      liveness(nullptr),
      in_scope()
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
        kind == "ReturnStmt" ||
        kind == "CaseStmt" ||
        kind == "ImplicitCastExpr" ||
        kind == "CXXCatchStmt" ||
        kind == "NullStmt") {
      return true;
    }

    // only visit "top-level" statements
    for (auto const &p : ctx->getParents(*stmt)) {
      if (p.get<clang::ReturnStmt>() ||
          p.get<clang::Expr>() ||
          p.get<clang::IfStmt>() ||
          p.get<clang::CaseStmt>() ||
          p.get<clang::Decl>() ||
          p.get<clang::SwitchStmt>() ||
          p.get<clang::DeclStmt>())
        return true;
    }

    // FIXME must belong to a real file
    // llvm::outs() << "STMT: ";
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

      // record variables
      if (clang::VarDecl const *vd = DynTypedNode::create(*d).get<clang::VarDecl>()) {
        if (!vd->getIdentifier())
          continue;

        // FIXME getQualifiedNameAsString // getName
        // std::string name = vd->getQualifiedNameAsString();
        std::string name = vd->getName();
        visible.emplace(name);
        in_scope.emplace(vd);
      }

      // record fields
      if (clang::FieldDecl const *fd = DynTypedNode::create(*d).get<clang::FieldDecl>()) {
        if (!fd->getIdentifier())
          continue;
        visible.emplace(fd->getName());
        in_scope.emplace(fd);
      }
    }

    CollectVisibleDecls(dctx->getParent());
  }

  // Upon visiting a function, we compute its liveness information.
  bool VisitFunctionDecl(clang::FunctionDecl *decl)
  {
    std::unique_ptr<clang::AnalysisDeclContext> adc =
      std::unique_ptr<clang::AnalysisDeclContext>(new clang::AnalysisDeclContext(NULL, decl));
    liveness =
      std::unique_ptr<clang::LiveVariables const>(clang::LiveVariables::create(*adc));
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
    in_scope.clear();
    CollectVisibleDecls(decl_ctx);

    //std::stringstream ss;
    //for (auto n : visible)
    //  ss << n << " ";
    //llvm::outs() << "VISIBLE: " << ss.str() << "\n";
    return true;
  }

private:
  clang::ASTContext *ctx;
  clang::SourceManager &SM;
  clang::DeclContext const *current_decl_ctx;
  std::unique_ptr<clang::LiveVariables const> liveness;
  StatementDB *db;
  std::unordered_set<std::string> visible;
  std::unordered_set<clang::Decl const *> in_scope;
};

class StatementConsumer : public clang::ASTConsumer
{
public:
  explicit StatementConsumer(clang::ASTContext *ctx,
                             StatementDB *db)
    : visitor(ctx, db)
  {}

  virtual void HandleTranslationUnit(clang::ASTContext &ctx)
  {
    visitor.TraverseDecl(ctx.getTranslationUnitDecl());
  }

private:
  StatementVisitor visitor;
};

class StatementAction : public clang::ASTFrontendAction
{
public:
  StatementAction(StatementDB *db)
    : db(db), clang::ASTFrontendAction()
  { }

  virtual std::unique_ptr<clang::ASTConsumer> CreateASTConsumer(
    clang::CompilerInstance &compiler, llvm::StringRef in_file)
  {
    return std::unique_ptr<clang::ASTConsumer>(
        new StatementConsumer(&compiler.getASTContext(), db));
  }

private:
  StatementDB *db;
};

std::unique_ptr<clang::tooling::FrontendActionFactory> functionFinderFactory(
  StatementDB *db)
{
  class StatementActionFactory
    : public clang::tooling::FrontendActionFactory
  {
  public:
    StatementActionFactory(StatementDB *db)
      : db(db), clang::tooling::FrontendActionFactory()
    { }

    clang::FrontendAction *create() override
    {
      return new StatementAction(db);
    }

  private:
    StatementDB *db;
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
