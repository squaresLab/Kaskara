#include "util.h"

#include <fmt/format.h>
#include <llvm/ADT/StringRef.h>
#include <clang/Basic/LangOptions.h>
#include <clang/Lex/Lexer.h>
#include <clang/AST/Stmt.h>

namespace kaskara {

std::string const build_loc_str(clang::SourceRange const &range,
                                clang::ASTContext const *ctx)
{
  clang::SourceManager const &SM = ctx->getSourceManager();
  clang::FullSourceLoc loc_begin = ctx->getFullLoc(range.getBegin());
  clang::FullSourceLoc loc_end = ctx->getFullLoc(range.getEnd());
  clang::FileID file_id = SM.getDecomposedExpansionLoc(range.getBegin()).first;
  std::string filename = SM.getFileEntryForID(file_id)->tryGetRealPathName().str();

  std::string s = fmt::format(
    "{0}@{1}:{2}::{3}:{4}",
    filename,
    loc_begin.getExpansionLineNumber(),
    loc_begin.getExpansionColumnNumber() - 1,
    loc_end.getExpansionLineNumber(),
    loc_end.getExpansionColumnNumber()
  );
  return s;
}

clang::SourceRange stmt_to_range(clang::ASTContext const &ctx,
                                 clang::Stmt const *stmt)
{
  return expand_range_to_token_end(ctx.getSourceManager(),
                                   stmt->getSourceRange());
}

std::string stmt_to_source(clang::ASTContext const &ctx,
                           clang::Stmt const *stmt)
{
  return read_source(ctx, stmt_to_range(ctx, stmt));
}

clang::SourceRange expand_range_to_token_end(clang::SourceManager const &SM,
                                             clang::SourceRange const &range)
{
  return clang::SourceRange(range.getBegin(),
                            end_of_range(SM, range.getEnd()));
}

clang::SourceLocation end_of_range(clang::SourceManager const &SM,
                                   clang::SourceRange const &range)
{
  static const clang::LangOptions opts;
  return clang::Lexer::getLocForEndOfToken(range.getEnd(), 0, SM, opts);
}

std::string read_source(clang::SourceManager const &SM,
                        clang::SourceRange const &range)
{
  clang::SourceLocation loc_start = range.getBegin();
  clang::SourceLocation loc_end = range.getEnd();
  int length = SM.getFileOffset(loc_end) - SM.getFileOffset(loc_start);
  const char *buff = SM.getCharacterData(loc_start);
  return llvm::StringRef(buff, length + 1).str();
}

/*
std::string read_source(clang::SourceManager const &SM,
                        clang::SourceRange const &range)
{
  return read_source(SM, SM.getExpansionRange(range));
}
*/

std::string read_source(clang::ASTContext const &ctx,
                        clang::SourceRange const &range)
{
  return read_source(ctx.getSourceManager(), range);
}

} // kaskara
