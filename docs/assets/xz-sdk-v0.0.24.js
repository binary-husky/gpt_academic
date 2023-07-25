function ownKeys(e, n) {
    var t = Object.keys(e);
    if (Object.getOwnPropertySymbols) {
        var i = Object.getOwnPropertySymbols(e);
        n && (i = i.filter((function (n) {
            return Object.getOwnPropertyDescriptor(e, n).enumerable
        }))), t.push.apply(t, i)
    }
    return t
}

function _objectSpread(e) {
    for (var n = 1; n < arguments.length; n++) {
        var t = null != arguments[n] ? arguments[n] : {};
        n % 2 ? ownKeys(Object(t), !0).forEach((function (n) {
            _defineProperty(e, n, t[n])
        })) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(t)) : ownKeys(Object(t)).forEach((function (n) {
            Object.defineProperty(e, n, Object.getOwnPropertyDescriptor(t, n))
        }))
    }
    return e
}

function _classCallCheck(e, n) {
    if (!(e instanceof n)) throw new TypeError("Cannot call a class as a function")
}

function _defineProperties(e, n) {
    for (var t = 0; t < n.length; t++) {
        var i = n[t];
        i.enumerable = i.enumerable || !1, i.configurable = !0, "value" in i && (i.writable = !0), Object.defineProperty(e, i.key, i)
    }
}

function _createClass(e, n, t) {
    return n && _defineProperties(e.prototype, n), t && _defineProperties(e, t), Object.defineProperty(e, "prototype", {writable: !1}), e
}

function _defineProperty(e, n, t) {
    return n in e ? Object.defineProperty(e, n, {
        value: t,
        enumerable: !0,
        configurable: !0,
        writable: !0
    }) : e[n] = t, e
}

function _typeof(e) {
    return _typeof = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function (e) {
        return typeof e
    } : function (e) {
        return e && "function" == typeof Symbol && e.constructor === Symbol && e !== Symbol.prototype ? "symbol" : typeof e
    }, _typeof(e)
    /*!
     * ksoxz-jssdk - 0.0.24
     * Copyright(c) 2023 Kingsoft Office XieZuo
     */
}

