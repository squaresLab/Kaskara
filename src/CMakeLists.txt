add_executable(bond
  main.cpp)

target_link_libraries(bond
  stdc++fs
  ${LLVM_LIBS}
  ${CLANG_LIBS})
