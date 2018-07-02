#ifndef H_LOOP_DB
#define H_LOOP_DB

#include <vector>
#include <string>

#include <nlohmann/json.hpp>
#include <clang/AST/Stmt.h>
#include <clang/AST/ASTContext.h>

namespace bond {

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

private:
  std::vector<Entry> contents;
}; // LoopDB

} // bond

#endif // H_LOOP_DB
