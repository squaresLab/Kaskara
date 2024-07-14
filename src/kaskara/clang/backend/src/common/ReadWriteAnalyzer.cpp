#include "ReadWriteAnalyzer.h"

#include <iostream>
#include <sstream>
#include <string>
#include <optional>
#include <stack>

#include <clang/AST/ASTTypeTraits.h>

#include "../util.h"

namespace kaskara {

// FIXME take non-const? use const cast?
std::optional<std::string> resolve_member_expr(clang::MemberExpr const *e, clang::ASTContext const *ctx)
{
  if (e == nullptr) {
    llvm::errs() << "[FATAL ERROR] null pointer provided to resolve_member_expr\n";
    abort();
  }

  // llvm::outs() << "[DEBUG] resolving member expression: ";
  // e->dump();
  // llvm::outs() << "\n";

  clang::MemberExpr const *parent = e;
  clang::Expr const *child = e->getBase();
  while (child) {
    // llvm::errs() << "[DEBUG] child expression: ";
    // child->dump(llvm::errs());
    // llvm::errs() << "\n";

    child = child->IgnoreImplicit()->IgnoreCasts()->IgnoreParens();
    // llvm::errs() << "[DEBUG] unwrapped expression: ";
    // child->dump(llvm::errs());
    // llvm::errs() << "\n";

    if (auto *member = clang::dyn_cast<clang::MemberExpr>(child)) {
      parent = member;
      child = member->getBase();
    } else if (auto *call = clang::dyn_cast<clang::CallExpr>(child)) {
      child = call->getCallee();
    // FIXME is this needed?
    } else if (auto *cast = clang::dyn_cast<clang::ImplicitCastExpr>(child)) {
      child = cast->getSubExprAsWritten();
    } else if (auto *root = clang::dyn_cast<clang::CXXThisExpr>(child)) {
      if (auto *field = clang::dyn_cast<clang::FieldDecl>(parent->getMemberDecl())) {
        return field->getNameAsString();
      }
      break;
    } else if (auto *root = clang::dyn_cast<clang::DeclRefExpr>(child)) {
      if (auto *var = clang::dyn_cast<clang::VarDecl>(root->getDecl())) {
        auto name = var->getNameAsString();
        return name;
      } else {
        llvm::errs() << "[ERROR] Unrecognized declrefexpr\n";
        break;
      }
      break;
    } else {
      llvm::errs() << "[ERROR] Failed to resolve member expression:\n";
      e->dump(llvm::errs(), *ctx);
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
  // llvm::outs() << "[DEBUG] visiting generic stmt...\n";
  for (clang::Stmt const *c : stmt->children()) {
    if (!c)
      continue;
    Visit(c);
  }
}

void ReadWriteAnalyzer::VisitBinaryOperator(clang::BinaryOperator const *op)
{
  // llvm::outs() << "[DEBUG] visiting binary operator...\n";
  VisitStmt(op);
  if (!op || !op->isAssignmentOp())
    return;

  clang::Expr const *expr = op->getLHS();
  // FIXME
  if (auto *dre = clang::dyn_cast<clang::DeclRefExpr>(expr)) {
    writes.emplace(dre->getNameInfo().getAsString());
  }
  if (auto *mex = clang::dyn_cast<clang::MemberExpr>(expr)) {
    if (auto resolved_name = resolve_member_expr(mex, ctx))
      writes.emplace(*resolved_name);
  }
}

void ReadWriteAnalyzer::VisitDeclStmt(clang::DeclStmt const *stmt)
{
  // llvm::outs() << "[DEBUG] visiting decl stmt...\n";
  VisitStmt(stmt);
  for (auto const d : stmt->decls()) {
    if (!d)
      continue;

    clang::NamedDecl const *nd = clang::DynTypedNode::create(*d).get<clang::NamedDecl>();
    if (!nd)
      continue;

    std::string name = nd->getName().str();
    decls.emplace(name);
    writes.emplace(name);
  }
}

void ReadWriteAnalyzer::VisitMemberExpr(clang::MemberExpr const *expr)
{
  // llvm::outs() << "[DEBUG] visiting member expr...\n";
  if (auto resolved = resolve_member_expr(expr, ctx))
    reads.emplace(*resolved);
}

void ReadWriteAnalyzer::VisitDeclRefExpr(clang::DeclRefExpr const *expr)
{
  // llvm::outs() << "[DEBUG] visiting decl ref expr...\n";
  // NOTE we do not record enum values
  if (auto const *var = clang::DynTypedNode::create(*expr->getDecl()).get<clang::VarDecl>())
    reads.emplace(var->getNameAsString());
}

} // kaskara
