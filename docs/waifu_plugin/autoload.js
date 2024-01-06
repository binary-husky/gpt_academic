try {
    $("<link>").attr({href: "file=docs/waifu_plugin/waifu.css", rel: "stylesheet", type: "text/css"}).appendTo('head');
    $('body').append('<div class="waifu"><div class="waifu-tips"></div><canvas id="live2d" class="live2d"></canvas><div class="waifu-tool"><span class="fui-home"></span> <span class="fui-chat"></span> <span class="fui-eye"></span> <span class="fui-user"></span> <span class="fui-photo"></span> <span class="fui-info-circle"></span> <span class="fui-cross"></span></div></div>');
    $.ajax({url: "file=docs/waifu_plugin/waifu-tips.js", dataType:"script", cache: true, success: function() {
        $.ajax({url: "file=docs/waifu_plugin/live2d.js", dataType:"script", cache: true, success: function() {
            /* 可直接修改部分参数 */
            live2d_settings['hitokotoAPI'] = "hitokoto.cn";  // 一言 API
            live2d_settings['modelId'] = 5;                  // 默认模型 ID
            live2d_settings['modelTexturesId'] = 1;          // 默认材质 ID
            live2d_settings['modelStorage'] = false;         // 不储存模型 ID
            live2d_settings['waifuSize']            = '210x187';  
            live2d_settings['waifuTipsSize']        = '187x52';  
            live2d_settings['canSwitchModel']       = true;
            live2d_settings['canSwitchTextures']    = true;
            live2d_settings['canSwitchHitokoto']    = false;
            live2d_settings['canTakeScreenshot']    = false;
            live2d_settings['canTurnToHomePage']    = false;
            live2d_settings['canTurnToAboutPage']   = false;
            live2d_settings['showHitokoto']         = false;         // 显示一言
            live2d_settings['showF12Status']        = false;         // 显示加载状态
            live2d_settings['showF12Message']       = false;        // 显示看板娘消息
            live2d_settings['showF12OpenMsg']       = false;         // 显示控制台打开提示
            live2d_settings['showCopyMessage']      = false;         // 显示 复制内容 提示
            live2d_settings['showWelcomeMessage']   = true;         // 显示进入面页欢迎词

            /* 在 initModel 前添加 */
            initModel("file=docs/waifu_plugin/waifu-tips.json");
        }});
    }});
} catch(err) { console.log("[Error] JQuery is not defined.") }
