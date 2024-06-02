#pragma once

#include <memory>

#include <clang/Tooling/CommonOptionsParser.h>

#include "InsertionPointDB.h"

namespace kaskara {

std::unique_ptr<InsertionPointDB> IndexInsertions(
    clang::tooling::CommonOptionsParser &optionsParser
);

}
