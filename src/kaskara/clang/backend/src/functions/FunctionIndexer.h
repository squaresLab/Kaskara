#pragma once

#include <memory>

#include <clang/Tooling/CommonOptionsParser.h>

#include "FunctionDB.h"

namespace kaskara {

std::unique_ptr<FunctionDB> IndexFunctions(
    clang::tooling::CommonOptionsParser &optionsParser
);

}
