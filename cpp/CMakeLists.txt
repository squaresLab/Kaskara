add_executable(kaskara-loop-finder
  LoopDB.cpp
  util.cpp
  loop-finder.cpp)

add_executable(kaskara-function-scanner
  FunctionDB.cpp
  util.cpp
  function-scanner.cpp)

set(KASKARA_LIBS
  fmt
  stdc++fs
  ${LLVM_LIBS}
  ${CLANG_LIBS})

target_link_libraries(kaskara-function-scanner ${KASKARA_LIBS})
target_link_libraries(kaskara-loop-finder ${KASKARA_LIBS})
