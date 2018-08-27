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
    Visit(c);
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
    llvm::outs() << "NAMED DECL: " << name << "\n";
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
