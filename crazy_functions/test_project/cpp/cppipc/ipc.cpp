
#include <type_traits>
#include <cstring>
#include <algorithm>
#include <utility>          // std::pair, std::move, std::forward
#include <atomic>
#include <type_traits>      // aligned_storage_t
#include <string>
#include <vector>
#include <array>
#include <cassert>

#include "libipc/ipc.h"
#include "libipc/def.h"
#include "libipc/shm.h"
#include "libipc/pool_alloc.h"
#include "libipc/queue.h"
#include "libipc/policy.h"
#include "libipc/rw_lock.h"
#include "libipc/waiter.h"

#include "libipc/utility/log.h"
#include "libipc/utility/id_pool.h"
#include "libipc/utility/scope_guard.h"
#include "libipc/utility/utility.h"

#include "libipc/memory/resource.h"
#include "libipc/platform/detail.h"
#include "libipc/circ/elem_array.h"

namespace {

using msg_id_t = std::uint32_t;
using acc_t    = std::atomic<msg_id_t>;

template <std::size_t DataSize, std::size_t AlignSize>
struct msg_t;

template <std::size_t AlignSize>
struct msg_t<0, AlignSize> {
    msg_id_t     cc_id_;
    msg_id_t     id_;
    std::int32_t remain_;
    bool         storage_;
};

template <std::size_t DataSize, std::size_t AlignSize>
struct msg_t : msg_t<0, AlignSize> {
    std::aligned_storage_t<DataSize, AlignSize> data_ {};

    msg_t() = default;
    msg_t(msg_id_t cc_id, msg_id_t id, std::int32_t remain, void const * data, std::size_t size)
        : msg_t<0, AlignSize> {cc_id, id, remain, (data == nullptr) || (size == 0)} {
        if (this->storage_) {
            if (data != nullptr) {
                // copy storage-id
                *reinterpret_cast<ipc::storage_id_t*>(&data_) =
                     *static_cast<ipc::storage_id_t const *>(data);
            }
        }
        else std::memcpy(&data_, data, size);
    }
};

template <typename T>
ipc::buff_t make_cache(T& data, std::size_t size) {
    auto ptr = ipc::mem::alloc(size);
    std::memcpy(ptr, &data, (ipc::detail::min)(sizeof(data), size));
    return { ptr, size, ipc::mem::free };
}

struct cache_t {
    std::size_t fill_;
    ipc::buff_t buff_;

    cache_t(std::size_t f, ipc::buff_t && b)
        : fill_(f), buff_(std::move(b))
    {}

    void append(void const * data, std::size_t size) {
        if (fill_ >= buff_.size() || data == nullptr || size == 0) return;
        auto new_fill = (ipc::detail::min)(fill_ + size, buff_.size());
        std::memcpy(static_cast<ipc::byte_t*>(buff_.data()) + fill_, data, new_fill - fill_);
        fill_ = new_fill;
    }
};

auto cc_acc() {
    static ipc::shm::handle acc_h("__CA_CONN__", sizeof(acc_t));
    return static_cast<acc_t*>(acc_h.get());
}

IPC_CONSTEXPR_ std::size_t align_chunk_size(std::size_t size) noexcept {
    return (((size - 1) / ipc::large_msg_align) + 1) * ipc::large_msg_align;
}

IPC_CONSTEXPR_ std::size_t calc_chunk_size(std::size_t size) noexcept {
    return ipc::make_align(alignof(std::max_align_t), align_chunk_size(
           ipc::make_align(alignof(std::max_align_t), sizeof(std::atomic<ipc::circ::cc_t>)) + size));
}

struct chunk_t {
    std::atomic<ipc::circ::cc_t> &conns() noexcept {
        return *reinterpret_cast<std::atomic<ipc::circ::cc_t> *>(this);
    }

    void *data() noexcept {
        return reinterpret_cast<ipc::byte_t *>(this)
             + ipc::make_align(alignof(std::max_align_t), sizeof(std::atomic<ipc::circ::cc_t>));
    }
};

struct chunk_info_t {
    ipc::id_pool<> pool_;
    ipc::spin_lock lock_;

    IPC_CONSTEXPR_ static std::size_t chunks_mem_size(std::size_t chunk_size) noexcept {
        return ipc::id_pool<>::max_count * chunk_size;
    }

