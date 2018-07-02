add_executable(shuriken
  util.cpp
  FunctionDB.cpp
  LoopDB.cpp
  main.cpp
)

add_executable(shuriken-loop-finder
  LoopDB.cpp
  util.cpp
  loop-finder.cpp
)

target_link_libraries(shuriken
  fmt
  stdc++fs
  ${LLVM_LIBS}
  ${CLANG_LIBS})

target_link_libraries(shuriken-loop-finder
  fmt
  stdc++fs
  ${LLVM_LIBS}
  ${CLANG_LIBS})
