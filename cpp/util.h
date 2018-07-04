#ifndef H_UTIL
#define H_UTIL

#include <string>

#include <clang/Basic/SourceLocation.h>
#include <clang/AST/ASTContext.h>
#include <clang/Basic/SourceManager.h>

namespace kaskara {

std::string const build_loc_str(clang::SourceRange const &range,
                                clang::ASTContext const *ctx);

clang::SourceLocation end_of_range(clang::SourceManager const &SM,
                                   clang::SourceRange const &range);

std::string read_source(clang::SourceManager const &SM,
                        clang::SourceRange const &range);

std::string read_source(clang::ASTContext const &ctx,
                        clang::SourceRange const &range);

}; // kaskara

#endif // H_UTIL