    ipc::byte_t *chunks_mem() noexcept {
        return reinterpret_cast<ipc::byte_t *>(this + 1);
    }

    chunk_t *at(std::size_t chunk_size, ipc::storage_id_t id) noexcept {
        if (id < 0) return nullptr;
        return reinterpret_cast<chunk_t *>(chunks_mem() + (chunk_size * id));
    }
};

auto& chunk_storages() {
    class chunk_handle_t {
        ipc::shm::handle handle_;

    public:
        chunk_info_t *get_info(std::size_t chunk_size) {
            if (!handle_.valid() &&
                !handle_.acquire( ("__CHUNK_INFO__" + ipc::to_string(chunk_size)).c_str(), 
                                  sizeof(chunk_info_t) + chunk_info_t::chunks_mem_size(chunk_size) )) {
                ipc::error("[chunk_storages] chunk_shm.id_info_.acquire failed: chunk_size = %zd\n", chunk_size);
                return nullptr;
            }
            auto info = static_cast<chunk_info_t*>(handle_.get());
            if (info == nullptr) {
                ipc::error("[chunk_storages] chunk_shm.id_info_.get failed: chunk_size = %zd\n", chunk_size);
                return nullptr;
            }
            return info;
        }
    };
    static ipc::map<std::size_t, chunk_handle_t> chunk_hs;
    return chunk_hs;
}

chunk_info_t *chunk_storage_info(std::size_t chunk_size) {
    auto &storages = chunk_storages();
    std::decay_t<decltype(storages)>::iterator it;
    {
        static ipc::rw_lock lock;
        IPC_UNUSED_ std::shared_lock<ipc::rw_lock> guard {lock};
        if ((it = storages.find(chunk_size)) == storages.end()) {
            using chunk_handle_t = std::decay_t<decltype(storages)>::value_type::second_type;
            guard.unlock();
            IPC_UNUSED_ std::lock_guard<ipc::rw_lock> guard {lock};
            it = storages.emplace(chunk_size, chunk_handle_t{}).first;
        }
    }
    return it->second.get_info(chunk_size);
}

std::pair<ipc::storage_id_t, void*> acquire_storage(std::size_t size, ipc::circ::cc_t conns) {
    std::size_t chunk_size = calc_chunk_size(size);
    auto info = chunk_storage_info(chunk_size);
    if (info == nullptr) return {};

    info->lock_.lock();
    info->pool_.prepare();
    // got an unique id
    auto id = info->pool_.acquire();
    info->lock_.unlock();

    auto chunk = info->at(chunk_size, id);
    if (chunk == nullptr) return {};
    chunk->conns().store(conns, std::memory_order_relaxed);
    return { id, chunk->data() };
}

void *find_storage(ipc::storage_id_t id, std::size_t size) {
    if (id < 0) {
        ipc::error("[find_storage] id is invalid: id = %ld, size = %zd\n", (long)id, size);
        return nullptr;
    }
    std::size_t chunk_size = calc_chunk_size(size);
    auto info = chunk_storage_info(chunk_size);
    if (info == nullptr) return nullptr;
    return info->at(chunk_size, id)->data();
}

void release_storage(ipc::storage_id_t id, std::size_t size) {
    if (id < 0) {
        ipc::error("[release_storage] id is invalid: id = %ld, size = %zd\n", (long)id, size);
        return;
    }
    std::size_t chunk_size = calc_chunk_size(size);
    auto info = chunk_storage_info(chunk_size);
    if (info == nullptr) return;
    info->lock_.lock();
    info->pool_.release(id);
    info->lock_.unlock();
}

template <ipc::relat Rp, ipc::relat Rc>
bool sub_rc(ipc::wr<Rp, Rc, ipc::trans::unicast>, 
            std::atomic<ipc::circ::cc_t> &/*conns*/, ipc::circ::cc_t /*curr_conns*/, ipc::circ::cc_t /*conn_id*/) noexcept {
    return true;
}

template <ipc::relat Rp, ipc::relat Rc>
bool sub_rc(ipc::wr<Rp, Rc, ipc::trans::broadcast>, 
            std::atomic<ipc::circ::cc_t> &conns, ipc::circ::cc_t curr_conns, ipc::circ::cc_t conn_id) noexcept {
    auto last_conns = curr_conns & ~conn_id;
    for (unsigned k = 0;;) {
        auto chunk_conns  = conns.load(std::memory_order_acquire);
        if (conns.compare_exchange_weak(chunk_conns, chunk_conns & last_conns, std::memory_order_release)) {
            return (chunk_conns & last_conns) == 0;
        }
        ipc::yield(k);
    }
}

template <typename Flag>
void recycle_storage(ipc::storage_id_t id, std::size_t size, ipc::circ::cc_t curr_conns, ipc::circ::cc_t conn_id) {
    if (id < 0) {
        ipc::error("[recycle_storage] id is invalid: id = %ld, size = %zd\n", (long)id, size);
        return;
    }
    std::size_t chunk_size = calc_chunk_size(size);
    auto info = chunk_storage_info(chunk_size);
    if (info == nullptr) return;

    auto chunk = info->at(chunk_size, id);
    if (chunk == nullptr) return;

    if (!sub_rc(Flag{}, chunk->conns(), curr_conns, conn_id)) {
        return;
    }
    info->lock_.lock();
    info->pool_.release(id);
    info->lock_.unlock();
}

template <typename MsgT>
bool clear_message(void* p) {
    auto msg = static_cast<MsgT*>(p);
    if (msg->storage_) {
        std::int32_t r_size = static_cast<std::int32_t>(ipc::data_length) + msg->remain_;
        if (r_size <= 0) {
            ipc::error("[clear_message] invalid msg size: %d\n", (int)r_size);
            return true;
        }
        release_storage(
            *reinterpret_cast<ipc::storage_id_t*>(&msg->data_),
            static_cast<std::size_t>(r_size));
    }
    return true;
}

struct conn_info_head {

