#include "ReadWriteAnalyzer.h"

#include <iostream>

namespace kaskara {

ReadWriteAnalyzer::ReadWriteAnalyzer(
    clang::ASTContext const *ctx,
    std::unordered_set<std::string> &reads,
    std::unordered_set<std::string> &writes)
  : ctx(ctx), reads(reads), writes(writes)
{ }

void ReadWriteAnalyzer::analyze(
  clang::ASTContext const *ctx,
  clang::Stmt const *stmt,
  std::unordered_set<std::string> &reads,
  std::unordered_set<std::string> &writes)
{
  std::cout << "analyzing\n";
}

} // kaskara
