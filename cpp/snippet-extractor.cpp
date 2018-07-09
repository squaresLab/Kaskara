// https://clang.llvm.org/docs/LibASTMatchersReference.html
#include <vector>
#include <memory>

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
#include "util.h"

using namespace clang;
using namespace clang::ast_matchers;
using namespace clang::tooling;

using namespace kaskara;

static llvm::cl::OptionCategory MyToolCategory("kaskara-snippet-extractor options");
static llvm::cl::extrahelp CommonHelp(clang::tooling::CommonOptionsParser::HelpMessage);


StatementMatcher VoidCallMatcher =
  callExpr(isExpansionInMainFile(),
           argumentCountIs(0),
           unless(anyOf(hasParent(expr()),
                        hasParent(decl()),
                        hasParent(whileStmt()),
                        hasParent(forStmt()),
                        hasParent(ifStmt()),
                        hasParent(switchStmt()),
                        hasParent(cxxForRangeStmt())))).bind("stmt");

StatementMatcher GuardedVoidReturnMatcher =
  ifStmt(isExpansionInMainFile(),
         hasThen(returnStmt(unless(hasReturnValue(anything())))),
         unless(anyOf(
             hasElse(anything()),
             hasParent(expr()),
             hasParent(decl()),
             hasParent(whileStmt()),
             hasParent(ifStmt()),
             hasParent(switchStmt()),
             hasParent(cxxForRangeStmt())
         ))).bind("stmt");

StatementMatcher GuardedBreakMatcher =
  ifStmt(isExpansionInMainFile(),
         hasThen(breakStmt()),
         unless(anyOf(
             hasElse(anything()),
             hasParent(expr()),
             hasParent(decl()),
             hasParent(whileStmt()),
             hasParent(ifStmt()),
             hasParent(switchStmt()),
             hasParent(cxxForRangeStmt())
         ))).bind("stmt");

class SnippetFinder : public MatchFinder::MatchCallback
{
public:
  SnippetFinder(std::string const &kind, SnippetDB *db)
    : kind(kind), db(db)
  { }

  virtual void run(const MatchFinder::MatchResult &result)
  {
    SourceManager const *SM = result.SourceManager;
    if (const Stmt *stmt = result.Nodes.getNodeAs<clang::Stmt>("stmt")) {
      if (!stmt || stmt->getSourceRange().isInvalid())
        return;

      if (!SM->isInMainFile(stmt->getLocStart()))
          return;

      FileID fid = SM->getFileID(stmt->getLocStart());
      FileEntry const *fe = SM->getFileEntryForID(fid);
      if (!fe)
        return;

      std::string loc = build_loc_str(stmt->getSourceRange(), result.Context);
      // llvm::outs() << "found match [" << kind << "]: " << loc << "\n";
      db->add(kind, result.Context, stmt);
    }
  }

private:
  SnippetDB *db;
  std::string kind;
};

int main(int argc, const char **argv)
{
  CommonOptionsParser OptionsParser(argc, argv, MyToolCategory);
  ClangTool Tool(OptionsParser.getCompilations(),
                 OptionsParser.getSourcePathList());

  std::unique_ptr<SnippetDB> db(new SnippetDB);
  MatchFinder finder;

  SnippetFinder finder_return = SnippetFinder("guarded-return", db.get());
  finder.addMatcher(GuardedVoidReturnMatcher, &finder_return);

  SnippetFinder finder_break = SnippetFinder("guarded-break", db.get());
  finder.addMatcher(GuardedBreakMatcher, &finder_break);

  SnippetFinder finder_void_call = SnippetFinder("void-call", db.get());
  finder.addMatcher(VoidCallMatcher, &finder_void_call);

  auto res = Tool.run(newFrontendActionFactory(&finder).get());
  db->dump();
  db->to_file("snippets.json");
  return res;
}
