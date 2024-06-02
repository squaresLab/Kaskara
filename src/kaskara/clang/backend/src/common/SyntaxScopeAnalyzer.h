#pragma once

#include <clang/AST/StmtVisitor.h>

namespace kaskara {

struct StatementSyntaxScope
{
  bool requires_break = false;
  bool requires_continue = false;
};

class SyntaxScopeAnalyzer
  : public clang::ConstStmtVisitor<SyntaxScopeAnalyzer>
//  : public clang::RecursiveASTVisitor<SyntaxScopeAnalyzer>
{
public:
  static StatementSyntaxScope const analyze(clang::ASTContext const *ctx,
                                            clang::Stmt const *stmt);

  void VisitStmt(clang::Stmt const *stmt);
  void VisitForStmt(clang::ForStmt const *stmt);
  void VisitCXXForRangeStmt(clang::CXXForRangeStmt const *stmt);
  void VisitWhileStmt(clang::WhileStmt const *stmt);
  void VisitBreakStmt(clang::BreakStmt const *stmt);
  void VisitContinueStmt(clang::ContinueStmt const *stmt);
  void VisitSwitchStmt(clang::SwitchStmt const *stmt);

private:
  explicit SyntaxScopeAnalyzer(clang::ASTContext const *ctx,
                               StatementSyntaxScope &results);

  clang::ASTContext const *ctx;
  StatementSyntaxScope &results;
};

} // kaskara
