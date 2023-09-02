function ChatBotHeight() {
    function update_height(){
        var { panel_height_target, chatbot_height, chatbot } = get_elements(true);
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

function get_elements(consider_state_panel=false) {
    var chatbot = document.querySelector('#gpt-chatbot > div.wrap.svelte-18telvq');
    if (!chatbot) {
        chatbot = document.querySelector('#gpt-chatbot');
    }
    const panel1 = document.querySelector('#input-panel').getBoundingClientRect();
    const panel2 = document.querySelector('#basic-panel').getBoundingClientRect()
    const panel3 = document.querySelector('#plugin-panel').getBoundingClientRect();
    const panel4 = document.querySelector('#interact-panel').getBoundingClientRect();
    const panel5 = document.querySelector('#input-panel2').getBoundingClientRect();
    const panel_active = document.querySelector('#state-panel').getBoundingClientRect();
    if (consider_state_panel || panel_active.height < 25){
        document.state_panel_height = panel_active.height;
    }
    // 25 是chatbot的label高度, 16 是右侧的gap
    var panel_height_target = panel1.height + panel2.height + panel3.height + panel4.height + panel5.height - 25 + 16*3;
    // 禁止动态的state-panel高度影响
    panel_height_target = panel_height_target + (document.state_panel_height-panel_active.height)
    var panel_height_target = parseInt(panel_height_target);
    var chatbot_height = chatbot.style.height;
    var chatbot_height = parseInt(chatbot_height);
    return { panel_height_target, chatbot_height, chatbot };
}