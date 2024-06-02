#pragma once

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
                      std::unordered_set<std::string> &writes,
                      std::unordered_set<std::string> &decls);

  void VisitStmt(clang::Stmt const *stmt);
  void VisitBinaryOperator(clang::BinaryOperator const *op);
  void VisitDeclRefExpr(clang::DeclRefExpr const *expr);
  void VisitDeclStmt(clang::DeclStmt const *stmt);
  void VisitMemberExpr(clang::MemberExpr const *expr);

private:
  explicit ReadWriteAnalyzer(clang::ASTContext const *ctx,
                             std::unordered_set<std::string> &reads,
                             std::unordered_set<std::string> &writes,
                             std::unordered_set<std::string> &decls);

  clang::ASTContext const *ctx;
  std::unordered_set<std::string> &reads;
  std::unordered_set<std::string> &writes;
  std::unordered_set<std::string> &decls;
};

} // kaskara
