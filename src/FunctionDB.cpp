#include "FunctionDB.h"

#include <iostream>

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

void FunctionDB::add(std::string const &name,
                     std::string const &location,
                     std::string const &return_type,
                     bool const &pure)
{
  contents.emplace_back(name, location, return_type, pure);
}

void FunctionDB::dump() const
{
  for (auto &e : contents) {
    std::cout << "FUNCTION: " << e.name << " ["
      << e.location
      << "] ("
      << e.return_type
      << ") "
      << (e.pure ? "[PURE]" : "[UNPURE]")
      << "\n";
  }
}

} // bond
