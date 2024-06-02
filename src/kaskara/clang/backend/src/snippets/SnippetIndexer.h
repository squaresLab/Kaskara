#pragma once

#include <memory>

#include <clang/Tooling/CommonOptionsParser.h>

#include "SnippetDB.h"

namespace kaskara {

std::unique_ptr<SnippetDB> IndexSnippets(
    clang::tooling::CommonOptionsParser &optionsParser
);

}
