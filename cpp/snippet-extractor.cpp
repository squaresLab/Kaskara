// https://clang.llvm.org/docs/LibASTMatchersReference.html
#include <vector>

#include <llvm/Support/raw_ostream.h>

#include <clang/Frontend/CompilerInstance.h>
#include <clang/Frontend/FrontendAction.h>
#include <clang/Frontend/FrontendActions.h>
#include <clang/Tooling/Tooling.h>
#include <clang/Tooling/CommonOptionsParser.h>

#include <clang/AST/RecursiveASTVisitor.h>
#include <clang/AST/StmtVisitor.h>

#include <clang/ASTMatchers/ASTMatchers.h>
#include <clang/ASTMatchers/ASTMatchFinder.h>

#include "SnippetDB.h"

using namespace clang;
using namespace clang::ast_matchers;
using namespace clang::tooling;

using namespace kaskara;

static llvm::cl::OptionCategory MyToolCategory("kaskara-snippet-extractor options");
static llvm::cl::extrahelp CommonHelp(clang::tooling::CommonOptionsParser::HelpMessage);


StatementMatcher VoidCallMatcher =
  callExpr(argumentCountIs(0)).bind("stmt");

StatementMatcher GuardedVoidReturnMatcher =
  ifStmt(hasThen(returnStmt(unless(hasReturnValue(anything())))),
         unless(hasElse(anything()))).bind("stmt");

StatementMatcher GuardedBreakMatcher =
  ifStmt(hasThen(breakStmt()), unless(hasElse(anything()))).bind("stmt");


class SnippetFinder : public MatchFinder::MatchCallback
{
public:
  SnippetFinder(SnippetDB &db) : db(db)
  { }

  virtual void run(const MatchFinder::MatchResult &result)
  {
    if (const Stmt *stmt = result.Nodes.getNodeAs<clang::Stmt>("stmt")) {
      // stmt->dumpPretty(*result.Context);
      // llvm::outs() << "\n";
      db.add("guarded-return", result.Context, stmt);
    }
  }

private:
  SnippetDB &db;
};

int main(int argc, const char **argv)
{
  CommonOptionsParser OptionsParser(argc, argv, MyToolCategory);
  ClangTool Tool(OptionsParser.getCompilations(),
                 OptionsParser.getSourcePathList());

  SnippetDB db;
  MatchFinder finder;
  SnippetFinder snippet_finder = SnippetFinder(db);
  // finder.addMatcher(VoidCallMatcher, &snippet_finder);
  finder.addMatcher(GuardedVoidReturnMatcher, &snippet_finder);

  auto res = Tool.run(newFrontendActionFactory(&finder).get());

  db.dump();

  return res;
}
