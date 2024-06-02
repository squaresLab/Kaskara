#pragma once

#include <memory>

#include <clang/Tooling/CommonOptionsParser.h>

#include "LoopDB.h"

namespace kaskara {

std::unique_ptr<LoopDB> IndexLoops(
    clang::tooling::CommonOptionsParser &optionsParser
);

}
