#include "ReadWriteAnalyzer.h"

#include <iostream>
#include <sstream>
#include <string>
#include <experimental/optional>
#include <stack>

#include <clang/AST/ASTTypeTraits.h>

#include "util.h"

using namespace clang::ast_type_traits;
using namespace std::experimental;

namespace kaskara {

optional<std::string> resolve_member_expr(clang::MemberExpr const *e)
{
  clang::MemberExpr const *parent = e;
  clang::Expr const *child = e->getBase();
  while (child) {
    if (auto const *member = DynTypedNode::create(*child).get<clang::MemberExpr>()) {
      parent = member;
      child = member->getBase();
    } else if (auto const *call = DynTypedNode::create(*child).get<clang::CallExpr>()) {
      child = call->getCallee();
    } else if (auto const *cast = DynTypedNode::create(*child).get<clang::ImplicitCastExpr>()) {
      child = cast->getSubExprAsWritten();
    } else if (auto const *root = DynTypedNode::create(*child).get<clang::CXXThisExpr>()) {
      if (auto const *field = DynTypedNode::create(*(parent->getMemberDecl())).get<clang::FieldDecl>())
        return field->getNameAsString();
      break;
    } else if (auto const *root = DynTypedNode::create(*child).get<clang::DeclRefExpr>()) {
      if (auto const *var = DynTypedNode::create(*(root->getDecl())).get<clang::VarDecl>())
        return var->getNameAsString();
      break;
    } else {
      llvm::errs() << "[ERROR] Failed to resolve member expression:\n";
      e->dump(llvm::errs());
      llvm::errs() << "[/ERROR]\n";
      break;
    }
  }
  return {};
}

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
  // llvm::outs() << "\n\nSTMT [" << stmt->getStmtClassName() << "]:\n";
  // stmt->dumpPretty(*ctx);
  // llvm::outs() << "\n";
  // stmt->dump(llvm::outs());

  for (clang::Stmt const *c : stmt->children()) {
    if (!c)
      continue;
    Visit(c);
  }
}

void ReadWriteAnalyzer::VisitBinaryOperator(clang::BinaryOperator const *op)
{
  VisitStmt(op);
  if (!op || !op->isAssignmentOp())
    return;

  clang::Expr const *expr = op->getLHS();
  // FIXME
  if (clang::DeclRefExpr const *dre = DynTypedNode::create(*expr).get<clang::DeclRefExpr>()) {
    writes.emplace(dre->getNameInfo().getAsString());
  }
  if (clang::MemberExpr const *mex = DynTypedNode::create(*expr).get<clang::MemberExpr>()) {
    if (auto resolved_name = resolve_member_expr(mex))
      writes.emplace(*resolved_name);
  }
}

void ReadWriteAnalyzer::VisitDeclStmt(clang::DeclStmt const *stmt)
{
  VisitStmt(stmt);
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

void ReadWriteAnalyzer::VisitMemberExpr(clang::MemberExpr const *expr)
{
  if (auto resolved = resolve_member_expr(expr))
    reads.emplace(*resolved);
}

void ReadWriteAnalyzer::VisitDeclRefExpr(clang::DeclRefExpr const *expr)
{
  // expr->dump();
  // NOTE we do not record enum values
  if (auto const *var = DynTypedNode::create(*expr->getDecl()).get<clang::VarDecl>())
    reads.emplace(var->getNameAsString());
}

} // kaskara
