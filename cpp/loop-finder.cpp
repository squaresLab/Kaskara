/**
 * Finds all loops within a set of files.
 */
#include <memory>

#include <clang/AST/ASTConsumer.h>
#include <clang/AST/RecursiveASTVisitor.h>
#include <clang/Frontend/CompilerInstance.h>
#include <clang/Frontend/FrontendAction.h>
#include <clang/Frontend/FrontendActions.h>
#include <clang/Tooling/Tooling.h>
#include <clang/Tooling/CommonOptionsParser.h>

#include "util.h"
#include "LoopDB.h"

using namespace kaskara;

static llvm::cl::OptionCategory MyToolCategory("my-tool options");
static llvm::cl::extrahelp CommonHelp(clang::tooling::CommonOptionsParser::HelpMessage);

class FindLoopVisitor
  : public clang::RecursiveASTVisitor<FindLoopVisitor>
{
public:
  explicit FindLoopVisitor(clang::ASTContext *ctx,
                           llvm::StringRef in_file,
                           LoopDB &db_loop)
    : ctx(ctx),
      SM(ctx->getSourceManager()),
      in_file(in_file),
      db_loop(db_loop)
  {}

  bool VisitWhileStmt(clang::WhileStmt const *stmt)
  {
    clang::FullSourceLoc loc = ctx->getFullLoc(stmt->getLocStart());
    std::string filename = SM.getFilename(loc);

    if (filename != in_file) {
      return true;
    }

    llvm::outs() << "recording while-stmt\n";
    stmt->dump();
    db_loop.add(ctx, stmt);
    llvm::outs() << "recorded while-stmt\n";
    return true;
  }

  bool VisitForStmt(clang::ForStmt const *stmt)
  {
    clang::FullSourceLoc loc = ctx->getFullLoc(stmt->getLocStart());
    std::string filename = SM.getFilename(loc);

    if (filename != in_file) {
      return true;
    }

    llvm::outs() << "recording for-stmt\n";
    db_loop.add(ctx, stmt);
    llvm::outs() << "recorded for-stmt\n";
    return true;
  }

private:
  clang::ASTContext *ctx;
  clang::SourceManager const &SM;
  std::string const in_file;
  kaskara::LoopDB &db_loop;
};

class FindLoopConsumer : public clang::ASTConsumer
{
public:
  explicit FindLoopConsumer(clang::ASTContext *ctx,
                            llvm::StringRef in_file,
                            LoopDB &db_loop)
    : visitor(ctx, in_file, db_loop)
  {}

  virtual void HandleTranslationUnit(clang::ASTContext &ctx)
  {
    visitor.TraverseDecl(ctx.getTranslationUnitDecl());
  }

private:
  FindLoopVisitor visitor;
};

class FindLoopAction : public clang::ASTFrontendAction
{
public:
  FindLoopAction(LoopDB &db_loop)
    : db_loop(db_loop), clang::ASTFrontendAction()
  { }

  virtual std::unique_ptr<clang::ASTConsumer> CreateASTConsumer(
    clang::CompilerInstance &compiler, llvm::StringRef in_file)
  {
    return std::unique_ptr<clang::ASTConsumer>(
        new FindLoopConsumer(&compiler.getASTContext(),
          in_file, db_loop));
  }

private:
  LoopDB &db_loop;
};

std::unique_ptr<clang::tooling::FrontendActionFactory> loopFinderFactory(
    LoopDB &db_loop)
{
  class LoopFinderActionFactory
    : public clang::tooling::FrontendActionFactory
  {
  public:
    LoopFinderActionFactory(LoopDB &db_loop)
      : db_loop(db_loop), clang::tooling::FrontendActionFactory()
    { }

    clang::FrontendAction *create() override
    {
      return new FindLoopAction(db_loop);
    }

  private:
    LoopDB &db_loop;
  };

  return std::unique_ptr<clang::tooling::FrontendActionFactory>(
      new LoopFinderActionFactory(db_loop));
};

int main(int argc, const char **argv)
{
  using namespace clang::tooling;
  CommonOptionsParser OptionsParser(argc, argv, MyToolCategory);
  ClangTool Tool(OptionsParser.getCompilations(),
                 OptionsParser.getSourcePathList());

  std::unique_ptr<LoopDB> db_loop(new LoopDB);
  auto res = Tool.run(loopFinderFactory(*db_loop).get());

  db_loop->dump();
  db_loop->to_file("loops.json");

  return res;
}
