function ChatBotHeight() {
    function update_height(){
        var { panel_height_target, chatbot_height, chatbot } = get_elements();
        if (panel_height_target!=chatbot_height)
        {
            var pixelString = panel_height_target.toString() + 'px';
            chatbot.style.maxHeight = pixelString; chatbot.style.height = pixelString; 
        }
    }

    function update_height_slow(){
        var { panel_height_target, chatbot_height, chatbot } = get_elements();
        if (panel_height_target!=chatbot_height)
        {
            new_panel_height = (panel_height_target - chatbot_height)*0.5 + chatbot_height;
            if (Math.abs(new_panel_height - panel_height_target) < 10){
                new_panel_height = panel_height_target;
            }
            // console.log(chatbot_height, panel_height_target, new_panel_height);
            var pixelString = new_panel_height.toString() + 'px';
            chatbot.style.maxHeight = pixelString; chatbot.style.height = pixelString; 
        }
    }

    update_height();
    setInterval(function() {
        update_height_slow()
    }, 50); // 每100毫秒执行一次
}

function get_elements() {
    var chatbot = document.querySelector('#gpt-chatbot > div.wrap.svelte-18telvq');
    if (!chatbot) {
        chatbot = document.querySelector('#gpt-chatbot');
    }
    const panel1 = document.querySelector('#input-panel');
    const panel2 = document.querySelector('#basic-panel');
    const panel3 = document.querySelector('#plugin-panel');
    const panel4 = document.querySelector('#interact-panel');
    const panel5 = document.querySelector('#input-panel2');
    const panel_active = document.querySelector('#state-panel');
    var panel_height_target = (20-panel_active.offsetHeight) + panel1.offsetHeight + panel2.offsetHeight + panel3.offsetHeight + panel4.offsetHeight + panel5.offsetHeight + 21;
    var panel_height_target = parseInt(panel_height_target);
    var chatbot_height = chatbot.style.height;
    var chatbot_height = parseInt(chatbot_height);
    return { panel_height_target, chatbot_height, chatbot };
}