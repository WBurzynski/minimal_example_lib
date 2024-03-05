#pragma once

#include "fmt/format.h"
#include "boost/container/vector.hpp"

namespace a {
    enum class film {
        house_of_cards, american_beauty, se7en = 7
    };
    auto format_as(film f) { return fmt::underlying(f); }
}

class MyClassHolder
{
public:

    void AddNewObject(const a::film &o);
    const a::film & GetLastObject() const;

private:
    boost::container::vector<a::film> vector_;
};
