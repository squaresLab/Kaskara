add_executable(bond
  main.cpp)

target_link_libraries(bond
  fmt
  stdc++fs
  ${LLVM_LIBS}
  ${CLANG_LIBS})
