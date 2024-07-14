#include "StatementDB.h"

#include <iostream>
#include <fstream>
#include <sstream>

#include <clang/AST/ASTTypeTraits.h>
#include <clang/AST/PrettyPrinter.h>
#include <clang/Analysis/CFGStmtMap.h>
#include <llvm/Support/raw_ostream.h>

#include "../util.h"
#include "../common/ReadWriteAnalyzer.h"

using json = nlohmann::json;
using namespace kaskara;

namespace kaskara {

StatementDB::StatementDB() : contents()
{ }

StatementDB::~StatementDB()
{ }

StatementDB::Entry::Entry(
  std::string const &location,
  std::string const &content,
  std::string const &canonical,
  std::string const &kind,
  std::unordered_set<std::string> const &reads,
  std::unordered_set<std::string> const &writes,
  std::unordered_set<std::string> const &decls,
  std::unordered_set<std::string> const &visible,
  std::unordered_set<std::string> const &live_before,
  std::unordered_set<std::string> const &live_after,
  StatementSyntaxScope const &syntax_scope
)
  : location(location),
    content(content),
    canonical(canonical),
    kind(kind),
    writes(writes),
    reads(reads),
    decls(decls),
    visible(visible),
    live_before(live_before),
    live_after(live_after),
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

  json j_live_after = json::array();
  for (auto v : live_after)
    j_live_after.push_back(v);

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
    {"live_after", j_live_after},
    {"requires_syntax", j_syntax_required},
  };

  return j;
}

void StatementDB::add(clang::ASTContext const *ctx,
                      clang::Stmt const *stmt,
                      std::unordered_set<clang::NamedDecl const *> const &visible,
                      clang::LiveVariables *liveness,
                      clang::AnalysisDeclContext *analysis_decl_ctx)
{
  // llvm::outs() << "DEBUG: StatementDatabase: adding statement...\n";

  if (analysis_decl_ctx == nullptr) {
    llvm::errs() << "WARNING: not adding statement to database (no analysis decl context)\n";
    return;
  }

  clang::SourceRange source_range = stmt_to_range(*ctx, stmt);
  std::string loc_str = build_loc_str(source_range, ctx);
  // llvm::outs() << "DEBUG: obtained statement location: " << loc_str << "\n";
  if (source_range.isInvalid() || source_range.getEnd() < source_range.getBegin()) {
    llvm::outs() << "WARNING: skipping statement with invalid location: " << loc_str << "\n";
    return;
  }

  std::string txt = read_source(*ctx, source_range);
  // llvm::outs() << "DEBUG: obtained source for statement: " << txt << "\n";

  auto *stmtMap = analysis_decl_ctx->getCFGStmtMap();
  if (stmtMap == nullptr) {
    llvm::outs() << "WARNING: failed to obtain stmt map -- skipping statement\n";
    return;
  }
  // llvm::outs() << "DEBUG: fetched stmt map\n";

  // compute read and write information
  std::unordered_set<std::string> reads;
  std::unordered_set<std::string> writes;
  std::unordered_set<std::string> decls;
  // llvm::outs() << "DEBUG: computing read-write information...\n";
  ReadWriteAnalyzer::analyze(ctx, stmt, reads, writes, decls);
  // llvm::outs() << "DEBUG: computed read-write information\n";

  // compute the names of all visible variables
  std::unordered_set<std::string> visible_names;
  for (auto decl : visible) {
    visible_names.emplace(decl->getNameAsString());
  }

  // compute liveness information
  // FIXME LiveVariables seems to ignore properties, therefore we assume that
  //  all properties are live (for now).
  // llvm::outs() << "DEBUG: computing liveness information...\n";
  std::unordered_set<std::string> live_before;
  for (auto decl : visible) {
    // llvm::outs() << "DEBUG: checking decl...\n";
    if (auto *vd = clang::dyn_cast<clang::VarDecl>(decl)) {
      // llvm::outs() << "DEBUG: checking decl liveness...\n";
      if (!liveness->isLive(stmt, vd))
        continue;
      // llvm::outs() << "DEBUG: checked decl liveness\n";
    }
    live_before.emplace(decl->getNameAsString());
  }
  // llvm::outs() << "DEBUG: computed live before\n";

  // find variables that are live after the statement
  clang::CFGBlock const *block = stmtMap->getBlock(stmt);
  // llvm::outs() << "DEBUG: fetched CFG block...\n";
  std::unordered_set<std::string> live_after;
  for (auto decl : visible) {
    if (auto *vd = clang::dyn_cast<clang::VarDecl>(decl)) {
      if (!liveness->isLive(block, vd))
        continue;
    }
    live_after.emplace(decl->getNameAsString());
  }
  // llvm::outs() << "DEBUG: computed liveness information\n";

  // compute syntax scope analysis
  StatementSyntaxScope syntax_scope = SyntaxScopeAnalyzer::analyze(ctx, stmt);

  // compute canonical form
  // llvm::outs() << "DEBUG: computing canonical form...\n";
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
  // llvm::outs() << "DEBUG: computed canonical form\n";

  // determine statement kind
  std::string kind = stmt->getStmtClassName();

  // llvm::outs() << "DEBUG: adding statement info...\n";
  contents.emplace_back(
    loc_str,
    txt,
    canonical,
    kind,
    reads,
    writes,
    decls,
    visible_names,
    live_before,
    live_after,
    syntax_scope);
  // llvm::outs() << "DEBUG: added statement info\n";
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