    ipc::string name_;
    msg_id_t    cc_id_; // connection-info id
    ipc::detail::waiter cc_waiter_, wt_waiter_, rd_waiter_;
    ipc::shm::handle acc_h_;

    conn_info_head(char const * name)
        : name_     {name}
        , cc_id_    {(cc_acc() == nullptr) ? 0 : cc_acc()->fetch_add(1, std::memory_order_relaxed)}
        , cc_waiter_{("__CC_CONN__" + name_).c_str()}
        , wt_waiter_{("__WT_CONN__" + name_).c_str()}
        , rd_waiter_{("__RD_CONN__" + name_).c_str()}
        , acc_h_    {("__AC_CONN__" + name_).c_str(), sizeof(acc_t)} {
    }

    void quit_waiting() {
        cc_waiter_.quit_waiting();
        wt_waiter_.quit_waiting();
        rd_waiter_.quit_waiting();
    }

    auto acc() {
        return static_cast<acc_t*>(acc_h_.get());
    }

    auto& recv_cache() {
        thread_local ipc::unordered_map<msg_id_t, cache_t> tls;
        return tls;
    }
};

template <typename W, typename F>
bool wait_for(W& waiter, F&& pred, std::uint64_t tm) {
    if (tm == 0) return !pred();
    for (unsigned k = 0; pred();) {
        bool ret = true;
        ipc::sleep(k, [&k, &ret, &waiter, &pred, tm] {
            ret = waiter.wait_if(std::forward<F>(pred), tm);
            k   = 0;
        });
        if (!ret) return false; // timeout or fail
        if (k == 0) break; // k has been reset
    }
    return true;
}

template <typename Policy,
          std::size_t DataSize  = ipc::data_length,
          std::size_t AlignSize = (ipc::detail::min)(DataSize, alignof(std::max_align_t))>
struct queue_generator {

    using queue_t = ipc::queue<msg_t<DataSize, AlignSize>, Policy>;

    struct conn_info_t : conn_info_head {
        queue_t que_;

        conn_info_t(char const * name)
            : conn_info_head{name}
            , que_{("__QU_CONN__" +
                    ipc::to_string(DataSize) + "__" +
                    ipc::to_string(AlignSize) + "__" + name).c_str()} {
        }

