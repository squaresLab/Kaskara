// https://clang.llvm.org/docs/LibASTMatchersReference.html
// https://github.com/eschulte/clang-mutate/blob/master/ASTMutate.cpp
#include "InsertionsIndexer.h"

#include <vector>
#include <unordered_set>

#include <fmt/format.h>

#include <clang/Frontend/CompilerInstance.h>
#include <clang/Frontend/FrontendAction.h>
#include <clang/Frontend/FrontendActions.h>
#include <clang/Tooling/Tooling.h>
#include <clang/Tooling/CommonOptionsParser.h>

#include <clang/AST/ASTTypeTraits.h>

#include <clang/AST/DeclBase.h>
#include <clang/AST/DeclLookups.h>
#include <clang/AST/Decl.h>
#include <clang/AST/ParentMapContext.h>

#include <clang/AST/RecursiveASTVisitor.h>

#include "../util.h"

using namespace clang;
using namespace clang::tooling;

namespace kaskara {

class InsertionPointVisitor
  : public clang::RecursiveASTVisitor<InsertionPointVisitor>
{
public:
  explicit InsertionPointVisitor(clang::ASTContext *ctx,
                                 InsertionPointDB *db)
    : ctx(ctx),
      SM(ctx->getSourceManager()),
      current_decl_ctx(nullptr),
      db(db),
      visible()
  { }

  // https://stackoverflow.com/questions/10454075/avoid-traversing-included-system-libraries
  bool TraverseDecl(clang::Decl *decl)
  {
    if (!decl)
      return true;

    // FIXME this is awful
    if (ctx->getSourceManager().isInMainFile(decl->getLocation()) || std::string(decl->getDeclKindName()) == "TranslationUnit") {
      return clang::RecursiveASTVisitor<InsertionPointVisitor>::TraverseDecl(decl);
    } else {
      return true;
    }
  }

  bool VisitStmt(clang::Stmt *stmt)
  {
    // determine the node type
    std::string kind = ASTNodeKind::getFromNode(*stmt).asStringRef().str();
    if (kind == "CompoundStmt" ||
        kind == "BreakStmt" ||
        kind == "DefaultStmt" ||
        kind == "ContinueStmt" ||
        kind == "ReturnStmt" ||
        kind == "CaseStmt" ||
        kind == "ImplicitCastExpr" ||
        kind == "CXXCatchStmt" ||
        kind == "NullStmt") {
      return true;
    }

    // only visit "top-level" statements
    for (auto const &p : ctx->getParents(*stmt)) {
      if (p.get<clang::ReturnStmt>() ||
          p.get<clang::Expr>() ||
          p.get<clang::IfStmt>() ||
          p.get<clang::CaseStmt>() ||
          p.get<clang::Decl>() ||
          p.get<clang::SwitchStmt>() ||
          p.get<clang::DeclStmt>())
        return true;
    }

    // determine the insertion point
    SourceRange stmt_range =
      expand_range_to_token_end(SM, stmt->getSourceRange());
    FullSourceLoc loc_insertion = ctx->getFullLoc(stmt_range.getEnd());

    // ignore bad insertion points
    if (loc_insertion.isInvalid())
      return true;

    // add to database
    clang::FileID file_id = loc_insertion.getFileID();
    clang::FileEntry const *file_entry = SM.getFileEntryForID(file_id);
    if (!file_entry)
      return true;

    std::string filename = file_entry->tryGetRealPathName().str();
    std::string location = fmt::format(
      "{0}@{1}:{2}",
      filename,
      loc_insertion.getSpellingLineNumber(),
      loc_insertion.getSpellingColumnNumber()
    );

    // record insertion point
    db->add(location, visible);

    // std::string src = read_source(SM, stmt_range);
    // llvm::outs() << "NICE [" << kind << "]: " << src << "\n\n";

    return true;
  }

  void CollectVisibleDecls(clang::DeclContext const *dctx)
  {
    if (!dctx)
      return;

    for (clang::Decl const *d : dctx->decls()) {
      if (!d)
        continue;

      clang::NamedDecl const *nd = DynTypedNode::create(*d).get<clang::NamedDecl>();
      if (!nd || !nd->getIdentifier())
        continue;

      // FIXME getQualifiedNameAsString // getName
      // std::string name = nd->getQualifiedNameAsString();
      std::string name = nd->getName().str();
      visible.emplace(name);
    }

    CollectVisibleDecls(dctx->getLexicalParent());
  }

  bool VisitDecl(clang::Decl *decl)
  {
    // avoid rebuilding the same context multiple times
    clang::DeclContext const *decl_ctx = decl->getDeclContext();
    if (!decl_ctx || decl_ctx == current_decl_ctx) {
      return true;
    }
    current_decl_ctx = decl_ctx;
    visible.clear();
    CollectVisibleDecls(decl_ctx);
    return true;
  }

private:
  clang::ASTContext *ctx;
  clang::SourceManager &SM;
  clang::DeclContext const *current_decl_ctx;
  InsertionPointDB *db;
  std::unordered_set<std::string> visible;
};

class InsertionPointConsumer : public clang::ASTConsumer
{
public:
  explicit InsertionPointConsumer(clang::ASTContext *ctx,
                                  InsertionPointDB *db)
    : visitor(ctx, db)
  {}

  virtual void HandleTranslationUnit(clang::ASTContext &ctx)
  {
    visitor.TraverseDecl(ctx.getTranslationUnitDecl());
  }

private:
  InsertionPointVisitor visitor;
};

class InsertionPointAction : public clang::ASTFrontendAction
{
public:
  InsertionPointAction(InsertionPointDB *db)
    : db(db), clang::ASTFrontendAction()
  { }

  virtual std::unique_ptr<clang::ASTConsumer> CreateASTConsumer(
    clang::CompilerInstance &compiler, llvm::StringRef in_file)
  {
    return std::unique_ptr<clang::ASTConsumer>(
        new InsertionPointConsumer(&compiler.getASTContext(), db));
  }

private:
  InsertionPointDB *db;
};

std::unique_ptr<clang::tooling::FrontendActionFactory> insertionPointFinderFactory(
  InsertionPointDB *db
) {
  class InsertionPointActionFactory
    : public clang::tooling::FrontendActionFactory
  {
  public:
    InsertionPointActionFactory(InsertionPointDB *db)
      : db(db), clang::tooling::FrontendActionFactory()
    { }

    std::unique_ptr<clang::FrontendAction> create() override
    {
      return std::make_unique<InsertionPointAction>(db);
    }

  private:
    InsertionPointDB *db;
  };

  return std::unique_ptr<clang::tooling::FrontendActionFactory>(
      new InsertionPointActionFactory(db));
};

std::unique_ptr<InsertionPointDB> IndexInsertions(
    clang::tooling::CommonOptionsParser &optionsParser
) {
  auto db = std::make_unique<InsertionPointDB>();
  clang::tooling::ClangTool Tool(
    optionsParser.getCompilations(),
    optionsParser.getSourcePathList()
  );
  Tool.run(insertionPointFinderFactory(db.get()).get());
  return db;
}

}
