set(BOND_SOURCES
  util.cpp
  FunctionDB.cpp
  LoopDB.cpp
  main.cpp
)

add_executable(bond ${BOND_SOURCES})

target_link_libraries(bond
  fmt
  stdc++fs
  ${LLVM_LIBS}
  ${CLANG_LIBS})