        void disconnect_receiver() {
            bool dis = que_.disconnect();
            this->quit_waiting();
            if (dis) {
                this->recv_cache().clear();
            }
        }
    };
};

template <typename Policy>
struct detail_impl {

using policy_t    = Policy;
using flag_t      = typename policy_t::flag_t;
using queue_t     = typename queue_generator<policy_t>::queue_t;
using conn_info_t = typename queue_generator<policy_t>::conn_info_t;

constexpr static conn_info_t* info_of(ipc::handle_t h) noexcept {
    return static_cast<conn_info_t*>(h);
}

constexpr static queue_t* queue_of(ipc::handle_t h) noexcept {
    return (info_of(h) == nullptr) ? nullptr : &(info_of(h)->que_);
}

/* API implementations */

static void disconnect(ipc::handle_t h) {
    auto que = queue_of(h);
    if (que == nullptr) {
        return;
    }
    que->shut_sending();
    assert(info_of(h) != nullptr);
    info_of(h)->disconnect_receiver();
}

static bool reconnect(ipc::handle_t * ph, bool start_to_recv) {
    assert(ph != nullptr);
    assert(*ph != nullptr);
    auto que = queue_of(*ph);
    if (que == nullptr) {
        return false;
    }
    if (start_to_recv) {
        que->shut_sending();
        if (que->connect()) { // wouldn't connect twice
            info_of(*ph)->cc_waiter_.broadcast();
            return true;
        }
        return false;
    }
    // start_to_recv == false
    if (que->connected()) {
        info_of(*ph)->disconnect_receiver();
    }
    return que->ready_sending();
}

static bool connect(ipc::handle_t * ph, char const * name, bool start_to_recv) {
    assert(ph != nullptr);
    if (*ph == nullptr) {
        *ph = ipc::mem::alloc<conn_info_t>(name);
    }
    return reconnect(ph, start_to_recv);
}

static void destroy(ipc::handle_t h) {
    disconnect(h);
    ipc::mem::free(info_of(h));
}

static std::size_t recv_count(ipc::handle_t h) noexcept {
    auto que = queue_of(h);
    if (que == nullptr) {
        return ipc::invalid_value;
    }
    return que->conn_count();
}

static bool wait_for_recv(ipc::handle_t h, std::size_t r_count, std::uint64_t tm) {
    auto que = queue_of(h);
    if (que == nullptr) {
        return false;
    }
    return wait_for(info_of(h)->cc_waiter_, [que, r_count] {
        return que->conn_count() < r_count;
    }, tm);
}

template <typename F>
static bool send(F&& gen_push, ipc::handle_t h, void const * data, std::size_t size) {
    if (data == nullptr || size == 0) {
        ipc::error("fail: send(%p, %zd)\n", data, size);
        return false;
    }
    auto que = queue_of(h);
    if (que == nullptr) {
        ipc::error("fail: send, queue_of(h) == nullptr\n");
        return false;
    }
    if (que->elems() == nullptr) {
        ipc::error("fail: send, queue_of(h)->elems() == nullptr\n");
        return false;
    }
    if (!que->ready_sending()) {
        ipc::error("fail: send, que->ready_sending() == false\n");
        return false;
    }
    ipc::circ::cc_t conns = que->elems()->connections(std::memory_order_relaxed);
    if (conns == 0) {
        ipc::error("fail: send, there is no receiver on this connection.\n");
        return false;
    }
    // calc a new message id
    auto acc = info_of(h)->acc();
    if (acc == nullptr) {
        ipc::error("fail: send, info_of(h)->acc() == nullptr\n");
        return false;
    }
    auto msg_id   = acc->fetch_add(1, std::memory_order_relaxed);
    auto try_push = std::forward<F>(gen_push)(info_of(h), que, msg_id);
    if (size > ipc::large_msg_limit) {
        auto   dat = acquire_storage(size, conns);
        void * buf = dat.second;
        if (buf != nullptr) {
            std::memcpy(buf, data, size);
            return try_push(static_cast<std::int32_t>(size) - 
                            static_cast<std::int32_t>(ipc::data_length), &(dat.first), 0);
        }
        // try using message fragment
        //ipc::log("fail: shm::handle for big message. msg_id: %zd, size: %zd\n", msg_id, size);
    }
    // push message fragment
    std::int32_t offset = 0;
    for (std::int32_t i = 0; i < static_cast<std::int32_t>(size / ipc::data_length); ++i, offset += ipc::data_length) {
        if (!try_push(static_cast<std::int32_t>(size) - offset - static_cast<std::int32_t>(ipc::data_length),
                      static_cast<ipc::byte_t const *>(data) + offset, ipc::data_length)) {
            return false;
        }
    }
    // if remain > 0, this is the last message fragment
    std::int32_t remain = static_cast<std::int32_t>(size) - offset;
    if (remain > 0) {
        if (!try_push(remain - static_cast<std::int32_t>(ipc::data_length),
                      static_cast<ipc::byte_t const *>(data) + offset, 
                      static_cast<std::size_t>(remain))) {
            return false;
        }
    }
    return true;
}

static bool send(ipc::handle_t h, void const * data, std::size_t size, std::uint64_t tm) {
    return send([tm](auto info, auto que, auto msg_id) {
        return [tm, info, que, msg_id](std::int32_t remain, void const * data, std::size_t size) {
            if (!wait_for(info->wt_waiter_, [&] {
                    return !que->push(
                        [](void*) { return true; },
                        info->cc_id_, msg_id, remain, data, size);
                }, tm)) {
                ipc::log("force_push: msg_id = %zd, remain = %d, size = %zd\n", msg_id, remain, size);
                if (!que->force_push(
                        clear_message<typename queue_t::value_t>,
                        info->cc_id_, msg_id, remain, data, size)) {
                    return false;
                }
            }
            info->rd_waiter_.broadcast();
            return true;
        };
    }, h, data, size);
}

static bool try_send(ipc::handle_t h, void const * data, std::size_t size, std::uint64_t tm) {
    return send([tm](auto info, auto que, auto msg_id) {
        return [tm, info, que, msg_id](std::int32_t remain, void const * data, std::size_t size) {
            if (!wait_for(info->wt_waiter_, [&] {
                    return !que->push(
                        [](void*) { return true; },
                        info->cc_id_, msg_id, remain, data, size);
                }, tm)) {
                return false;
            }
            info->rd_waiter_.broadcast();
            return true;
        };
    }, h, data, size);
}

static ipc::buff_t recv(ipc::handle_t h, std::uint64_t tm) {
    auto que = queue_of(h);
    if (que == nullptr) {
        ipc::error("fail: recv, queue_of(h) == nullptr\n");
        return {};
    }
    if (!que->connected()) {
        // hasn't connected yet, just return.
        return {};
    }
    auto& rc = info_of(h)->recv_cache();
    for (;;) {
        // pop a new message
        typename queue_t::value_t msg;
        if (!wait_for(info_of(h)->rd_waiter_, [que, &msg] {
                return !que->pop(msg);
            }, tm)) {
            // pop failed, just return.
            return {};
        }
        info_of(h)->wt_waiter_.broadcast();
        if ((info_of(h)->acc() != nullptr) && (msg.cc_id_ == info_of(h)->cc_id_)) {
            continue; // ignore message to self
        }
        // msg.remain_ may minus & abs(msg.remain_) < data_length
        std::int32_t r_size = static_cast<std::int32_t>(ipc::data_length) + msg.remain_;
        if (r_size <= 0) {
            ipc::error("fail: recv, r_size = %d\n", (int)r_size);
            return {};
        }
        std::size_t msg_size = static_cast<std::size_t>(r_size);
        // large message
        if (msg.storage_) {
            ipc::storage_id_t buf_id = *reinterpret_cast<ipc::storage_id_t*>(&msg.data_);
            void* buf = find_storage(buf_id, msg_size);
            if (buf != nullptr) {
                struct recycle_t {
                    ipc::storage_id_t storage_id;
                    ipc::circ::cc_t   curr_conns;
                    ipc::circ::cc_t   conn_id;
                } *r_info = ipc::mem::alloc<recycle_t>(recycle_t{
                    buf_id, que->elems()->connections(std::memory_order_relaxed), que->connected_id()
                });
                if (r_info == nullptr) {
                    ipc::log("fail: ipc::mem::alloc<recycle_t>.\n");
                    return ipc::buff_t{buf, msg_size}; // no recycle
                } else {
                    return ipc::buff_t{buf, msg_size, [](void* p_info, std::size_t size) {
                        auto r_info = static_cast<recycle_t *>(p_info);
                        IPC_UNUSED_ auto finally = ipc::guard([r_info] {
                            ipc::mem::free(r_info);
                        });
                        recycle_storage<flag_t>(r_info->storage_id, size, r_info->curr_conns, r_info->conn_id);
                    }, r_info};
                }
            } else {
                ipc::log("fail: shm::handle for large message. msg_id: %zd, buf_id: %zd, size: %zd\n", msg.id_, buf_id, msg_size);
                continue;
            }
        }
        // find cache with msg.id_
        auto cac_it = rc.find(msg.id_);
        if (cac_it == rc.end()) {
            if (msg_size <= ipc::data_length) {
                return make_cache(msg.data_, msg_size);
            }
            // gc
            if (rc.size() > 1024) {
                std::vector<msg_id_t> need_del;
                for (auto const & pair : rc) {
                    auto cmp = std::minmax(msg.id_, pair.first);
                    if (cmp.second - cmp.first > 8192) {
                        need_del.push_back(pair.first);
                    }
                }
                for (auto id : need_del) rc.erase(id);
            }
            // cache the first message fragment
            rc.emplace(msg.id_, cache_t { ipc::data_length, make_cache(msg.data_, msg_size) });
        }
        // has cached before this message
        else {
            auto& cac = cac_it->second;
            // this is the last message fragment
            if (msg.remain_ <= 0) {
                cac.append(&(msg.data_), msg_size);
                // finish this message, erase it from cache
                auto buff = std::move(cac.buff_);
                rc.erase(cac_it);
                return buff;
            }
            // there are remain datas after this message
            cac.append(&(msg.data_), ipc::data_length);
        }
    }
}

static ipc::buff_t try_recv(ipc::handle_t h) {
    return recv(h, 0);
}

}; // detail_impl<Policy>

template <typename Flag>
using policy_t = ipc::policy::choose<ipc::circ::elem_array, Flag>;

} // internal-linkage

