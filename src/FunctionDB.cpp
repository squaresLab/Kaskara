#include "FunctionDB.h"

#include <iostream>

using json = nlohmann::json;

namespace bond {

FunctionDB::FunctionDB() : contents()
{ }

FunctionDB::~FunctionDB()
{ }

FunctionDB::Entry::Entry(std::string const &name,
                         std::string const &location,
                         std::string const &return_type,
                         bool const &pure)
  : name(name),
    location(location),
    return_type(return_type),
    pure(pure)
{ }

json const FunctionDB::Entry::to_json() const
{
  json j = {
    {"name", name},
    {"location", location},
    {"return-type", return_type},
    {"pure", pure}
  };
  return j;
}

void FunctionDB::add(std::string const &name,
                     std::string const &location,
                     std::string const &return_type,
                     bool const &pure)
{
  contents.emplace_back(name, location, return_type, pure);
}

void FunctionDB::dump() const
{
  json j = json::array();
  for (auto &e : contents) {
    j.push_back(e.to_json());
  }
  std::cout << std::setw(2) << j << std::endl;
}

} // bond
