#include <iostream>

#include <llvm/Support/CommandLine.h>

#include <clang/Tooling/CommonOptionsParser.h>
#include <clang/Tooling/Tooling.h>

#include "functions/FunctionIndexer.h"
#include "loops/LoopIndexer.h"
#include "insertions/InsertionsIndexer.h"
#include "snippets/SnippetIndexer.h"
#include "statements/StatementIndexer.h"

using namespace clang::tooling;
using namespace kaskara;
using namespace llvm;

static cl::OptionCategory KaskaraCategory("kaskara options");

static cl::SubCommand FunctionsSubCmd("functions", "indexes all functions in the program");
static cl::SubCommand LoopsSubCmd("loops", "indexes all loops in the program");
static cl::SubCommand InsertionsSubCmd("insertions", "indexes all insertion points in the program");
static cl::SubCommand SnippetsSubCmd("snippets", "extracts all snippets in the program");
static cl::SubCommand StatementsSubCmd("statements", "indexes all statements in the program");

// NOTE: code below is used to add arguments to a specific subcommand
// static cl::opt<std::string> InputFile1(cl::Positional, cl::desc("<input file>"), cl::Required, cl::sub(FunctionsSubCmd));
// static cl::opt<bool> Verbose1("verbose", cl::desc("Enable verbose output"), cl::sub(FunctionsSubCmd));

static cl::extrahelp CommonHelp(CommonOptionsParser::HelpMessage);

int index_functions(
    CommonOptionsParser &optionsParser
) {
    llvm::outs() << "indexing functions...\n";
    auto database = IndexFunctions(optionsParser);
    database->to_file("functions.json");
    return 0;
}

int index_loops(
    CommonOptionsParser &optionsParser
) {
    llvm::outs() << "indexing loops...\n";
    auto database = IndexLoops(optionsParser);
    database->to_file("loops.json");
    return 0;
}

int index_insertions(
    CommonOptionsParser &optionsParser
) {
    llvm::outs() << "indexing insertions...\n";
    auto database = IndexInsertions(optionsParser);
    database->to_file("insertion-points.json");
    return 0;
}

int index_snippets(
    CommonOptionsParser &optionsParser
) {
    llvm::outs() << "indexing snippets...\n";
    auto database = IndexSnippets(optionsParser);
    database->to_file("snippets.json");
    return 0;
}

int index_statements(
    CommonOptionsParser &optionsParser
) {
    llvm::outs() << "indexing statements...\n";
    auto database = IndexStatements(optionsParser);
    database->to_file("statements.json");
    return 0;
}

int main(int argc, const char **argv) {
    auto expectedParser = CommonOptionsParser::create(
        argc,
        argv,
        KaskaraCategory,
        cl::ZeroOrMore
    );
    if (!expectedParser) {
        llvm::errs() << expectedParser.takeError();
        return 1;
    }
    CommonOptionsParser &optionsParser = expectedParser.get();

    if (FunctionsSubCmd) {
        return index_functions(optionsParser);
    } else if (LoopsSubCmd) {
        return index_loops(optionsParser);
    } else if (InsertionsSubCmd) {
        return index_insertions(optionsParser);
    } else if (SnippetsSubCmd) {
        return index_snippets(optionsParser);
    } else if (StatementsSubCmd) {
        return index_statements(optionsParser);
    }

    llvm::errs() << "No subcommand provided\n";
    return 1;
}