namespace ipc {

template <typename Flag>
ipc::handle_t chan_impl<Flag>::inited() {
    ipc::detail::waiter::init();
    return nullptr;
}

template <typename Flag>
bool chan_impl<Flag>::connect(ipc::handle_t * ph, char const * name, unsigned mode) {
    return detail_impl<policy_t<Flag>>::connect(ph, name, mode & receiver);
}

template <typename Flag>
bool chan_impl<Flag>::reconnect(ipc::handle_t * ph, unsigned mode) {
    return detail_impl<policy_t<Flag>>::reconnect(ph, mode & receiver);
}

template <typename Flag>
void chan_impl<Flag>::disconnect(ipc::handle_t h) {
    detail_impl<policy_t<Flag>>::disconnect(h);
}

template <typename Flag>
void chan_impl<Flag>::destroy(ipc::handle_t h) {
    detail_impl<policy_t<Flag>>::destroy(h);
}

template <typename Flag>
char const * chan_impl<Flag>::name(ipc::handle_t h) {
    auto info = detail_impl<policy_t<Flag>>::info_of(h);
    return (info == nullptr) ? nullptr : info->name_.c_str();
}

template <typename Flag>
std::size_t chan_impl<Flag>::recv_count(ipc::handle_t h) {
    return detail_impl<policy_t<Flag>>::recv_count(h);
}

template <typename Flag>
bool chan_impl<Flag>::wait_for_recv(ipc::handle_t h, std::size_t r_count, std::uint64_t tm) {
    return detail_impl<policy_t<Flag>>::wait_for_recv(h, r_count, tm);
}

template <typename Flag>
bool chan_impl<Flag>::send(ipc::handle_t h, void const * data, std::size_t size, std::uint64_t tm) {
    return detail_impl<policy_t<Flag>>::send(h, data, size, tm);
}

template <typename Flag>
buff_t chan_impl<Flag>::recv(ipc::handle_t h, std::uint64_t tm) {
    return detail_impl<policy_t<Flag>>::recv(h, tm);
}

template <typename Flag>
bool chan_impl<Flag>::try_send(ipc::handle_t h, void const * data, std::size_t size, std::uint64_t tm) {
    return detail_impl<policy_t<Flag>>::try_send(h, data, size, tm);
}

template <typename Flag>
buff_t chan_impl<Flag>::try_recv(ipc::handle_t h) {
    return detail_impl<policy_t<Flag>>::try_recv(h);
}

template struct chan_impl<ipc::wr<relat::single, relat::single, trans::unicast  >>;
// template struct chan_impl<ipc::wr<relat::single, relat::multi , trans::unicast  >>; // TBD
// template struct chan_impl<ipc::wr<relat::multi , relat::multi , trans::unicast  >>; // TBD
template struct chan_impl<ipc::wr<relat::single, relat::multi , trans::broadcast>>;
template struct chan_impl<ipc::wr<relat::multi , relat::multi , trans::broadcast>>;

} // namespace ipc
