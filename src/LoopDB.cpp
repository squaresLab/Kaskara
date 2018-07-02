#include "LoopDB.h"

#include <iostream>

using json = nlohmann::json;

namespace bond {

LoopDB::LoopDB() : contents()
{ }

LoopDB::~LoopDB()
{ }

LoopDB::Entry::Entry(std::string const &location)
  : location(location)
{ }

json const LoopDB::Entry::to_json() const
{
  json j = {
    {"location", location},
  };
  return j;
}

void LoopDB::add(std::string const &location)
{
  contents.emplace_back(location);
}

void LoopDB::dump() const
{
  json j = json::array();
  for (auto &e : contents) {
    j.push_back(e.to_json());
  }
  std::cout << std::setw(2) << j << std::endl;
}

} // bond
