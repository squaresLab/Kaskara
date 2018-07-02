add_executable(kaskara
  util.cpp
  FunctionDB.cpp
  LoopDB.cpp
  main.cpp
)

add_executable(kaskara-loop-finder
  LoopDB.cpp
  util.cpp
  loop-finder.cpp
)

target_link_libraries(kaskara
  fmt
  stdc++fs
  ${LLVM_LIBS}
  ${CLANG_LIBS})

target_link_libraries(kaskara-loop-finder
  fmt
  stdc++fs
  ${LLVM_LIBS}
  ${CLANG_LIBS})
