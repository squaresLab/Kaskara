#include <iostream>
#include <memory>

#include <fmt/format.h>

#include <llvm/IR/BasicBlock.h>

#include <clang/Analysis/Analyses/LiveVariables.h>
#include <clang/AST/ASTConsumer.h>
#include <clang/AST/RecursiveASTVisitor.h>
#include <clang/Frontend/CompilerInstance.h>
#include <clang/Frontend/FrontendAction.h>
#include <clang/Frontend/FrontendActions.h>
#include <clang/Tooling/Tooling.h>
#include <clang/Tooling/CommonOptionsParser.h>

#include "util.h"
#include "FunctionDB.h"

using namespace std;
using namespace clang;
using namespace clang::tooling;
using namespace llvm;

static cl::OptionCategory MyToolCategory("my-tool options");
static cl::extrahelp CommonHelp(CommonOptionsParser::HelpMessage);

class FindNamedClassVisitor
  : public RecursiveASTVisitor<FindNamedClassVisitor> {
public:
  explicit FindNamedClassVisitor(ASTContext *ctx,
                                 llvm::StringRef in_file,
                                 kaskara::FunctionDB &db_function)
    : ctx(ctx),
      SM(ctx->getSourceManager()),
      in_file(in_file),
      db_function(db_function)
  {}

  bool VisitFunctionDecl(FunctionDecl const *decl)
  {
    // d.isPure()

    FullSourceLoc loc = ctx->getFullLoc(decl->getLocStart());
    string name = decl->getNameInfo().getName().getAsString();

    if (!decl->isThisDeclarationADefinition() ||
        !loc.isValid()) {
      return true;
    }

    string filename = SM.getFilename(loc);
    if (filename != in_file) {
      return true;
    }

    // register function
    string loc_str = kaskara::build_loc_str(decl->getSourceRange(), ctx);
    string return_type = decl->getReturnType().getAsString();
    db_function.add(name, loc_str, return_type, decl->isPure());
    return true;
  }

private:
  ASTContext *ctx;
  SourceManager const &SM;
  string const in_file;
  kaskara::FunctionDB &db_function;
};

class FindNamedClassConsumer : public clang::ASTConsumer {
public:
  explicit FindNamedClassConsumer(ASTContext *ctx,
                                  llvm::StringRef in_file,
                                  kaskara::FunctionDB &db_function)
    : visitor(ctx, in_file, db_function) {}

  virtual void HandleTranslationUnit(clang::ASTContext &ctx) {
    visitor.TraverseDecl(ctx.getTranslationUnitDecl());
  }
private:
  FindNamedClassVisitor visitor;
};

class FindNamedClassAction : public clang::ASTFrontendAction {
public:
  FindNamedClassAction(kaskara::FunctionDB &db_function)
    : db_function(db_function), clang::ASTFrontendAction()
  { }

  virtual std::unique_ptr<clang::ASTConsumer> CreateASTConsumer(
    clang::CompilerInstance &compiler, llvm::StringRef in_file)
  {
    llvm::outs() << "looking in file:"
                 << in_file
                 << "\n";
    return std::unique_ptr<clang::ASTConsumer>(
        new FindNamedClassConsumer(&compiler.getASTContext(),
          in_file, db_function));
  }

private:
  kaskara::FunctionDB &db_function;
};

std::unique_ptr<FrontendActionFactory> lando(kaskara::FunctionDB &db_function)
{
  class CoolJellyDog : public FrontendActionFactory
  {
  public:
    CoolJellyDog(kaskara::FunctionDB &db_function) :
      db_function(db_function), FrontendActionFactory()
    { };

    clang::FrontendAction *create() override {
      return new FindNamedClassAction(db_function);
    }
  private:
    kaskara::FunctionDB &db_function;
  };
  return std::unique_ptr<FrontendActionFactory>(new CoolJellyDog(db_function));
};

int main(int argc, const char **argv) {
  CommonOptionsParser OptionsParser(argc, argv, MyToolCategory);
  ClangTool Tool(OptionsParser.getCompilations(),
                 OptionsParser.getSourcePathList());

  std::unique_ptr<kaskara::FunctionDB> db_function(
      new kaskara::FunctionDB);
  auto res = Tool.run(lando(*db_function).get());

  // dump
  db_function->dump();

  return res;
}
