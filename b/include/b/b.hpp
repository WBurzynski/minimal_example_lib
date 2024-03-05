#pragma once

#include "fmt/format.h"

namespace b
{
    enum class game
    {
        gothic, horizon_zero_dawn, starcraft_2
    };
    auto format_as(game f) { return fmt::underlying(f); }
}
