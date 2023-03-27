#pragma once

#include <type_traits>

#include "libipc/def.h"
#include "libipc/prod_cons.h"

#include "libipc/circ/elem_array.h"

namespace ipc {
namespace policy {

template <template <typename, std::size_t...> class Elems, typename Flag>
struct choose;

template <typename Flag>
struct choose<circ::elem_array, Flag> {
    using flag_t = Flag;

    template <std::size_t DataSize, std::size_t AlignSize>
    using elems_t = circ::elem_array<ipc::prod_cons_impl<flag_t>, DataSize, AlignSize>;
};

} // namespace policy
} // namespace ipc
