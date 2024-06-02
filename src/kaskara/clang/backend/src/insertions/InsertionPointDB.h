#pragma once

#include <vector>
#include <unordered_set>
#include <string>

#include <nlohmann/json.hpp>
#include <clang/AST/ASTContext.h>
#include <clang/AST/Decl.h>

namespace kaskara {

class InsertionPointDB
{
public:
  InsertionPointDB();
  ~InsertionPointDB();

  class Entry {
  public:
    Entry(std::string const &location,
          std::unordered_set<std::string> const &visible);

    nlohmann::json const to_json() const;

  private:
    std::string location;
    std::unordered_set<std::string> visible;
  }; // Entry

  void add(std::string const &location,
           std::unordered_set<std::string> const &visible);
  void dump() const;
  void to_file(const std::string &fn) const;
  nlohmann::json to_json() const;

private:
  std::vector<Entry> contents;
}; // InsertionPointDB

} // kaskara
