add_executable(kaskara-loop-finder
  LoopDB.cpp
  util.cpp
  loop-finder.cpp)

add_executable(kaskara-function-scanner
  FunctionDB.cpp
  util.cpp
  function-scanner.cpp)

add_executable(kaskara-snippet-extractor
  SnippetDB.cpp
  util.cpp
  snippet-extractor.cpp)

add_executable(kaskara-insertion-point-finder
  util.cpp
  insertion-point-finder.cpp)

set(KASKARA_LIBS
  fmt
  stdc++fs
  ${LLVM_LIBS}
  ${CLANG_LIBS})

target_link_libraries(kaskara-function-scanner ${KASKARA_LIBS})
target_link_libraries(kaskara-loop-finder ${KASKARA_LIBS})
target_link_libraries(kaskara-snippet-extractor ${KASKARA_LIBS})
target_link_libraries(kaskara-insertion-point-finder ${KASKARA_LIBS})
