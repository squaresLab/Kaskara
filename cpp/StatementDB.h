#ifndef H_STATEMENT_DB
#define H_STATEMENT_DB

#include <vector>
#include <string>
#include <unordered_set>

#include <nlohmann/json.hpp>
#include <clang/AST/ASTContext.h>
#include <clang/AST/Decl.h>

namespace kaskara {

class StatementDB
{
public:
  StatementDB();
  ~StatementDB();

  class Entry {
  public:
    Entry(std::string const &location,
          std::string const &content,
          std::unordered_set<std::string> const &reads,
          std::unordered_set<std::string> const &writes);

    std::string location;
    std::string content;
    std::unordered_set<std::string> writes;
    std::unordered_set<std::string> reads;
    std::unordered_set<std::string> visible;

    nlohmann::json const to_json() const;
  }; // Entry

  void add(clang::ASTContext const *ctx,
           clang::Stmt const *stmt);
  void dump() const;
  nlohmann::json to_json() const;
  void to_file(const std::string &fn) const;

private:
  std::vector<Entry> contents;
}; // StatementDB

} // kaskara

#endif // H_STATEMENT_DB
