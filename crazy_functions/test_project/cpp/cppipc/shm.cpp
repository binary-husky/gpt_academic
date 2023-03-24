
#include <string>
#include <utility>

#include "libipc/shm.h"

#include "libipc/utility/pimpl.h"
#include "libipc/memory/resource.h"

namespace ipc {
namespace shm {

class handle::handle_ : public pimpl<handle_> {
public:
    shm::id_t id_ = nullptr;
    void*     m_  = nullptr;

    ipc::string n_;
    std::size_t s_ = 0;
};

handle::handle()
    : p_(p_->make()) {
}

handle::handle(char const * name, std::size_t size, unsigned mode)
    : handle() {
    acquire(name, size, mode);
}

handle::handle(handle&& rhs)
    : handle() {
    swap(rhs);
}

handle::~handle() {
    release();
    p_->clear();
}

void handle::swap(handle& rhs) {
    std::swap(p_, rhs.p_);
}

handle& handle::operator=(handle rhs) {
    swap(rhs);
    return *this;
}

bool handle::valid() const noexcept {
    return impl(p_)->m_ != nullptr;
}

std::size_t handle::size() const noexcept {
    return impl(p_)->s_;
}

char const * handle::name() const noexcept {
    return impl(p_)->n_.c_str();
}

std::int32_t handle::ref() const noexcept {
    return shm::get_ref(impl(p_)->id_);
}

void handle::sub_ref() noexcept {
    shm::sub_ref(impl(p_)->id_);
}

bool handle::acquire(char const * name, std::size_t size, unsigned mode) {
    release();
    impl(p_)->id_ = shm::acquire((impl(p_)->n_ = name).c_str(), size, mode);
    impl(p_)->m_  = shm::get_mem(impl(p_)->id_, &(impl(p_)->s_));
    return valid();
}

std::int32_t handle::release() {
    if (impl(p_)->id_ == nullptr) return -1;
    return shm::release(detach());
}

void* handle::get() const {
    return impl(p_)->m_;
}

void handle::attach(id_t id) {
    if (id == nullptr) return;
    release();
    impl(p_)->id_ = id;
    impl(p_)->m_  = shm::get_mem(impl(p_)->id_, &(impl(p_)->s_));
}

id_t handle::detach() {
    auto old = impl(p_)->id_;
    impl(p_)->id_ = nullptr;
    impl(p_)->m_  = nullptr;
    impl(p_)->s_  = 0;
    impl(p_)->n_.clear();
    return old;
}

} // namespace shm
} // namespace ipc
