#ifndef H_READ_WRITE_ANALYZER
#define H_READ_WRITE_ANALYZER

#include <unordered_set>
#include <string>

#include <clang/AST/StmtVisitor.h>

namespace kaskara {

class ReadWriteAnalyzer
  : public clang::ConstStmtVisitor<ReadWriteAnalyzer>
{
public:
  static void analyze(clang::ASTContext const *ctx,
                      clang::Stmt const *stmt,
                      std::unordered_set<std::string> &reads,
                      std::unordered_set<std::string> &writes);

  void VisitStmt(clang::Stmt const *stmt);
  void VisitDeclRefExpr(clang::DeclRefExpr const *expr);
  void VisitCXXDependentScopeMemberExpr(
      clang::CXXDependentScopeMemberExpr const *expr);

private:
  explicit ReadWriteAnalyzer(clang::ASTContext const *ctx,
                             std::unordered_set<std::string> &reads,
                             std::unordered_set<std::string> &writes);

  clang::ASTContext const *ctx;
  std::unordered_set<std::string> &reads;
  std::unordered_set<std::string> &writes;
};

} // kaskara

#endif // H_READ_WRITE_ANALYZER