!function (e, n) {
    "object" === ("undefined" == typeof exports ? "undefined" : _typeof(exports)) && "undefined" != typeof module ? module.exports = n() : "function" == typeof define && define.amd ? define(n) : (e = "undefined" != typeof globalThis ? globalThis : e || self).ksoxz_sdk = n()
}(this, (function () {
    "use strict";
    var e = function () {
        function e() {
            _classCallCheck(this, e), _defineProperty(this, "_id", 0), _defineProperty(this, "listeners", {})
        }

        return _createClass(e, [{
            key: "id", get: function () {
                return this._id += 1, this._id
            }
        }, {
            key: "addListener", value: function (e, n) {
                var t = n.options, i = void 0 === t ? {} : t, r = n.onSuccess, o = n.onError;
                this.listeners[e] = {
                    options: i, eventList: [], onSuccess: function (e) {
                        r && r(e)
                    }, onError: function (e) {
                        o && o(e)
                    }
                }
            }
        }, {
            key: "removeListener", value: function (e) {
                delete this.listeners[e]
            }
        }], [{
            key: "getInstance", value: function () {
                return null == this.instance ? this.instance = new e : this.instance
            }
        }]), e
    }();
    _defineProperty(e, "instance", void 0);
    var n, t, i = {uploadFile: "setUploadFileEvent", downloadFile: "setDownloadFileEvent"}, r = "onProgressUpdate";
    !function (e) {
        e.PENDING = "pending", e.SUCCESS = "success"
    }(n || (n = {})), function (e) {
        e.CREATED = "created"
    }(t || (t = {}));
    var o = {params: {}}, s = function () {
        function s() {
            _classCallCheck(this, s), _defineProperty(this, "eventListener", void 0), this.eventListener = e.getInstance()
        }

        return _createClass(s, [{
            key: "getProgressInstance", value: function (e, n) {
                var t = this;
                return {
                    taskId: n, abort: function () {
                        var t = {params: {taskId: n}};
                        window.ksoxz_sdk.core.invokeAbortApi(e, t, n)
                    }, onProgressUpdate: function (o) {
                        var s = {eventName: i[e], payload: {params: {taskId: n, isCallback: !0, event: r}}, taskId: n};
                        t.eventListener.listeners[n].onProgressUpdate = o, t.eventListener.listeners[n].eventList.push(s)
                    }
                }
            }
        }, {
            key: "getInvokeProgressApiParams", value: function (e) {
                var n = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : o,
                    t = arguments.length > 2 ? arguments[2] : void 0,
                    i = t || "".concat(e, "_").concat(this.eventListener.id), r = {
                        methodName: e,
                        callbackName: i,
                        params: _objectSpread(_objectSpread({}, n.params), {}, {taskId: i})
                    }, s = this.getProgressInstance(e, i);
                return t || this.eventListener.addListener(i, n), {invokeParams: r, progressParams: s}
            }
        }, {
            key: "getInvokeApiParams", value: function (e) {
                var n = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : o,
                    t = "".concat(e, "_").concat(this.eventListener.id),
                    i = {methodName: e, callbackName: t, params: n.params || {}};
                return this.eventListener.addListener(t, n), i
            }
        }, {
            key: "handleCallbackEvent", value: function (e) {
                var i = e.callbackName, r = e.status, o = e.params, s = this.eventListener.listeners[i];
                if (r === n.PENDING && o.event) {
                    o.event === t.CREATED ? ((s.eventList || []).forEach((function (e) {
                        var n = e.eventName, t = e.payload;
                        window.ksoxz_sdk.core.invokeApi(n, t)
                    })), s.eventList = []) : s[o.event] && s[o.event](o)
                } else {
                    var a;
                    if (s) if (r === n.SUCCESS ? s.onSuccess(o) : s.onError(o), null !== (a = s.options) && void 0 !== a && a.undeleteCallback) return;
                    this.eventListener.removeListener(i)
                }
            }
        }], [{
            key: "getInstance", value: function () {
                return null == this.instance ? this.instance = new s : this.instance
            }
        }]), s
    }();

    function a(e) {
        return decodeURIComponent(window.atob(e))
    }

    _defineProperty(s, "instance", void 0);
    var c = function () {
        function e() {
            _classCallCheck(this, e), this.initBridge()
        }

        return _createClass(e, [{
            key: "initBridge", value: function () {
                window.addEventListener("message", (function (e) {
                    if (function (e) {
                        if ("string" == typeof e) try {
                            var n = JSON.parse(e);
                            return !("object" !== _typeof(n) || !n)
                        } catch (e) {
                            return !1
                        }
                        return !1
                    }(e.data)) {
                        var n = JSON.parse(e.data);
                        "xz_sdk_callback" === n.eventName && s.getInstance().handleCallbackEvent(n.payload)
                    }
                })), window.WOA_electron && window.WOA_electron.ipcRenderer.on("sdk_callback", (function (e, n) {
                    s.getInstance().handleCallbackEvent(n)
                }))
            }
        }, {
            key: "sendApi", value: function (e) {
                window.woa ? window.woa.invoke(e) : window.WOA_electron && (e.eventName = e.methodName, e.payload = e.params, window.WOA_electron.ipcRenderer.sendToHost("sdk__postMessage", JSON.stringify(e)))
            }
        }, {
            key: "invokeProgressApi", value: function (e) {
                var n = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : o,
                    t = arguments.length > 2 && void 0 !== arguments[2] ? arguments[2] : "",
                    i = s.getInstance().getInvokeProgressApiParams(e, n, t), r = i.invokeParams, a = i.progressParams;
                return this.sendApi(r), a
            }
        }, {
            key: "invokeApi", value: function (e) {
                var n = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : o,
                    t = s.getInstance().getInvokeApiParams(e, n);
                this.sendApi(t)
            }
        }], [{
            key: "getInstance", value: function () {
                return null == this.instance ? this.instance = new e : this.instance
            }
        }]), e
    }();
    _defineProperty(c, "instance", void 0);
    var u = navigator.userAgent, d = (u.includes("xiezuo") || u.includes("WOA")) && window.isWOAClient,
        l = u.includes("android-woa"), p = u.includes("ios-woa"), v = d || l || p, f = function () {
            function e() {
                _classCallCheck(this, e), _defineProperty(this, "version", ""), this.initBridge()
            }

            return _createClass(e, [{
                key: "initBridge", value: function () {
                    var e;
                    l ? window.WOA_Sdk = {
                        callback: function (e) {
                            s.getInstance().handleCallbackEvent(JSON.parse(e))
                        }
                    } : p && (this.version = (e = u.match(/ios-woa\/(\S*)/gm)) ? e[0].split("/")[1] : "", window.WOA_Sdk = {
                        callback: function (e) {
                            s.getInstance().handleCallbackEvent(e)
                        }
                    })
                }
            }, {
                key: "sendApi", value: function (e) {
                    if (l) window.woa.invoke(JSON.stringify(e)); else if (p) {
                        var n = this.version >= "3.12.0" ? "WOA_APPSDK_Invoke" : e.methodName;
                        window.webkit.messageHandlers[n].postMessage(e)
                    }
                }
            }, {
                key: "invokeProgressApi", value: function (e) {
                    var n = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : o,
                        t = arguments.length > 2 && void 0 !== arguments[2] ? arguments[2] : "",
                        i = s.getInstance().getInvokeProgressApiParams(e, n, t), r = i.invokeParams, a = i.progressParams;
                    return this.sendApi(r), a
                }
            }, {
                key: "invokeApi", value: function (e) {
                    var n = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : o,
                        t = s.getInstance().getInvokeApiParams(e, n);
                    this.sendApi(t)
                }
            }], [{
                key: "getInstance", value: function () {
                    return null == this.instance ? this.instance = new e : this.instance
                }
            }]), e
        }();
    _defineProperty(f, "instance", void 0);
    var g = new (function () {
        function n() {
            _classCallCheck(this, n), _defineProperty(this, "bridge", void 0), _defineProperty(this, "apiList", []);
            var e = d ? c : f;
            this.bridge = e.getInstance(), v || console.warn("please use in kso xiezuo client environment")
        }

        return _createClass(n, [{
            key: "initSdk", value: function () {
                var n = this, t = "initSdk", i = {methodName: t, callbackName: t};
                e.getInstance().addListener(t, {
                    onSuccess: function (e) {
                        n.apiList = e.apis
                    }
                }), d && window.woa ? window.woa.invoke(i) : l ? window.woa.initSdk(JSON.stringify(i)) : p && window.webkit.messageHandlers.initSdk.postMessage(i)
            }
        }, {
            key: "ready", value: function (e) {
                return e()
            }
        }]), n
    }()), k = "0.0.24", h = {
        invokeAbortApi: function (e, n, t) {
            return g.bridge.invokeProgressApi("".concat(e, "Abort"), n, t)
        }, invokeApi: function (e, n) {
            return g.bridge.invokeApi(e, n)
        }
    }, b = {params: {count: 9}}, m = Object.freeze({
        __proto__: null, chooseContact: function (e) {
            return g.bridge.invokeApi("chooseContact", e)
        }, createGroupChat: function (e) {
            return g.bridge.invokeApi("createGroupChat", e)
        }, chooseGroupMember: function (e) {
            return g.bridge.invokeApi("chooseGroupMember", e)
        }, shareMessage: function (e) {
            return g.bridge.invokeApi("shareMessage", e)
        }, canIUse: function (e) {
            return g.apiList.includes(e)
        }, config: function (e) {
            var n = e.onSuccess;
            return e.params && (e.params.version = k), e.onSuccess = function () {
                g.initSdk(), n && n()
            }, g.bridge.invokeApi("config", e)
        }, ready: function (e) {
            return g.ready(e)
        }, core: h, setClipboard: function (e) {
            return g.bridge.invokeApi("setClipboard", e)
        }, scan: function (e) {
            var n = e.onSuccess;
            return e.onSuccess = function (t) {
                if (t.text) try {
                    t.text = encodeURIComponent(t.text)
                } catch (n) {
                    console.error("error: ", n), e.onError && e.onError(n)
                }
                n && n(t)
            }, g.bridge.invokeApi("scan", e)
        }, accelerometerWatchShake: function (e) {
            return e.options = {undeleteCallback: !0}, g.bridge.invokeApi("accelerometerWatchShake", e)
        }, accelerometerClearShake: function () {
            return e.getInstance().removeListener("accelerometerWatchShake"), g.bridge.invokeApi("accelerometerClearShake")
        }, setNetworkListener: function (e) {
            return e.options = {undeleteCallback: !0}, e.onSuccess = e.onChange, g.bridge.invokeApi("setNetworkListener", e)
        }, removeNetworkListener: function () {
            return e.getInstance().removeListener("setNetworkListener"), g.bridge.invokeApi("removeNetworkListener")
        }, setScreenShotListener: function (e) {
            return e.options = {undeleteCallback: !0}, e.onSuccess = e.onChange, g.bridge.invokeApi("setScreenShotListener", e)
        }, removeScreenShotListener: function () {
            return e.getInstance().removeListener("setScreenShotListener"), g.bridge.invokeApi("removeScreenShotListener")
        }, setDisplayModeListener: function (e) {
            return e.options = {undeleteCallback: !0}, e.onSuccess = e.onChange, g.bridge.invokeApi("setDisplayModeListener", e)
        }, removeDisplayModeListener: function (n) {
            return e.getInstance().removeListener("setDisplayModeListener"), g.bridge.invokeApi("removeDisplayModeListener", n)
        }, chooseFile: function (e) {
            return g.bridge.invokeApi("chooseFile", e)
        }, previewFile: function (e) {
            return g.bridge.invokeApi("previewFile", e)
        }, uploadFile: function (e) {
            var n = e.onSuccess, t = e.onError;
            return e.onSuccess = function (e) {
                if (n) try {
                    e.response ? n(a(e.response)) : n(e)
                } catch (e) {
                    t && t(e)
                }
            }, e.onError = function (e) {
                if (t) try {
                    e.response && (e.response = a(e.response)), t(e)
                } catch (e) {
                    t(e)
                }
            }, g.bridge.invokeProgressApi("uploadFile", e)
        }, downloadFile: function (e) {
            return g.bridge.invokeProgressApi("downloadFile", e)
        }, getLocationInfo: function (e) {
            return g.bridge.invokeApi("getLocationInfo", e)
        }, chooseImage: function () {
            var e = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : b;
            return g.bridge.invokeApi("chooseImage", e)
        }, previewImage: function (e) {
            return g.bridge.invokeApi("previewImage", e)
        }, getImageBase64: function (e) {
            return g.bridge.invokeApi("getImageBase64", e)
        }, saveImageToAlbum: function (e) {
            return g.bridge.invokeApi("saveImageToAlbum", e)
        }, previewImageById: function (e) {
            return g.bridge.invokeApi("previewImageById", e)
        }, setNavigationButton: function (e) {
            return e.options = {undeleteCallback: !0}, g.bridge.invokeApi("setNavigationButton", e)
        }, closeNavBar: function () {
            return g.bridge.invokeApi("closeNavBar")
        }, setSidebarButton: function (e) {
            return g.bridge.invokeApi("setSidebarButton", e)
        }, hideMenuItems: function (e) {
            return g.bridge.invokeApi("hideMenuItems", e)
        }, showMenuItems: function (e) {
            return g.bridge.invokeApi("showMenuItems", e)
        }, getDeviceInfo: function (e) {
            return g.bridge.invokeApi("getDeviceInfo", e)
        }, getAppInfo: function (e) {
            return g.bridge.invokeApi("getAppInfo", e)
        }, authorize: function (e) {
            return g.bridge.invokeApi("authorize", e)
        }, getWebAppInfo: function (e) {
            return g.bridge.invokeApi("getWebAppInfo", e)
        }, showAlert: function (e) {
            return g.bridge.invokeApi("showAlert", e)
        }, showConfirm: function (e) {
            return g.bridge.invokeApi("showConfirm", e)
        }, showPrompt: function (e) {
            return g.bridge.invokeApi("showPrompt", e)
        }, showToast: function (e) {
            return g.bridge.invokeApi("showToast", e)
        }, showPreloader: function (e) {
            return g.bridge.invokeApi("showPreloader", e)
        }, hidePreloader: function (e) {
            return g.bridge.invokeApi("hidePreloader", e)
        }, showActionSheet: function (e) {
            return g.bridge.invokeApi("showActionSheet", e)
        }, openUrl: function (e) {
            return g.bridge.invokeApi("openUrl", e)
        }, closeApp: function () {
            return g.bridge.invokeApi("closeApp")
        }, closeWeb: function () {
            return g.bridge.invokeApi("closeWeb")
        }, closeSidebar: function () {
            return g.bridge.invokeApi("closeSidebar")
        }, goHome: function () {
            return g.bridge.invokeApi("goHome")
        }
    });
    return window.ksoxz_sdk = m, console.log("ksoxz jssdk version:", k), m
}));


window.ksoxz_sdk.ready()