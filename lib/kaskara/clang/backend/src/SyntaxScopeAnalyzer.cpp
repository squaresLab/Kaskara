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

void SyntaxScopeAnalyzer::VisitStmt(clang::Stmt const *stmt)
{
  if (!stmt)
    return;
  for (clang::Stmt const *c : stmt->children()) {
    if (!c)
      continue;
    Visit(c);
  }
}

void SyntaxScopeAnalyzer::VisitBreakStmt(clang::BreakStmt const *stmt)
{
  results.requires_break = true;
}

void SyntaxScopeAnalyzer::VisitContinueStmt(clang::ContinueStmt const *stmt)
{
  results.requires_continue = true;
}

void SyntaxScopeAnalyzer::VisitForStmt(clang::ForStmt const *stmt) { }
void SyntaxScopeAnalyzer::VisitCXXForRangeStmt(clang::CXXForRangeStmt const *stmt) { }
void SyntaxScopeAnalyzer::VisitWhileStmt(clang::WhileStmt const *stmt) { }
void SyntaxScopeAnalyzer::VisitSwitchStmt(clang::SwitchStmt const *stmt) { }

} // kaskara
