#ifndef H_SYNTAX_SCOPE_ANALYZER
#define H_SYNTAX_SCOPE_ANALYZER

#include <clang/AST/StmtVisitor.h>

namespace kaskara {

struct StatementSyntaxScope
{
  bool requires_break = false;
  bool requires_continue = false;
  bool allows_break = false;
  bool allows_continue = false;
};

class SyntaxScopeAnalyzer
  : public clang::ConstStmtVisitor<SyntaxScopeAnalyzer>
{
public:
  static StatementSyntaxScope const analyze(clang::ASTContext const *ctx,
                                            clang::Stmt const *stmt);

  // void VisitStmt(clang::Stmt const *stmt);

private:
  explicit SyntaxScopeAnalyzer(clang::ASTContext const *ctx,
                               StatementSyntaxScope &results);

  clang::ASTContext const *ctx;
  StatementSyntaxScope &results;
};

} // kaskara

#endif // H_SYNTAX_SCOPE_ANALYZER
