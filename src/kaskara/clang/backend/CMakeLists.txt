cmake_minimum_required(VERSION 3.24)
include(CheckLibraryExists)
include(CheckIncludeFiles)
include(GNUInstallDirs)

project(kaskara CXX)

option(KASKARA_BUILD_STATIC "builds a static binary" OFF)

find_package(LLVM REQUIRED CONFIG)
message(STATUS "Found LLVM: ${LLVM_PACKAGE_VERSION}")
message(STATUS "Using LLVMConfig.cmake in: ${LLVM_DIR}")

find_package(Clang REQUIRED CONFIG)
set(CLANG_LIBS
  clangAST
  clangASTMatchers
  clangAnalysis
  clangBasic
  clangDriver
  clangEdit
  clangFrontend
  clangFrontendTool
  clangLex
  clangParse
  clangSema
  clangEdit
  clangRewrite
  clangRewriteFrontend
  clangStaticAnalyzerFrontend
  clangStaticAnalyzerCheckers
  clangStaticAnalyzerCore
  clangSerialization
  clangToolingCore
  clangTooling
  clangFormat
)
message(STATUS "Using Clang libs: ${CLANG_LIBS}")

find_package(fmt REQUIRED)

add_subdirectory(src)
