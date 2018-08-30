#include "SyntaxScopeAnalyzer.h"

namespace kaskara {

SyntaxScopeAnalyzer::SyntaxScopeAnalyzer(
    clang::ASTContext const *ctx,
    StatementSyntaxScope &results)
  : ctx(ctx), results(results)
{ }

StatementSyntaxScope const SyntaxScopeAnalyzer::analyze(
  clang::ASTContext const *ctx,
  clang::Stmt const *stmt)
{
  StatementSyntaxScope results;
  SyntaxScopeAnalyzer analyzer(ctx, results);
  analyzer.Visit(stmt);
  return results;
}

} // kaskara
