add_executable(kaskara-clang
  Kaskara.cpp
  common/ReadWriteAnalyzer.cpp
  common/SyntaxScopeAnalyzer.cpp
  functions/FunctionDB.cpp
  functions/FunctionIndexer.cpp
  insertions/InsertionPointDB.cpp
  insertions/InsertionsIndexer.cpp
  loops/LoopDB.cpp
  loops/LoopIndexer.cpp
  snippets/SnippetDB.cpp
  snippets/SnippetIndexer.cpp
  statements/StatementDB.cpp
  statements/StatementIndexer.cpp
  util.cpp
)

set_target_properties(kaskara-clang
  PROPERTIES
    CXX_STANDARD 17
    CMAKE_CXX_STANDARD_REQUIRED ON
)

if(KASKARA_BUILD_STATIC)
  set_target_properties(kaskara-clang
    PROPERTIES
      LINK_SEARCH_START_STATIC ON
      LINK_SEARCH_END_STATIC ON
  )
  target_link_options(kaskara-clang
    PRIVATE
      -static-libstdc++ -static
  )
endif()

target_link_libraries(kaskara-clang
  PRIVATE
    ${LLVM_LIBS} ${CLANG_LIBS} fmt::fmt-header-only
)

target_include_directories(kaskara-clang
  PUBLIC
    ${CLANG_INCLUDE_DIRS}
    ${LLVM_INCLUDE_DIRS}
    nlohmann_json::nlohmann_json
    fmt::fmt
)

target_compile_definitions(kaskara-clang
  PUBLIC ${CLANG_DEFINITIONS}
)

target_compile_options(kaskara-clang PRIVATE -O0 -ggdb)

install(
  TARGETS kaskara-clang
  DESTINATION "${CMAKE_INSTALL_BINDIR}"
)

# TODO https://cmake.org/cmake/help/latest/command/install.html#runtime-dependency-set
# TODO https://cmake.org/cmake/help/latest/command/file.html#get-runtime-dependencies
# TODO https://discourse.cmake.org/t/copying-dependent-dlls-to-executable-directory/852/4
install(CODE [[
  include(GNUInstallDirs)
  message(STATUS "Copying runtime dependencies...")

  file(GET_RUNTIME_DEPENDENCIES
    RESOLVED_DEPENDENCIES_VAR resolved_deps
    UNRESOLVED_DEPENDENCIES_VAR unresolved_deps
    EXECUTABLES $<TARGET_FILE:kaskara-clang>
  )

  foreach(dep IN LISTS resolved_deps)
    message(STATUS "Copying runtime dependency: ${dep}")
    get_filename_component(dep_name "${dep}" NAME)
    get_filename_component(dep_ext "${dep_name}" EXT)

    if("${dep_ext}" STREQUAL ".so" OR "${dep_ext}" STREQUAL ".dylib" OR "${dep_ext}" MATCHES "^\\.so\\.[0-9]+$")
      set(dep_dest "${CMAKE_INSTALL_LIBDIR}")
    elseif("${dep_ext}" STREQUAL ".dll")
      set(dep_dest "${CMAKE_INSTALL_BINDIR}")
    else()
      set(dep_dest "${CMAKE_INSTALL_BINDIR}")
    endif()

    file(INSTALL
      DESTINATION "${dep_dest}"
      TYPE FILE
      FILES "${dep}"
    )
    message(STATUS "Copied runtime dependency [${dep_name}] to ${dep_dest}")
  endforeach()

  if(unresolved_deps)
    message(WARNING "Unresolved dependencies: ${unresolved_deps}")
  endif()
]])
