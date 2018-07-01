#ifndef H_FUNCTION_DB
#define H_FUNCTION_DB

#include <vector>
#include <string>

#include <nlohmann/json.hpp>

namespace bond {

class FunctionDB
{
public:
  FunctionDB();
  ~FunctionDB();

  class Entry {
  public:
    Entry(std::string const &name,
          std::string const &location,
          std::string const &return_type,
          bool const &pure);

    std::string const name;
    std::string const location;
    std::string const return_type;
    bool const pure;

    nlohmann::json const to_json() const;
  }; // Entry

  void add(std::string const &name,
           std::string const &location,
           std::string const &return_type,
           bool const &pure);
  void dump() const;

private:
  std::vector<Entry> contents;
}; // FunctionDB

} // bond

#endif // H_FUNCTION_DB
