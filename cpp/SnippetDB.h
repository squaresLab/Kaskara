#ifndef H_SNIPPET_DB
#define H_SNIPPET_DB

#include <vector>
#include <string>

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
    Entry(std::string const &kind,
          std::string const &contents);

    std::string const kind;
    std::string const contents;

    nlohmann::json const to_json() const;
  }; // Entry

  void dump() const;
  void add(std::string const &kind,
           clang::ASTContext const *ctx,
           clang::Stmt const *stmt);
  nlohmann::json to_json() const;
  void to_file(const std::string &fn) const;

private:
  std::vector<Entry> contents;
}; // SnippetDB

} // kaskara

#endif // H_SNIPPET_DB
