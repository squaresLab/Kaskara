#include "ReadWriteAnalyzer.h"

#include <iostream>

namespace kaskara {

ReadWriteAnalyzer::ReadWriteAnalyzer(
    clang::ASTContext const *ctx,
    std::unordered_set<std::string> &reads,
    std::unordered_set<std::string> &writes)
  : ctx(ctx), reads(reads), writes(writes)
{ }

void ReadWriteAnalyzer::analyze(
  clang::ASTContext const *ctx,
  clang::Stmt const *stmt,
  std::unordered_set<std::string> &reads,
  std::unordered_set<std::string> &writes)
{
  ReadWriteAnalyzer analyzer(ctx, reads, writes);
  analyzer.Visit(stmt);
}

void ReadWriteAnalyzer::VisitStmt(clang::Stmt const *stmt)
{
  for (clang::Stmt const *c : stmt->children()) {
    if (!c)
      continue;
    Visit(c);
  }
}

void ReadWriteAnalyzer::VisitCXXDependentScopeMemberExpr(
    clang::CXXDependentScopeMemberExpr const *expr)
{
  if (!expr)
    return;

  // std::string name = expr->getMember().getAsString();
  // // only look at this->BLAH
  // llvm::outs() << "MEMBER: " << name << "\n";
}

void ReadWriteAnalyzer::VisitDeclRefExpr(clang::DeclRefExpr const *expr)
{
  reads.emplace(expr->getNameInfo().getAsString());
}

} // kaskara
