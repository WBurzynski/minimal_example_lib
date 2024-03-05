add_library(c c.cpp ../include/c/c.hpp)

target_include_directories(c PUBLIC ../include)

target_link_libraries(c PUBLIC a fmt::fmt)