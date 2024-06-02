#pragma once

#include <vector>
#include <string>
#include <unordered_set>

#include <nlohmann/json.hpp>
#include <clang/AST/ASTContext.h>
#include <clang/AST/Decl.h>
#include <clang/Analysis/Analyses/LiveVariables.h>

#include "../common/SyntaxScopeAnalyzer.h"

namespace kaskara {

class StatementDB
{
public:
  StatementDB();
  ~StatementDB();

  class Entry {
  public:
    Entry(std::string const &location,
          std::string const &content,
          std::string const &canonical,
          std::string const &kind,
          std::unordered_set<std::string> const &reads,
          std::unordered_set<std::string> const &writes,
          std::unordered_set<std::string> const &decls,
          std::unordered_set<std::string> const &visible,
          std::unordered_set<std::string> const &live_before,
          std::unordered_set<std::string> const &live_after,
          StatementSyntaxScope const &syntax_scope);

    std::string location;
    std::string content;
    std::string canonical;
    std::string kind;
    std::unordered_set<std::string> writes;
    std::unordered_set<std::string> reads;
    std::unordered_set<std::string> visible;
    std::unordered_set<std::string> decls;
    std::unordered_set<std::string> live_before;
    std::unordered_set<std::string> live_after;
    StatementSyntaxScope syntax_scope;

    nlohmann::json const to_json() const;
  }; // Entry

  void add(clang::ASTContext const *ctx,
           clang::Stmt const *stmt,
           std::unordered_set<clang::NamedDecl const *> const &visible,
           clang::LiveVariables *liveness,
           clang::AnalysisDeclContext *analysis_decl_ctx);
  void dump() const;
  nlohmann::json to_json() const;
  void to_file(const std::string &fn) const;

private:
  std::vector<Entry> contents;
}; // StatementDB

} // kaskara
