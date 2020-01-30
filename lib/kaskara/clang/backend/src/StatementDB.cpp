#include "StatementDB.h"

#include <iostream>
#include <fstream>
#include <sstream>

#include <clang/AST/ASTTypeTraits.h>
#include <clang/AST/PrettyPrinter.h>
#include <llvm/Support/raw_ostream.h>

#include "util.h"
#include "ReadWriteAnalyzer.h"

using json = nlohmann::json;
using namespace kaskara;
using namespace clang::ast_type_traits;

namespace kaskara {

StatementDB::StatementDB() : contents()
{ }

StatementDB::~StatementDB()
{ }

StatementDB::Entry::Entry(std::string const &location,
                          std::string const &content,
                          std::string const &canonical,
                          std::string const &kind,
                          std::unordered_set<std::string> const &reads,
                          std::unordered_set<std::string> const &writes,
                          std::unordered_set<std::string> const &decls,
                          std::unordered_set<std::string> const &visible,
                          std::unordered_set<std::string> const &live_before,
                          StatementSyntaxScope const &syntax_scope)
  : location(location),
    content(content),
    canonical(canonical),
    kind(kind),
    writes(writes),
    reads(reads),
    decls(decls),
    visible(visible),
    live_before(live_before),
    syntax_scope(syntax_scope)
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

  json j_live_before = json::array();
  for (auto v : live_before)
    j_live_before.push_back(v);

  json j_syntax_required = json::array();
  if (syntax_scope.requires_break)
    j_syntax_required.push_back("break");
  if (syntax_scope.requires_continue)
    j_syntax_required.push_back("continue");

  json j = {
    {"location", location},
    {"content", content},
    {"canonical", canonical},
    {"kind", kind},
    {"reads", j_reads},
    {"writes", j_writes},
    {"visible", j_visible},
    {"decls", j_decls},
    {"live_before", j_live_before},
    {"requires_syntax", j_syntax_required},
  };

  return j;
}

void StatementDB::add(clang::ASTContext const *ctx,
                      clang::Stmt const *stmt,
                      std::unordered_set<clang::NamedDecl const *> const &visible,
                      clang::LiveVariables *liveness)
{
  clang::SourceRange source_range = stmt_to_range(*ctx, stmt);
  std::string loc_str = build_loc_str(source_range, ctx);
  std::string txt = read_source(*ctx, source_range);

  // compute read and write information
  std::unordered_set<std::string> reads;
  std::unordered_set<std::string> writes;
  std::unordered_set<std::string> decls;
  ReadWriteAnalyzer::analyze(ctx, stmt, reads, writes, decls);

  // compute liveness information
  // FIXME LiveVariables seems to ignore properties, therefore we assume that
  //  all properties are live (for now).
  std::unordered_set<std::string> visible_names;
  std::unordered_set<std::string> live_before;
  for (auto decl : visible) {
    std::string name = decl->getNameAsString();
    visible_names.emplace(name);
    if (clang::VarDecl const *vd = DynTypedNode::create(*decl).get<clang::VarDecl>()) {
      if (!liveness->isLive(stmt, vd))
        continue;
    }
    live_before.emplace(name);
  }

  // compute syntax scope analysis
  StatementSyntaxScope syntax_scope = SyntaxScopeAnalyzer::analyze(ctx, stmt);

  // compute canonical form
  std::string canonical;
  llvm::raw_string_ostream ss(canonical);

  // FIXME store this printing policy
  clang::PrintingPolicy pp = clang::PrintingPolicy(clang::LangOptions());
  pp.Indentation = 0;
  pp.IncludeNewlines = 0;
  // pp.SuppressImplicitBase = 1;  // FIXME requires Clang 8
  // pp.FullyQualifiedName = 0;  // FIXME requires Clang 8
  stmt->printPretty(ss, NULL, pp);
  ss.flush();

  // add missing semi-colon to end of canonical form
  char last = canonical.back();
  if (last != '\n' && last != '}' && last != ';')
    canonical.push_back(';');

  // determine statement kind
  std::string kind = stmt->getStmtClassName();

  contents.emplace_back(loc_str, txt, canonical, kind,
                        reads, writes, decls, visible_names, live_before,
                        syntax_scope);
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
