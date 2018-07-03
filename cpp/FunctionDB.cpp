#include "FunctionDB.h"

#include <iostream>
#include <fstream>

#include "util.h"

using json = nlohmann::json;

namespace kaskara {

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

void FunctionDB::add(clang::ASTContext *ctx, clang::FunctionDecl const *decl)
{
  std::string name = decl->getNameInfo().getName().getAsString();
  std::string loc_str = build_loc_str(decl->getSourceRange(), ctx);
  std::string return_type = decl->getReturnType().getAsString();
  bool pure = decl->isPure();
  contents.emplace_back(name, loc_str, return_type, pure);
}

json FunctionDB::to_json() const
{
  json j = json::array();
  for (auto &e : contents)
    j.push_back(e.to_json());
  return j;
}

void FunctionDB::dump() const
{
  std::cout << std::setw(2) << to_json() << std::endl;
}

void FunctionDB::to_file(const std::string &fn) const
{
  std::ofstream o(fn);
  o << std::setw(2) << to_json() << std::endl;
}

} // kaskara
