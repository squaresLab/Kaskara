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

SnippetDB::Entry::Entry(SnippetDB::Entry const &other)
  : kind(other.kind), contents(other.contents)
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

  Entry snippet = Entry(kind, txt);

  // TODO does this snippet already exist?
  contents.emplace(std::make_pair(txt, snippet));
}

json SnippetDB::to_json() const
{
  json j = json::array();
  for (auto const &item : contents) {
    SnippetDB::Entry const &entry = item.second;
    j.push_back(entry.to_json());
  }
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
