#include "ReadWriteAnalyzer.h"

#include <iostream>

#include <clang/AST/ASTTypeTraits.h>

#include "util.h"

using namespace clang::ast_type_traits;

namespace kaskara {

ReadWriteAnalyzer::ReadWriteAnalyzer(
    clang::ASTContext const *ctx,
    std::unordered_set<std::string> &reads,
    std::unordered_set<std::string> &writes,
    std::unordered_set<std::string> &decls)
  : ctx(ctx), reads(reads), writes(writes), decls(decls)
{ }

void ReadWriteAnalyzer::analyze(
  clang::ASTContext const *ctx,
  clang::Stmt const *stmt,
  std::unordered_set<std::string> &reads,
  std::unordered_set<std::string> &writes,
  std::unordered_set<std::string> &decls)
{
  ReadWriteAnalyzer analyzer(ctx, reads, writes, decls);
  analyzer.Visit(stmt);
}

void ReadWriteAnalyzer::VisitStmt(clang::Stmt const *stmt)
{
  for (clang::Stmt const *c : stmt->children()) {
    if (!c)
      continue;

    // llvm::outs() << "\n\nSTMT [" << stmt->getStmtClassName() << "]:\n";
    // c->dumpPretty(*ctx);
    Visit(c);
  }
}

void ReadWriteAnalyzer::VisitBinaryOperator(clang::BinaryOperator const *op)
{
  if (!op || !op->isAssignmentOp())
    return;

  clang::Expr const *expr = op->getLHS();

  if (clang::DeclRefExpr const *dre = DynTypedNode::create(*expr).get<clang::DeclRefExpr>()) {
    writes.emplace(dre->getNameInfo().getAsString());
    return;
  }

  // FIXME ensure consistent handling of MemberExpr
  if (clang::MemberExpr const *mex = DynTypedNode::create(*expr).get<clang::MemberExpr>()) {
    // llvm::outs() << "BASE: " << mex->getBase()->getStmtClassName() << "\n";

    if (clang::CXXThisExpr const *base = DynTypedNode::create(*mex->getBase()).get<clang::CXXThisExpr>())
      writes.emplace(mex->getMemberNameInfo().getAsString());
  }
}

void ReadWriteAnalyzer::VisitDeclStmt(clang::DeclStmt const *stmt)
{
  for (auto const d : stmt->decls()) {
    if (!d)
      continue;

    clang::NamedDecl const *nd = DynTypedNode::create(*d).get<clang::NamedDecl>();
    if (!nd)
      continue;

    std::string name = nd->getName();
    decls.emplace(name);
    writes.emplace(name);
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
