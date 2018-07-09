#include "SnippetDB.h"

#include <iostream>
#include <fstream>

#include <clang/AST/StmtVisitor.h>

#include "util.h"

using json = nlohmann::json;
using namespace kaskara;

namespace kaskara {

/**
 * Computes read and write sets for given statements.
 */
class ReadWriteAnalyzer
  : public clang::ConstStmtVisitor<ReadWriteAnalyzer>
{
public:
  explicit ReadWriteAnalyzer(clang::ASTContext const *ctx,
                             std::unordered_set<std::string> &reads)
    : ctx(ctx), reads(reads)
  { }

  void VisitStmt(clang::Stmt const *stmt)
  {
    for (clang::Stmt const *c : stmt->children()) {
      if (!c) {
        continue;
      }
      Visit(c);
    }
  }

  void VisitCXXDependentScopeMemberExpr(clang::CXXDependentScopeMemberExpr const *expr)
  {
    if (!expr)
      return;

    // std::string name = expr->getMember().getAsString();
    // // only look at this->BLAH
    // llvm::outs() << "MEMBER: " << name << "\n";
  }

  void VisitDeclRefExpr(clang::DeclRefExpr const *expr)
  {
    reads.emplace(expr->getNameInfo().getAsString());
  }

private:
  clang::ASTContext const *ctx;
  std::unordered_set<std::string> &reads;
};

SnippetDB::SnippetDB() : contents()
{ }

SnippetDB::~SnippetDB()
{ }

SnippetDB::Entry::Entry()
  : kind(""), contents(""), locations(), reads()
{ }

SnippetDB::Entry::Entry(std::string const &kind,
                        std::string const &contents,
                        std::unordered_set<std::string> const &reads)
  : kind(kind),
    contents(contents),
    locations(),
    reads(reads)
{ }

SnippetDB::Entry::Entry(SnippetDB::Entry const &other)
  : kind(other.kind),
    contents(other.contents),
    locations(),
    reads(other.reads)
{
  for (std::string const &loc : other.locations) {
    locations.emplace(loc);
  }
}

void SnippetDB::Entry::observe(std::string const &location)
{
  locations.emplace(location);
}

json const SnippetDB::Entry::to_json() const
{
  json j_locations = json::array();
  json j_reads = json::array();
  for (std::string const &loc : locations) {
    j_locations.push_back(loc);
  }
  for (std::string const &v : reads) {
    j_reads.push_back(v);
  }
  json j = {
    {"kind", kind},
    {"contents", contents},
    {"locations", j_locations},
    {"reads", j_reads},
    {"writes", json::array()}
  };
  return j;
}

void SnippetDB::add(std::string const &kind,
                    clang::ASTContext const *ctx,
                    clang::Stmt const *stmt)
{
  clang::SourceRange source_range = stmt_to_range(*ctx, stmt);
  // llvm::outs() << "attempting to read source...\n";
  std::string txt = read_source(*ctx, source_range);
  // llvm::outs() << "successfully read source...\n";
  std::string location = build_loc_str(source_range, ctx);
  // llvm::outs() << "successfully built location string...\n";

  // create an entry if one doesn't already exist
  if (contents.find(txt) == contents.end()) {
    // llvm::outs() << "creating entry for snippet\n";
    std::unordered_set<std::string> reads;
    ReadWriteAnalyzer analyzer = ReadWriteAnalyzer(ctx, reads);
    analyzer.Visit(stmt);
    // llvm::outs() << "computed read-write information\n";
    contents.emplace(std::make_pair(txt, Entry(kind, txt, reads)));
    // llvm::outs() << "record entry\n";
  }

  // record the snippet location
  // llvm::outs() << "observing location\n";
  contents[txt].observe(location);
  // llvm::outs() << "observed location\n";
}

json SnippetDB::to_json() const
{
  json j = json::array();
  for (auto const &item : contents) {
    SnippetDB::Entry const &entry = item.second;
    j.push_back(entry.to_json());
  }
  return j;
}

void SnippetDB::dump() const
{
  std::cout << std::setw(2) << to_json() << std::endl;
}

void SnippetDB::to_file(const std::string &fn) const
{
  std::ofstream o(fn);
  o << std::setw(2) << to_json() << std::endl;
}

} // kaskara
