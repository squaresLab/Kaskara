cmake_minimum_required(VERSION 2.8)
include(CheckLibraryExists)
include(CheckIncludeFiles)
include(GNUInstallDirs)

project(kaskara CXX)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O0 -ggdb")
set(BUILD_SHARED_LIBRARIES OFF)
set(CMAKE_EXE_LINKER_FLAGS "-static-libstdc++")

#set(CMAKE_C_COMPILER "/usr/local/bin/clang")
#set(CMAKE_CXX_COMPILER "/usr/local/bin/clang++")

#set(CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/cmake)

find_package(LLVM REQUIRED)
find_package(LLVM REQUIRED CONFIG)
include_directories(${LLVM_INCLUDE_DIR})
link_directories(${LLVM_LIB_DIR})
set(LLVM_LIBS
  LLVMLTO
  LLVMPasses
  LLVMObjCARCOpts
  LLVMMIRParser
  LLVMSymbolize
  LLVMDebugInfoPDB
  LLVMDebugInfoDWARF
  LLVMCoverage
  LLVMTableGen
  LLVMOrcJIT
  LLVMXCoreDisassembler
  LLVMXCoreCodeGen
  LLVMXCoreDesc
  LLVMXCoreInfo
  LLVMXCoreAsmPrinter
  LLVMSystemZDisassembler
  LLVMSystemZCodeGen
  LLVMSystemZAsmParser
  LLVMSystemZDesc
  LLVMSystemZInfo
  LLVMSystemZAsmPrinter
  LLVMSparcDisassembler
  LLVMSparcCodeGen
  LLVMSparcAsmParser
  LLVMSparcDesc
  LLVMSparcInfo
  LLVMSparcAsmPrinter
  LLVMRISCVDesc
  LLVMRISCVCodeGen
  LLVMRISCVInfo
  LLVMPowerPCDisassembler
  LLVMPowerPCCodeGen
  LLVMPowerPCAsmParser
  LLVMPowerPCDesc
  LLVMPowerPCInfo
  LLVMPowerPCAsmPrinter
  LLVMNVPTXCodeGen
  LLVMNVPTXDesc
  LLVMNVPTXInfo
  LLVMNVPTXAsmPrinter
  LLVMMSP430CodeGen
  LLVMMSP430Desc
  LLVMMSP430Info
  LLVMMSP430AsmPrinter
  LLVMMipsDisassembler
  LLVMMipsCodeGen
  LLVMMipsAsmParser
  LLVMMipsDesc
  LLVMMipsInfo
  LLVMMipsAsmPrinter
  LLVMLanaiDisassembler
  LLVMLanaiCodeGen
  LLVMLanaiAsmParser
  LLVMLanaiDesc
  LLVMLanaiAsmPrinter
  LLVMLanaiInfo
  LLVMHexagonDisassembler
  LLVMHexagonCodeGen
  LLVMHexagonAsmParser
  LLVMHexagonDesc
  LLVMHexagonInfo
  LLVMBPFDisassembler
  LLVMBPFCodeGen
  LLVMBPFDesc
  LLVMBPFInfo
  LLVMBPFAsmPrinter
  LLVMARMDisassembler
  LLVMARMCodeGen
  LLVMARMAsmParser
  LLVMARMDesc
  LLVMARMInfo
  LLVMARMAsmPrinter
  LLVMAMDGPUDisassembler
  LLVMAMDGPUCodeGen
  LLVMAMDGPUAsmParser
  LLVMAMDGPUDesc
  LLVMAMDGPUInfo
  LLVMAMDGPUAsmPrinter
  LLVMAMDGPUUtils
  LLVMAArch64Disassembler
  LLVMAArch64CodeGen
  LLVMAArch64AsmParser
  LLVMAArch64Desc
  LLVMAArch64Info
  LLVMAArch64AsmPrinter
  LLVMAArch64Utils
  LLVMObjectYAML
  LLVMLibDriver
  LLVMOption
  LLVMX86Disassembler
  LLVMX86AsmParser
  LLVMX86CodeGen
  LLVMGlobalISel
  LLVMSelectionDAG
  LLVMAsmPrinter
  LLVMDebugInfoCodeView
  LLVMDebugInfoMSF
  LLVMX86Desc
  LLVMMCDisassembler
  LLVMX86Info
  LLVMX86AsmPrinter
  LLVMX86Utils
  LLVMMCJIT
  LLVMLineEditor
  LLVMInterpreter
  LLVMExecutionEngine
  LLVMRuntimeDyld
  LLVMCodeGen
  LLVMTarget
  LLVMCoroutines
  LLVMipo
  LLVMInstrumentation
  LLVMVectorize
  LLVMScalarOpts
  LLVMLinker
  LLVMIRReader
  LLVMAsmParser
  LLVMInstCombine
  LLVMTransformUtils
  LLVMBitWriter
  LLVMAnalysis
  LLVMObject
  LLVMMCParser
  LLVMMC
  LLVMBitReader
  LLVMProfileData
  LLVMCore
  LLVMSupport
  LLVMDemangle
)
message(STATUS "Found LLVM: ${LLVM_PACKAGE_VERSION}")
message(STATUS "Using LLVMConfig.cmake in: ${LLVM_DIR}")
message(STATUS "Using LLVM libs: ${LLVM_LIBS}")

find_package(Clang REQUIRED)
find_package(Clang REQUIRED clangTooling libClang)
include_directories(${CLANG_INCLUDE_DIRS})
link_directories(${CLANG_LIB_DIR})
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

add_definitions(${CLANG_DEFINITIONS})
add_definitions(${LLVM_DEFINITIONS})
add_definitions(-fno-rtti -std=c++17)

add_subdirectory(src)
