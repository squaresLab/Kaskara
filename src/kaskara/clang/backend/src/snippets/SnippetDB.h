#pragma once

#include <unordered_map>
#include <string>
#include <unordered_set>

#include <nlohmann/json.hpp>
#include <clang/AST/Stmt.h>
#include <clang/AST/ASTContext.h>

namespace kaskara {

class SnippetDB
{
public:
  SnippetDB();
  ~SnippetDB();

  class Entry {
  public:
    Entry(); // FIXME
    Entry(std::string const &kind,
          std::string const &contents,
          std::unordered_set<std::string> const &reads);
    Entry(Entry const &other);

    std::string kind;
    std::string contents;
    std::unordered_set<std::string> locations;
    std::unordered_set<std::string> reads;

    void observe(std::string const &location);
    nlohmann::json const to_json() const;
  }; // Entry

  void dump() const;
  void add(std::string const &kind,
           clang::ASTContext const *ctx,
           clang::Stmt const *stmt);
  nlohmann::json to_json() const;
  void to_file(const std::string &fn) const;

private:
  std::unordered_map<std::string, Entry> contents;
}; // SnippetDB

} // kaskara
