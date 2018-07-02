#include "LoopDB.h"

#include <iostream>

#include "util.h"

using json = nlohmann::json;
using namespace bond;

namespace bond {

LoopDB::LoopDB() : contents()
{ }

LoopDB::~LoopDB()
{ }

LoopDB::Entry::Entry(std::string const &kind,
                     std::string const &location,
                     std::string const &body)
  : kind(kind), location(location), body(body)
{ }

json const LoopDB::Entry::to_json() const
{
  json j = {
    {"kind", kind},
    {"location", location},
    {"body", body}
  };
  return j;
}

void LoopDB::add(clang::ASTContext *ctx, clang::WhileStmt const *stmt)
{
  std::string location = build_loc_str(stmt->getSourceRange(), ctx);
  std::string body = build_loc_str(stmt->getBody()->getSourceRange(), ctx);
  contents.emplace_back("while", location, body);
}

void LoopDB::add(clang::ASTContext *ctx, clang::ForStmt const *stmt)
{
  std::string location = build_loc_str(stmt->getSourceRange(), ctx);
  std::string body = build_loc_str(stmt->getBody()->getSourceRange(), ctx);
  contents.emplace_back("for", location, body);
}

/*
void LoopDB::add(clang::ASTContext *ctx, clang::CXXForRangeStmt const *stmt)
{
  clang::SourceRange source_range(stmt->getLocStart(), stmt->getLocEnd());
  std::string location = build_loc_str(source_range, ctx);
  std::string body = build_loc_str(stmt->getBody()->getSourceRange(), ctx);
  contents.emplace_back("for-range", location, body);
}
*/

void LoopDB::dump() const
{
  json j = json::array();
  for (auto &e : contents) {
    j.push_back(e.to_json());
  }
  std::cout << std::setw(2) << j << std::endl;
}

} // bond
