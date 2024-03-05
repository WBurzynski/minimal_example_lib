#pragma once

#include "fmt/format.h"
#include "a/a.hpp"

namespace c
{
    enum class book
    {
        dune, sum_of_all_fears, dracula
    };
    auto format_as(book b) { return fmt::underlying(b); }
    void foo(a::film f);
}
