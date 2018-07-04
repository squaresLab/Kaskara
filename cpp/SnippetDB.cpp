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

SnippetDB::Entry::Entry()
  : kind(""), contents(""), locations()
{ }

SnippetDB::Entry::Entry(std::string const &kind,
                        std::string const &contents)
  : kind(kind),
    contents(contents),
    locations()
{ }

SnippetDB::Entry::Entry(SnippetDB::Entry const &other)
  : kind(other.kind), contents(other.contents), locations()
{
  for (std::string const &loc : other.locations) {
    locations.emplace(loc);
  }
}

void SnippetDB::Entry::observe(std::string const &location)
{
  locations.emplace(location);
}

json const SnippetDB::Entry::to_json() const
{
  json j_locations = json::array();
  for (std::string const &loc : locations) {
    j_locations.push_back(loc);
  }
  json j = {
    {"kind", kind},
    {"contents", contents},
    {"locations", j_locations},
    {"reads", json::array()},
    {"writes", json::array()}
  };
  return j;
}

void SnippetDB::add(std::string const &kind,
                    clang::ASTContext const *ctx,
                    clang::Stmt const *stmt)
{
  clang::SourceRange source_range = stmt_to_range(*ctx, stmt);
  std::string txt = read_source(*ctx, source_range);
  std::string location = build_loc_str(source_range, ctx);

  // create an entry if one doesn't already exist
  if (contents.find(txt) == contents.end()) {
    contents.emplace(std::make_pair(txt, Entry(kind, txt)));
  }

  // record the snippet location
  contents[txt].observe(location);
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
