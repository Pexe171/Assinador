set(TEST_SOURCES
    test_database_manager.cpp
)

add_executable(database_manager_tests
    ${TEST_SOURCES}
    ${CMAKE_SOURCE_DIR}/src/data/database_manager.cpp
)

target_include_directories(database_manager_tests
    PRIVATE
        ${CMAKE_SOURCE_DIR}/src
        ${CMAKE_SOURCE_DIR}/include
)

target_link_libraries(database_manager_tests
    PRIVATE
        Qt6::Test
        Qt6::Sql
        Qt6::Core
)

target_compile_definitions(database_manager_tests
    PRIVATE
        QT_DEPRECATED_WARNINGS
)

add_test(
    NAME database_manager_tests
    COMMAND database_manager_tests
)
