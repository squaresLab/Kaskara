#include "FunctionDB.h"

#include <iostream>

namespace bond {

FunctionDB::FunctionDB() : contents()
{ }

FunctionDB::~FunctionDB()
{ }

FunctionDB::Entry::Entry(std::string const &name,
                         std::string const &location)
  : name(name), location(location)
{ }

void FunctionDB::add(std::string const &name,
                     std::string const &location)
{
  contents.emplace_back(name, location);
}

void FunctionDB::dump() const
{
  for (auto &e : contents) {
    std::cout << "FUNCTION:" << e.name << "\n";
  }
}

} // bond
