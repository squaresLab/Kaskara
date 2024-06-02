add_executable(kaskara
  Kaskara.cpp
  common/ReadWriteAnalyzer.cpp
  common/SyntaxScopeAnalyzer.cpp
  functions/FunctionDB.cpp
  functions/FunctionIndexer.cpp
  insertions/InsertionPointDB.cpp
  insertions/InsertionsIndexer.cpp
  loops/LoopDB.cpp
  loops/LoopIndexer.cpp
  snippets/SnippetDB.cpp
  snippets/SnippetIndexer.cpp
  statements/StatementDB.cpp
  statements/StatementIndexer.cpp
  util.cpp
)

set_target_properties(kaskara
  PROPERTIES
    CXX_STANDARD 17
    CMAKE_CXX_STANDARD_REQUIRED ON
)

if(KASKARA_BUILD_STATIC)
  set_target_properties(kaskara
    PROPERTIES
      LINK_SEARCH_START_STATIC ON
      LINK_SEARCH_END_STATIC ON
  )
endif()

target_link_libraries(kaskara
  PRIVATE
    ${LLVM_LIBS} ${CLANG_LIBS} fmt::fmt-header-only
)

# TODO add install macro
# TODO https://cmake.org/cmake/help/latest/command/install.html#runtime-dependency-set
# TODO https://cmake.org/cmake/help/latest/command/file.html#get-runtime-dependencies
# TODO https://discourse.cmake.org/t/copying-dependent-dlls-to-executable-directory/852/4
