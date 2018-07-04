#include "SnippetDB.h"

#include <iostream>
#include <fstream>

#include "util.h"

using json = nlohmann::json;
using namespace kaskara;

namespace kaskara {

SnippetDB::SnippetDB() : contents()
{ }

SnippetDB::~SnippetDB()
{ }

SnippetDB::Entry::Entry(std::string const &kind,
                        std::string const &contents)
  : kind(kind),
    contents(contents)
{ }

json const SnippetDB::Entry::to_json() const
{
  json j = {
    {"kind", kind},
    {"contents", contents},
    {"reads", json::array()},
    {"writes", json::array()}
  };
  return j;
}

void SnippetDB::add(std::string const &kind,
                    clang::ASTContext const *ctx,
                    clang::Stmt const *stmt)
{
  std::string txt = stmt_to_source(*ctx, stmt);
  std::string location = build_loc_str(stmt->getSourceRange(), ctx);
  contents.emplace_back(kind, txt);
}

json SnippetDB::to_json() const
{
  json j = json::array();
  for (auto &e : contents)
    j.push_back(e.to_json());
  return j;
}

void SnippetDB::dump() const
{
  std::cout << std::setw(2) << to_json() << std::endl;
}

void SnippetDB::to_file(const std::string &fn) const
{
  std::ofstream o(fn);
  o << std::setw(2) << to_json() << std::endl;
}

} // kaskara
