// https://clang.llvm.org/docs/LibASTMatchersReference.html
#include <vector>

#include <clang/Frontend/CompilerInstance.h>
#include <clang/Frontend/FrontendAction.h>
#include <clang/Frontend/FrontendActions.h>
#include <clang/Tooling/Tooling.h>
#include <clang/Tooling/CommonOptionsParser.h>

#include <clang/AST/RecursiveASTVisitor.h>
#include <clang/AST/StmtVisitor.h>

#include <clang/ASTMatchers/ASTMatchers.h>
#include <clang/ASTMatchers/ASTMatchFinder.h>

using namespace clang;
using namespace clang::ast_matchers;
using namespace clang::tooling;

static llvm::cl::OptionCategory MyToolCategory("kaskara-snippet-extractor options");
static llvm::cl::extrahelp CommonHelp(clang::tooling::CommonOptionsParser::HelpMessage);


StatementMatcher VoidCallMatcher =
  callExpr(argumentCountIs(0)).bind("stmt");

StatementMatcher GuardedVoidReturnMatcher =
  ifStmt(hasThen(returnStmt(unless(hasReturnValue(anything())))),
         unless(hasElse(anything()))).bind("stmt");

StatementMatcher GuardedBreakMatcher =
  ifStmt(hasThen(breakStmt()), unless(hasElse(anything()))).bind("stmt");


class ReadWriteAnalyzer
  : public clang::ConstStmtVisitor<ReadWriteAnalyzer>
{
public:
  explicit ReadWriteAnalyzer(clang::ASTContext const *ctx)
    : ctx(ctx)
  { }

  void VisitStmt(clang::Stmt const *stmt)
  {
    //stmt->dumpPretty(*ctx);
    //llvm::outs() << "\n";
    for (clang::Stmt const *c : stmt->children()) {
      if (!c) {
        continue;
      }
      Visit(c);
    }
  }

  /*
  void VisitExpr(clang::Expr const *expr)
  {
    llvm::outs() << expr->getStmtClassName() << "\n";
    VisitStmt(llvm::dyn_cast<Stmt>(expr));
  }
  */

  void VisitDeclRefExpr(clang::DeclRefExpr const *expr)
  {
    llvm::outs() << "REF: " << expr->getNameInfo().getAsString() << "\n";
  }

private:
  clang::ASTContext const *ctx;
  std::vector<std::string> reads;
};

class SnippetFinder : public MatchFinder::MatchCallback
{
public:
  virtual void run(const MatchFinder::MatchResult &result)
  {
    if (const Stmt *stmt = result.Nodes.getNodeAs<clang::Stmt>("stmt")) {
      ReadWriteAnalyzer analyzer = ReadWriteAnalyzer(result.Context);
      stmt->dumpPretty(*result.Context);
      llvm::outs() << "\n";
      analyzer.Visit(stmt);
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
  // finder.addMatcher(VoidCallMatcher, &snippet_finder);
  finder.addMatcher(GuardedVoidReturnMatcher, &snippet_finder);

  auto res = Tool.run(newFrontendActionFactory(&finder).get());
  return res;
}
