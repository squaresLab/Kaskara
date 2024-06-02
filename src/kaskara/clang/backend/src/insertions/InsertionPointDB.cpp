#include "InsertionPointDB.h"

#include <iostream>
#include <fstream>

#include "../util.h"

using json = nlohmann::json;

namespace kaskara {

InsertionPointDB::InsertionPointDB() : contents()
{ }

InsertionPointDB::~InsertionPointDB()
{ }

InsertionPointDB::Entry::Entry(std::string const &location,
                               std::unordered_set<std::string> const &visible)
  : location(location),
    visible(visible)
{ }

json const InsertionPointDB::Entry::to_json() const
{
  json j_visible = json::array();
  for (auto &v : visible)
    j_visible.push_back(v);

  json j = {
    {"location", location},
    {"visible", j_visible}
  };
  return j;
}

void InsertionPointDB::add(std::string const &location,
                           std::unordered_set<std::string> const &visible)
{
  contents.emplace_back(location, visible);
}

json InsertionPointDB::to_json() const
{
  json j = json::array();
  for (auto &e : contents)
    j.push_back(e.to_json());
  return j;
}

void InsertionPointDB::dump() const
{
  std::cout << std::setw(2) << to_json() << std::endl;
}

void InsertionPointDB::to_file(const std::string &fn) const
{
  std::ofstream o(fn);
  o << std::setw(2) << to_json() << std::endl;
}

} // kaskara
