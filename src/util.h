#ifndef H_UTIL
#define H_UTIL

#include <string>

#include <clang/Basic/SourceLocation.h>
#include <clang/AST/ASTContext.h>

namespace bond {

std::string const build_loc_str(clang::SourceRange const &range,
                                clang::ASTContext const *ctx);

}; // bond

#endif // H_UTIL