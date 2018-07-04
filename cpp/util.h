#ifndef H_UTIL
#define H_UTIL

#include <string>

#include <clang/Basic/SourceLocation.h>
#include <clang/AST/ASTContext.h>
#include <clang/Basic/SourceManager.h>

namespace kaskara {

std::string const build_loc_str(clang::SourceRange const &range,
                                clang::ASTContext const *ctx);

clang::SourceRange stmt_to_range(clang::ASTContext const &ctx,
                                 clang::Stmt const *stmt);

std::string stmt_to_source(clang::ASTContext const &ctx,
                           clang::Stmt const *stmt);

clang::SourceRange expand_range_to_token_end(clang::SourceManager const &SM,
                                             clang::SourceRange const &range);

clang::SourceLocation end_of_range(clang::SourceManager const &SM,
                                   clang::SourceRange const &range);

std::string read_source(clang::SourceManager const &SM,
                        clang::SourceRange const &range);

std::string read_source(clang::ASTContext const &ctx,
                        clang::SourceRange const &range);

}; // kaskara

#endif // H_UTIL
