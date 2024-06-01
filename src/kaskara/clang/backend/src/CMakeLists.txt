add_executable(kaskara-loop-finder
  LoopDB.cpp
  util.cpp
  loop-finder.cpp)

add_executable(kaskara-statement-finder
  SyntaxScopeAnalyzer.cpp
  ReadWriteAnalyzer.cpp
  StatementDB.cpp
  util.cpp
  statement-finder.cpp)

add_executable(kaskara-function-scanner
  FunctionDB.cpp
  util.cpp
  function-scanner.cpp)

add_executable(kaskara-snippet-extractor
  ReadWriteAnalyzer.cpp
  SnippetDB.cpp
  util.cpp
  snippet-extractor.cpp)

add_executable(kaskara-insertion-point-finder
  InsertionPointDB.cpp
  util.cpp
  insertion-point-finder.cpp)

set_target_properties(kaskara-loop-finder
  PROPERTIES
    CXX_STANDARD 17
    CMAKE_CXX_STANDARD_REQUIRED ON
)

if(KASKARA_BUILD_STATIC)
  set_target_properties(kaskara-loop-finder
    PROPERTIES
      LINK_SEARCH_START_STATIC ON
      LINK_SEARCH_END_STATIC ON
  )
endif()

set(KASKARA_LIBS
  ${LLVM_LIBS}
  ${CLANG_LIBS}
)

target_link_libraries(kaskara-function-scanner PRIVATE ${KASKARA_LIBS} fmt::fmt-header-only)
target_link_libraries(kaskara-loop-finder PRIVATE ${KASKARA_LIBS} fmt::fmt-header-only)
target_link_libraries(kaskara-statement-finder PRIVATE ${KASKARA_LIBS} fmt::fmt-header-only)
target_link_libraries(kaskara-snippet-extractor PRIVATE ${KASKARA_LIBS} fmt::fmt-header-only)
target_link_libraries(kaskara-insertion-point-finder PRIVATE ${KASKARA_LIBS} fmt::fmt-header-only)
