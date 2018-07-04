// https://clang.llvm.org/docs/LibASTMatchersReference.html
#include <clang/Frontend/CompilerInstance.h>
#include <clang/Frontend/FrontendAction.h>
#include <clang/Frontend/FrontendActions.h>
#include <clang/Tooling/Tooling.h>
#include <clang/Tooling/CommonOptionsParser.h>

#include <clang/ASTMatchers/ASTMatchers.h>
#include <clang/ASTMatchers/ASTMatchFinder.h>

using namespace clang;
using namespace clang::ast_matchers;
using namespace clang::tooling;

static llvm::cl::OptionCategory MyToolCategory("kaskara-snippet-extractor options");
static llvm::cl::extrahelp CommonHelp(clang::tooling::CommonOptionsParser::HelpMessage);

// returnStmt

StatementMatcher GuardedBreakMatcher =
  ifStmt(hasThen(breakStmt()), unless(hasElse(anything()))).bind("if-stmt");

class SnippetFinder : public MatchFinder::MatchCallback
{
public:
  virtual void run(const MatchFinder::MatchResult &result)
  {
    if (const IfStmt *stmt = result.Nodes.getNodeAs<clang::IfStmt>("if-stmt")) {
      stmt->dumpPretty(*result.Context);
      llvm::outs() << "\n";
    }
  }
};

int main(int argc, const char **argv)
{
  CommonOptionsParser OptionsParser(argc, argv, MyToolCategory);
  ClangTool Tool(OptionsParser.getCompilations(),
                 OptionsParser.getSourcePathList());

  MatchFinder finder;
  SnippetFinder snippet_finder;
  finder.addMatcher(GuardedBreakMatcher, &snippet_finder);

  auto res = Tool.run(newFrontendActionFactory(&finder).get());
  return res;
}
