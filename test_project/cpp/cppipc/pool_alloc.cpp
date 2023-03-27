#include "libipc/pool_alloc.h"

#include "libipc/memory/resource.h"

namespace ipc {
namespace mem {

void* pool_alloc::alloc(std::size_t size) {
    return async_pool_alloc::alloc(size);
}

void pool_alloc::free(void* p, std::size_t size) {
    async_pool_alloc::free(p, size);
}

} // namespace mem
} // namespace ipc
