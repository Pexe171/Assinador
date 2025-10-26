set(SOURCES
    main.cpp
    ui/main_window.cpp
    ui/cadastro_form.cpp
    ui/consulta_widget.cpp
    data/database_manager.cpp
    data/cadastro_repository.cpp
    integration/outlook_automation.cpp
)

set(HEADERS
    ui/main_window.h
    ui/cadastro_form.h
    ui/consulta_widget.h
    data/database_manager.h
    data/cadastro_repository.h
    integration/outlook_automation.h
)

add_executable(assinador
    ${SOURCES}
    ${HEADERS}
)

target_include_directories(assinador
    PUBLIC
        ${CMAKE_SOURCE_DIR}/include
        ${CMAKE_CURRENT_SOURCE_DIR}
)

target_link_libraries(assinador
    PRIVATE
        Qt6::Widgets
        Qt6::Sql
        Qt6::AxContainer
)

target_compile_definitions(assinador
    PRIVATE
        QT_DEPRECATED_WARNINGS
)
