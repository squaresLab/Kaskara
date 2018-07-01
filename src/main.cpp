#include <iostream>

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

using namespace std;
using namespace clang;
using namespace clang::tooling;
using namespace llvm;

static cl::OptionCategory MyToolCategory("my-tool options");
static cl::extrahelp CommonHelp(CommonOptionsParser::HelpMessage);

class FindNamedClassVisitor
  : public RecursiveASTVisitor<FindNamedClassVisitor> {
public:
  explicit FindNamedClassVisitor(ASTContext *Context, llvm::StringRef in_file)
    : Context(Context),
      SM(Context->getSourceManager()),
      in_file(in_file)
  {}

  bool VisitFunctionDecl(FunctionDecl *decl)
  {
    // d.isPure()

    FullSourceLoc loc = Context->getFullLoc(decl->getLocStart());

    string name = decl->getNameInfo().getName().getAsString();

    if (!decl->isThisDeclarationADefinition() ||
        !loc.isValid()) {
      return true;
    }

    string filename = SM.getFilename(loc);
    if (filename != in_file) {
      return true;
    }

    string loc_str = bond::build_loc_str(decl->getSourceRange(), Context);
    llvm::outs() << "FUNCTION: "
                 << name
                 << " at "
                 << loc_str
                 << "\n";

    return true;
  }

private:
  ASTContext *Context;
  SourceManager const &SM;
  string const in_file;
};

class FindNamedClassConsumer : public clang::ASTConsumer {
public:
  explicit FindNamedClassConsumer(ASTContext *ctx, llvm::StringRef in_file)
    : visitor(ctx, in_file) {}

  virtual void HandleTranslationUnit(clang::ASTContext &ctx) {
    visitor.TraverseDecl(ctx.getTranslationUnitDecl());
  }
private:
  FindNamedClassVisitor visitor;
};

class FindNamedClassAction : public clang::ASTFrontendAction {
public:
  virtual std::unique_ptr<clang::ASTConsumer> CreateASTConsumer(
    clang::CompilerInstance &compiler, llvm::StringRef in_file)
  {
    llvm::outs() << "looking in file:"
                 << in_file
                 << "\n";
    return std::unique_ptr<clang::ASTConsumer>(
        new FindNamedClassConsumer(&compiler.getASTContext(), in_file));
  }
};

int main(int argc, const char **argv) {
  CommonOptionsParser OptionsParser(argc, argv, MyToolCategory);
  ClangTool Tool(OptionsParser.getCompilations(),
                 OptionsParser.getSourcePathList());
  return Tool.run(newFrontendActionFactory<FindNamedClassAction>().get());
}
