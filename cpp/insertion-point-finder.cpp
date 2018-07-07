// https://clang.llvm.org/docs/LibASTMatchersReference.html
// https://github.com/eschulte/clang-mutate/blob/master/ASTMutate.cpp
#include <vector>
#include <unordered_set>

#include <fmt/format.h>

#include <clang/Frontend/CompilerInstance.h>
#include <clang/Frontend/FrontendAction.h>
#include <clang/Frontend/FrontendActions.h>
#include <clang/Tooling/Tooling.h>
#include <clang/Tooling/CommonOptionsParser.h>

#include <clang/AST/DeclBase.h>
#include <clang/AST/DeclLookups.h>
#include <clang/AST/Decl.h>

#include <clang/AST/RecursiveASTVisitor.h>
//#include <clang/AST/LexicallyOrderedRecursiveASTVisitor.h>

#include "util.h"
#include "InsertionPointDB.h"

using namespace kaskara;

using namespace clang;
using namespace clang::tooling;

static llvm::cl::OptionCategory MyToolCategory("kaskara-insertion-point-finder options");
static llvm::cl::extrahelp CommonHelp(clang::tooling::CommonOptionsParser::HelpMessage);

class InsertionPointVisitor
  : public clang::RecursiveASTVisitor<InsertionPointVisitor>
{
public:
  explicit InsertionPointVisitor(clang::ASTContext *ctx,
                                 InsertionPointDB *db)
    : ctx(ctx), SM(ctx->getSourceManager()), db(db), visible()
  { }

  // https://stackoverflow.com/questions/10454075/avoid-traversing-included-system-libraries
  bool TraverseDecl(clang::Decl *decl)
  {
    if (!decl)
      return true;

    // FIXME this is awful
    if (ctx->getSourceManager().isInMainFile(decl->getLocation()) || std::string(decl->getDeclKindName()) == "TranslationUnit") {
      return clang::RecursiveASTVisitor<InsertionPointVisitor>::TraverseDecl(decl);
    } else {
      return true;
    }
  }

  // ignore null statements
  bool TraverseNullStmt(clang::NullStmt const *stmt)
  {
    return true;
  }

  bool VisitStmt(clang::Stmt *stmt)
  {
    // FIXME assignments are handled incorrectly
    // FIXME case statements
    // only visit "top-level" statements
    for (auto const &p : ctx->getParents(*stmt)) {
      if (p.get<clang::ReturnStmt>() || p.get<clang::Expr>() || p.get<clang::IfStmt>())
        return true;
    }

    // FIXME don't insert after the following:
    // - return statement
    // - throw statement
    // - break statement

    // ignore bad locations
    FullSourceLoc loc_insertion = ctx->getFullLoc(stmt->getLocEnd());
    if (loc_insertion.isInvalid())
      return true;

    // add to database
    // FIXME get insertion location
    clang::FileID file_id = loc_insertion.getFileID();
    clang::FileEntry const *file_entry = SM.getFileEntryForID(file_id);
    if (!file_entry) {
      llvm::outs() << "BAD LOCATION:\n";
      loc_insertion.dump();
      llvm::outs() << "\n";
      return true;
    }

    std::string filename = file_entry->tryGetRealPathName();
    std::string location =
      fmt::format(fmt("{0}@{1}:{2}"),
                  filename,
                  loc_insertion.getSpellingLineNumber(),
                  loc_insertion.getSpellingColumnNumber());

    // record insertion point
    db->add(location, visible);

    // llvm::outs() << "NICE: ";
    // stmt->dumpPretty(*ctx);
    // llvm::outs() << "\n\n";

    return true;
  }

  bool VisitDecl(clang::Decl *decl)
  {
    clang::DeclContext const *decl_ctx = decl->getDeclContext();
    if (!decl_ctx) {
      return true;
    }

    visible.clear();
    for (auto d : decl_ctx->lookups()) {
      for (auto dd : d) {
        std::string name = dd->getNameAsString();
        visible.emplace(name);
      }
    }
    return true;
  }

private:
  clang::ASTContext *ctx;
  clang::SourceManager &SM;
  InsertionPointDB *db;
  std::unordered_set<std::string> visible;
};

class InsertionPointConsumer : public clang::ASTConsumer
{
public:
  explicit InsertionPointConsumer(clang::ASTContext *ctx,
                                  InsertionPointDB *db)
    : visitor(ctx, db)
  {}

  virtual void HandleTranslationUnit(clang::ASTContext &ctx)
  {
    visitor.TraverseDecl(ctx.getTranslationUnitDecl());
  }

private:
  InsertionPointVisitor visitor;
};

class InsertionPointAction : public clang::ASTFrontendAction
{
public:
  InsertionPointAction(InsertionPointDB *db)
    : db(db), clang::ASTFrontendAction()
  { }

  virtual std::unique_ptr<clang::ASTConsumer> CreateASTConsumer(
    clang::CompilerInstance &compiler, llvm::StringRef in_file)
  {
    return std::unique_ptr<clang::ASTConsumer>(
        new InsertionPointConsumer(&compiler.getASTContext(), db));
  }

private:
  InsertionPointDB *db;
};

std::unique_ptr<clang::tooling::FrontendActionFactory> functionFinderFactory(
  InsertionPointDB *db)
{
  class InsertionPointActionFactory
    : public clang::tooling::FrontendActionFactory
  {
  public:
    InsertionPointActionFactory(InsertionPointDB *db)
      : db(db), clang::tooling::FrontendActionFactory()
    { }

    clang::FrontendAction *create() override
    {
      return new InsertionPointAction(db);
    }

  private:
    InsertionPointDB *db;
  };

  return std::unique_ptr<clang::tooling::FrontendActionFactory>(
      new InsertionPointActionFactory(db));
};

int main(int argc, const char **argv)
{
  CommonOptionsParser OptionsParser(argc, argv, MyToolCategory);
  ClangTool Tool(OptionsParser.getCompilations(),
                 OptionsParser.getSourcePathList());

  std::unique_ptr<InsertionPointDB> db(new InsertionPointDB);
  int res = Tool.run(functionFinderFactory(db.get()).get());
  db->to_file("insertion-points.json");
  return res;
}
