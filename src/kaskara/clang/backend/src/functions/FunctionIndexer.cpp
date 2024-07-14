/**
 * Finds all functions within a set of files.
 */

#include "FunctionIndexer.h"

#include <memory>

#include <clang/AST/ASTConsumer.h>
#include <clang/AST/RecursiveASTVisitor.h>
#include <clang/Frontend/CompilerInstance.h>
#include <clang/Frontend/FrontendAction.h>
#include <clang/Frontend/FrontendActions.h>
#include <clang/Tooling/Tooling.h>
#include <clang/Tooling/CommonOptionsParser.h>

#include <clang/AST/DeclBase.h>
#include <clang/AST/DeclLookups.h>
#include <clang/AST/Decl.h>

#include "../util.h"

namespace kaskara {

class FindFunctionVisitor
  : public clang::RecursiveASTVisitor<FindFunctionVisitor>
{
public:
  explicit FindFunctionVisitor(clang::ASTContext *ctx,
                               llvm::StringRef in_file,
                               FunctionDB &db)
    : ctx(ctx),
      SM(ctx->getSourceManager()),
      in_file(in_file),
      db(db)
  {}

  bool VisitFunctionDecl(clang::FunctionDecl const *decl)
  {
    if (!decl->isThisDeclarationADefinition())
      return true;

    clang::FullSourceLoc loc = ctx->getFullLoc(decl->getBeginLoc());
    std::string filename = SM.getFilename(loc).str();
    if (filename != in_file) {
      return true;
    }

    // TODO get scope info
    // llvm::outs() << "SCOPE: ";
    std::vector<std::string> visible;
    for (auto d : decl->getDeclContext()->lookups()) {
      for (auto dd : d) {
        std::string name = dd->getNameAsString();
        visible.push_back(name);
        // llvm::outs() << " " << name;
      }
    }
    // llvm::outs() << "\n";

    // dump

    db.add(ctx, decl);
    return true;
  }

private:
  clang::ASTContext *ctx;
  clang::SourceManager const &SM;
  std::string const in_file;
  kaskara::FunctionDB &db;
};

class FindFunctionConsumer : public clang::ASTConsumer
{
public:
  explicit FindFunctionConsumer(clang::ASTContext *ctx,
                                llvm::StringRef in_file,
                                FunctionDB &db_func)
    : visitor(ctx, in_file, db_func)
  {}

  virtual void HandleTranslationUnit(clang::ASTContext &ctx)
  {
    visitor.TraverseDecl(ctx.getTranslationUnitDecl());
  }

private:
  FindFunctionVisitor visitor;
};

class FindFunctionAction : public clang::ASTFrontendAction
{
public:
  FindFunctionAction(FunctionDB &db_func)
    : db_func(db_func), clang::ASTFrontendAction()
  { }

  virtual std::unique_ptr<clang::ASTConsumer> CreateASTConsumer(
    clang::CompilerInstance &compiler, llvm::StringRef in_file)
  {
    return std::unique_ptr<clang::ASTConsumer>(
        new FindFunctionConsumer(&compiler.getASTContext(),
          in_file, db_func));
  }

private:
  FunctionDB &db_func;
};

std::unique_ptr<clang::tooling::FrontendActionFactory> functionFinderFactory(
    FunctionDB &db_func)
{
  class FunctionFinderActionFactory
    : public clang::tooling::FrontendActionFactory
  {
  public:
    FunctionFinderActionFactory(FunctionDB &db_func)
      : db_func(db_func), clang::tooling::FrontendActionFactory()
    { }

    std::unique_ptr<clang::FrontendAction> create() override
    {
      return std::make_unique<FindFunctionAction>(db_func);
    }

  private:
    FunctionDB &db_func;
  };

  return std::unique_ptr<clang::tooling::FrontendActionFactory>(
      new FunctionFinderActionFactory(db_func));
};

std::unique_ptr<FunctionDB> IndexFunctions(
    clang::tooling::CommonOptionsParser &optionsParser
) {
  std::unique_ptr<FunctionDB> db_func(new FunctionDB);
  clang::tooling::ClangTool Tool(
    optionsParser.getCompilations(),
    optionsParser.getSourcePathList()
  );
  Tool.run(functionFinderFactory(*db_func).get());
  return db_func;
}

}
