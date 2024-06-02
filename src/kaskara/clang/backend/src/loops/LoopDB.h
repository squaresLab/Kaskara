#pragma once

#include <vector>
#include <string>

#include <nlohmann/json.hpp>
#include <clang/AST/Stmt.h>
#include <clang/AST/ASTContext.h>

namespace kaskara {

class LoopDB
{
public:
  LoopDB();
  ~LoopDB();

  class Entry {
  public:
    Entry(std::string const &kind,
          std::string const &location,
          std::string const &body);

    std::string const location;
    std::string const kind;
    std::string const body;

    nlohmann::json const to_json() const;
  }; // Entry

  void add(clang::ASTContext *ctx, clang::WhileStmt const *stmt);
  void add(clang::ASTContext *ctx, clang::ForStmt const *stmt);
  // void add(clang::ASTContext *ctx, clang::CXXForRangeStmt const *stmt);
  void dump() const;
  nlohmann::json to_json() const;
  void to_file(const std::string &fn) const;

private:
  std::vector<Entry> contents;
}; // LoopDB

} // kaskara
