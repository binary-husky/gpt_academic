class WelcomeMessage {
    constructor() {
        this.static_welcome_message = [
            {
                title: "论文翻译与润色",
                content: "跨越学术交流语言障碍。"
            },
            {
                title: "PDF翻译",
                content: "这是一个可以翻译PDF内容的工具。"
            },
            {
                title: "推荐配置",
                content: "这是一个根据你的需求推荐最佳配置的工具。"
            },
            {
                title: "论文翻译与润色",
                content: "跨越学术交流语言障碍。"
            },
            {
                title: "PDF翻译",
                content: "这是一个可以翻译PDF内容的工具。"
            },
            {
                title: "推荐配置",
                content: "这是一个根据你的需求推荐最佳配置的工具。"
            }
        ];
        this.visible = false;

    }

    begin_render() {
        this.update();
        setInterval(() => { this.update() }, 2000); // 每2000毫秒执行一次
    }

    async update() {
        console.log('update')
        if (!await this.isChatbotEmpty()) {
            if (this.visible) {
                this.removeWelcome();
                this.visible = false;
            }
            return; 
        }
        if (this.visible){
            return;
        }
        this.showWelcome();
        this.visible = true;
    }

    async showWelcome() {

        // 首先，找到你想要添加子元素的父元素
        const elem_chatbot = document.getElementById('gpt-chatbot');

        // 创建一个新的div元素
        const welcome_card_container = document.createElement('div');
        welcome_card_container.classList.add('welcome-card-container');
        
        // 创建主标题
        const major_title = document.createElement('div');
        major_title.classList.add('welcome-card-title');
        major_title.textContent = "欢迎使用GPT-Academic";
        // major_title.style.paddingBottom = '5px'
        welcome_card_container.appendChild(major_title)

        // 创建卡片
        this.static_welcome_message.forEach(function (message) {
            const card = document.createElement('div');
            card.classList.add('welcome-card');

            // 创建标题
            const title = document.createElement('p');
            title.textContent = message.title;
            title.style.fontSize = '20px'
            title.style.paddingBottom = '5px'

            // 创建内容
            const content = document.createElement('p');
            content.textContent = message.content;

            // 将标题和内容添加到卡片 div 中
            card.appendChild(title);
            card.appendChild(content);
            welcome_card_container.appendChild(card);
        });

        elem_chatbot.appendChild(welcome_card_container);
    }

    async removeWelcome() {
        // remove welcome-card-container
        const elem_chatbot = document.getElementById('gpt-chatbot');
        const welcome_card_container = document.getElementsByClassName('welcome-card-container')[0];
        elem_chatbot.removeChild(welcome_card_container);
    }

    async isChatbotEmpty() {
        return (await get_data_from_gradio_component("gpt-chatbot")).length == 0;
    }


}

