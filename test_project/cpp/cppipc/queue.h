#pragma once

#include <type_traits>
#include <new>
#include <utility>  // [[since C++14]]: std::exchange
#include <algorithm>
#include <atomic>
#include <tuple>
#include <thread>
#include <chrono>
#include <string>
#include <cassert>  // assert

#include "libipc/def.h"
#include "libipc/shm.h"
#include "libipc/rw_lock.h"

#include "libipc/utility/log.h"
#include "libipc/platform/detail.h"
#include "libipc/circ/elem_def.h"

namespace ipc {
namespace detail {

class queue_conn {
protected:
    circ::cc_t connected_ = 0;
    shm::handle elems_h_;

    template <typename Elems>
    Elems* open(char const * name) {
        if (name == nullptr || name[0] == '\0') {
            ipc::error("fail open waiter: name is empty!\n");
            return nullptr;
        }
        if (!elems_h_.acquire(name, sizeof(Elems))) {
            return nullptr;
        }
        auto elems = static_cast<Elems*>(elems_h_.get());
        if (elems == nullptr) {
            ipc::error("fail acquire elems: %s\n", name);
            return nullptr;
        }
        elems->init();
        return elems;
    }

    void close() {
        elems_h_.release();
    }

public:
    queue_conn() = default;
    queue_conn(const queue_conn&) = delete;
    queue_conn& operator=(const queue_conn&) = delete;

    bool connected() const noexcept {
        return connected_ != 0;
    }

    circ::cc_t connected_id() const noexcept {
        return connected_;
    }

    template <typename Elems>
    auto connect(Elems* elems) noexcept
                         /*needs 'optional' here*/
     -> std::tuple<bool, bool, decltype(std::declval<Elems>().cursor())> {
        if (elems == nullptr) return {};
        // if it's already connected, just return
        if (connected()) return {connected(), false, 0};
        connected_ = elems->connect_receiver();
        return {connected(), true, elems->cursor()};
    }

    template <typename Elems>
    bool disconnect(Elems* elems) noexcept {
        if (elems == nullptr) return false;
        // if it's already disconnected, just return false
        if (!connected()) return false;
        elems->disconnect_receiver(std::exchange(connected_, 0));
        return true;
    }
};

template <typename Elems>
class queue_base : public queue_conn {
    using base_t = queue_conn;

public:
    using elems_t  = Elems;
    using policy_t = typename elems_t::policy_t;

protected:
    elems_t * elems_ = nullptr;
    decltype(std::declval<elems_t>().cursor()) cursor_ = 0;
    bool sender_flag_ = false;

public:
    using base_t::base_t;

    queue_base() = default;

    explicit queue_base(char const * name)
        : queue_base{} {
        elems_ = open<elems_t>(name);
    }

    explicit queue_base(elems_t * elems) noexcept
        : queue_base{} {
        assert(elems != nullptr);
        elems_ = elems;
    }

    /* not virtual */ ~queue_base() {
        base_t::close();
    }

    elems_t       * elems()       noexcept { return elems_; }
    elems_t const * elems() const noexcept { return elems_; }

    bool ready_sending() noexcept {
        if (elems_ == nullptr) return false;
        return sender_flag_ || (sender_flag_ = elems_->connect_sender());
    }

    void shut_sending() noexcept {
        if (elems_ == nullptr) return;
        if (!sender_flag_) return;
        elems_->disconnect_sender();
    }

    bool connect() noexcept {
        auto tp = base_t::connect(elems_);
        if (std::get<0>(tp) && std::get<1>(tp)) {
            cursor_ = std::get<2>(tp);
            return true;
        }
        return std::get<0>(tp);
    }

    bool disconnect() noexcept {
        return base_t::disconnect(elems_);
    }

    std::size_t conn_count() const noexcept {
        return (elems_ == nullptr) ? static_cast<std::size_t>(invalid_value) : elems_->conn_count();
    }

    bool valid() const noexcept {
        return elems_ != nullptr;
    }

    bool empty() const noexcept {
        return !valid() || (cursor_ == elems_->cursor());
    }

    template <typename T, typename F, typename... P>
    bool push(F&& prep, P&&... params) {
        if (elems_ == nullptr) return false;
        return elems_->push(this, [&](void* p) {
            if (prep(p)) ::new (p) T(std::forward<P>(params)...);
        });
    }

    template <typename T, typename F, typename... P>
    bool force_push(F&& prep, P&&... params) {
        if (elems_ == nullptr) return false;
        return elems_->force_push(this, [&](void* p) {
            if (prep(p)) ::new (p) T(std::forward<P>(params)...);
        });
    }

    template <typename T, typename F>
    bool pop(T& item, F&& out) {
        if (elems_ == nullptr) {
            return false;
        }
        return elems_->pop(this, &(this->cursor_), [&item](void* p) {
            ::new (&item) T(std::move(*static_cast<T*>(p)));
        }, std::forward<F>(out));
    }
};

} // namespace detail

template <typename T, typename Policy>
class queue final : public detail::queue_base<typename Policy::template elems_t<sizeof(T), alignof(T)>> {
    using base_t = detail::queue_base<typename Policy::template elems_t<sizeof(T), alignof(T)>>;

public:
    using value_t = T;

    using base_t::base_t;

    template <typename... P>
    bool push(P&&... params) {
        return base_t::template push<T>(std::forward<P>(params)...);
    }

    template <typename... P>
    bool force_push(P&&... params) {
        return base_t::template force_push<T>(std::forward<P>(params)...);
    }

    bool pop(T& item) {
        return base_t::pop(item, [](bool) {});
    }

    template <typename F>
    bool pop(T& item, F&& out) {
        return base_t::pop(item, std::forward<F>(out));
    }
};

} // namespace ipc
