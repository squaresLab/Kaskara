#ifndef H_LOOP_DB
#define H_LOOP_DB

#include <vector>
#include <string>

#include <nlohmann/json.hpp>

namespace bond {

class LoopDB
{
public:
  LoopDB();
  ~LoopDB();

  class Entry {
  public:
    Entry(std::string const &location);

    std::string const location;

    nlohmann::json const to_json() const;
  }; // Entry

  void add(std::string const &location);
  void dump() const;

private:
  std::vector<Entry> contents;
}; // LoopDB

} // bond

#endif // H_LOOP_DB
