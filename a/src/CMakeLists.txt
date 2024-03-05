add_library(a a.cpp ../include/a/a.hpp)

target_include_directories(a PUBLIC ../include)
target_include_directories(a PUBLIC ${fmt_INCLUDE_DIR} ${boost_INCLUDE_DIR})


target_link_libraries(a PUBLIC fmt::fmt boost::boost)
