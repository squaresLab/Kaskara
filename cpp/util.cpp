#include "util.h"

#include <fmt/format.h>

namespace kaskara {

std::string const build_loc_str(clang::SourceRange const &range,
                                clang::ASTContext const *ctx)
{
  clang::SourceManager const &SM = ctx->getSourceManager();
  clang::FullSourceLoc loc_begin = ctx->getFullLoc(range.getBegin());
  clang::FullSourceLoc loc_end = ctx->getFullLoc(range.getEnd());
  clang::FileID file_id = SM.getFileID(loc_begin);
  std::string filename = SM.getFileEntryForID(file_id)->tryGetRealPathName();
  std::string s = fmt::format(fmt("{0}@{1}:{2}::{3}:{4}"),
                              filename,
                              loc_begin.getSpellingLineNumber(),
                              loc_begin.getSpellingColumnNumber(),
                              loc_end.getSpellingLineNumber(),
                              loc_end.getSpellingColumnNumber());
  return s;
}

} // kaskara
