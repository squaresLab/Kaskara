#include "StatementDB.h"

#include <iostream>
#include <fstream>

#include "util.h"
#include "ReadWriteAnalyzer.h"

using json = nlohmann::json;
using namespace kaskara;

namespace kaskara {

StatementDB::StatementDB() : contents()
{ }

StatementDB::~StatementDB()
{ }

StatementDB::Entry::Entry(std::string const &location,
                          std::string const &content,
                          std::unordered_set<std::string> const &reads,
                          std::unordered_set<std::string> const &writes,
                          std::unordered_set<std::string> const &decls,
                          std::unordered_set<std::string> const &visible)
  : location(location),
    content(content),
    writes(writes),
    reads(reads),
    decls(decls),
    visible(visible)
{ }

json const StatementDB::Entry::to_json() const
{
  json j_reads = json::array();
  for (auto v : reads)
    j_reads.push_back(v);

  json j_writes = json::array();
  for (auto v : writes)
    j_writes.push_back(v);

  json j_visible = json::array();
  for (auto v : visible)
    j_visible.push_back(v);

  json j_decls = json::array();
  for (auto v : decls)
    j_decls.push_back(v);

  json j = {
    {"location", location},
    {"content", content},
    {"reads", j_reads},
    {"writes", j_writes},
    {"visible", j_visible},
    {"decls", j_decls}
  };
  return j;
}

void StatementDB::add(clang::ASTContext const *ctx,
                      clang::Stmt const *stmt,
                      std::unordered_set<std::string> const &visible,
                      clang::LiveVariables const *liveness)
{
  clang::SourceRange source_range = stmt_to_range(*ctx, stmt);
  std::string loc_str = build_loc_str(source_range, ctx);
  std::string txt = read_source(*ctx, source_range);

  // compute read and write information
  std::unordered_set<std::string> reads;
  std::unordered_set<std::string> writes;
  std::unordered_set<std::string> decls;
  ReadWriteAnalyzer::analyze(ctx, stmt, reads, writes, decls);

  contents.emplace_back(loc_str, txt, reads, writes, decls, visible);
}

json StatementDB::to_json() const
{
  json j = json::array();
  for (auto &e : contents)
    j.push_back(e.to_json());
  return j;
}

void StatementDB::dump() const
{
  std::cout << std::setw(2) << to_json() << std::endl;
}

void StatementDB::to_file(const std::string &fn) const
{
  std::ofstream o(fn);
  o << std::setw(2) << to_json() << std::endl;
}

} // kaskara
