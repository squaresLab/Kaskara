#pragma once

#include <memory>

#include <clang/Tooling/CommonOptionsParser.h>

#include "StatementDB.h"

namespace kaskara {

std::unique_ptr<StatementDB> IndexStatements(
    clang::tooling::CommonOptionsParser &optionsParser
);

}
