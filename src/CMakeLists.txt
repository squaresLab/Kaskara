set(BOND_SOURCES
  util.cpp
  FunctionDB.cpp
  LoopDB.cpp
  main.cpp
)

add_executable(bond ${BOND_SOURCES})

add_executable(bond-loop-finder
  LoopDB.cpp
  util.cpp
  loop-finder.cpp
)

target_link_libraries(bond
  fmt
  stdc++fs
  ${LLVM_LIBS}
  ${CLANG_LIBS})

target_link_libraries(bond-loop-finder
  fmt
  stdc++fs
  ${LLVM_LIBS}
  ${CLANG_LIBS})
