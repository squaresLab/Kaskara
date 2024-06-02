#ifndef H_FUNCTION_DB
#define H_FUNCTION_DB

#include <vector>
#include <string>

#include <nlohmann/json.hpp>
#include <clang/AST/ASTContext.h>
#include <clang/AST/Decl.h>
#include <clang/AST/Stmt.h>

namespace kaskara {

class FunctionDB
{
public:
  FunctionDB();
  ~FunctionDB();

  class Entry {
  public:
    Entry(std::string const &name,
          std::string const &location,
          std::string const &body,
          std::string const &return_type,
          bool const &pure,
          bool const &global);

    std::string const name;
    std::string const location;
    std::string const body;
    std::string const return_type;
    bool const pure;
    bool const global;

    nlohmann::json const to_json() const;
  }; // Entry

  void add(clang::ASTContext *ctx, clang::FunctionDecl const *decl);
  void dump() const;
  nlohmann::json to_json() const;
  void to_file(const std::string &fn) const;

private:
  std::vector<Entry> contents;
}; // FunctionDB

} // kaskara

#endif // H_FUNCTION_DB
