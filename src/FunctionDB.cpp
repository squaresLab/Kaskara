#include "FunctionDB.h"

#include <iostream>

namespace bond {

FunctionDB::FunctionDB() : contents()
{ }

FunctionDB::~FunctionDB()
{ }

FunctionDB::Entry::Entry(std::string const &name,
                         std::string const &location,
                         std::string const &return_type)
  : name(name),
    location(location),
    return_type(return_type)
{ }

void FunctionDB::add(std::string const &name,
                     std::string const &location,
                     std::string const &return_type)
{
  contents.emplace_back(name, location, return_type);
}

void FunctionDB::dump() const
{
  for (auto &e : contents) {
    std::cout << "FUNCTION: " << e.name << " ["
      << e.location
      << "] ("
      << e.return_type
      << ")\n";
  }
}

} // bond
