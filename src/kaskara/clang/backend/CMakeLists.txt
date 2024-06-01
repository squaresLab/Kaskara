cmake_minimum_required(VERSION 3.24)
include(CheckLibraryExists)
include(CheckIncludeFiles)
include(GNUInstallDirs)

project(kaskara CXX)

option(KASKARA_BUILD_STATIC "builds a static binary" OFF)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O0 -ggdb")

if(KASKARA_BUILD_STATIC)
  set(CMAKE_EXE_LINKER_FLAGS "-static")
  set(BUILD_SHARED_LIBRARIES OFF)
  # set(CMAKE_EXE_LINKER_FLAGS "-static-libstdc++")
endif()

# set(ZLIB_USE_STATIC_LIBS ON)
# find_package(ZLIB REQUIRED)

find_package(LLVM REQUIRED CONFIG)
include_directories(${LLVM_INCLUDE_DIRS})
# add_definitions(${LLVM_DEFINITIONS})
# llvm_map_components_to_libnames(LLVM_LIBRARIES
#   support
#   core
# )
# link_directories(${LLVM_LIB_DIR})
# set(LLVM_LIBS
#   LLVMLTO
#   LLVMPasses
#   LLVMObjCARCOpts
#   LLVMMIRParser
#   LLVMSymbolize
#   LLVMDebugInfoPDB
#   LLVMDebugInfoDWARF
#   LLVMCoverage
#   LLVMTableGen
#   LLVMOrcJIT
#   LLVMXCoreDisassembler
#   LLVMXCoreDesc
#   LLVMXCoreInfo
#   LLVMSystemZDisassembler
#   LLVMSystemZCodeGen
#   LLVMSystemZAsmParser
#   LLVMSystemZDesc
#   LLVMSystemZInfo
#   LLVMSparcDisassembler
#   LLVMSparcCodeGen
#   LLVMSparcAsmParser
#   LLVMSparcDesc
#   LLVMSparcInfo
#   LLVMRISCVDesc
#   LLVMRISCVCodeGen
#   LLVMRISCVInfo
#   LLVMPowerPCDisassembler
#   LLVMPowerPCCodeGen
#   LLVMPowerPCAsmParser
#   LLVMPowerPCDesc
#   LLVMPowerPCInfo
#   LLVMNVPTXCodeGen
#   LLVMNVPTXDesc
#   LLVMNVPTXInfo
#   LLVMMSP430CodeGen
#   LLVMMSP430Desc
#   LLVMMSP430Info
#   LLVMMipsDisassembler
#   LLVMMipsCodeGen
#   LLVMMipsAsmParser
#   LLVMMipsDesc
#   LLVMMipsInfo
#   LLVMLanaiDisassembler
#   LLVMLanaiCodeGen
#   LLVMLanaiAsmParser
#   LLVMLanaiDesc
#   LLVMLanaiInfo
#   LLVMHexagonDisassembler
#   LLVMHexagonCodeGen
#   LLVMHexagonAsmParser
#   LLVMHexagonDesc
#   LLVMHexagonInfo
#   LLVMBPFDisassembler
#   LLVMBPFCodeGen
#   LLVMBPFDesc
#   LLVMBPFInfo
#   LLVMARMDisassembler
#   LLVMARMCodeGen
#   LLVMARMAsmParser
#   LLVMARMDesc
#   LLVMARMInfo
#   LLVMAMDGPUDisassembler
#   LLVMAMDGPUCodeGen
#   LLVMAMDGPUAsmParser
#   LLVMAArch64Disassembler
#   LLVMAArch64CodeGen
#   LLVMAArch64AsmParser
#   LLVMAArch64Desc
#   LLVMAArch64Info
#   LLVMAArch64Utils
#   LLVMObjectYAML
#   LLVMLibDriver
#   LLVMOption
#   LLVMX86Disassembler
#   LLVMX86AsmParser
#   LLVMX86CodeGen
#   LLVMGlobalISel
#   LLVMSelectionDAG
#   LLVMDebugInfoCodeView
#   LLVMDebugInfoMSF
#   LLVMX86Desc
#   LLVMMCDisassembler
#   LLVMX86Info
#   LLVMMCJIT
#   LLVMLineEditor
#   LLVMInterpreter
#   LLVMExecutionEngine
#   LLVMRuntimeDyld
#   LLVMCodeGen
#   LLVMTarget
#   LLVMCoroutines
#   LLVMipo
#   LLVMInstrumentation
#   LLVMVectorize
#   LLVMScalarOpts
#   LLVMLinker
#   LLVMIRReader
#   LLVMAsmParser
#   LLVMInstCombine
#   LLVMTransformUtils
#   LLVMBitWriter
#   LLVMAnalysis
#   LLVMObject
#   LLVMMCParser
#   LLVMMC
#   LLVMBitReader
#   LLVMProfileData
#   LLVMCore
#   LLVMSupport
#   LLVMDemangle
# )
message(STATUS "Found LLVM: ${LLVM_PACKAGE_VERSION}")
message(STATUS "Using LLVMConfig.cmake in: ${LLVM_DIR}")
message(STATUS "Using LLVM libs: ${LLVM_LIBS}")

find_package(Clang REQUIRED CONFIG)
# find_package(Clang REQUIRED clangTooling libClang)
include_directories(${CLANG_INCLUDE_DIRS})
add_definitions(${CLANG_DEFINITIONS})

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

# link_directories(${CLANG_LIB_DIR})

# add_definitions(${CLANG_DEFINITIONS})
# add_definitions(${LLVM_DEFINITIONS})
add_definitions(-fno-rtti -std=c++17)

find_package(fmt)

add_subdirectory(src)
