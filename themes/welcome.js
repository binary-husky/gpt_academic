class WelcomeMessage {
    constructor() {
        this.static_welcome_message = [
            {
                title: "环境配置教程",
                content: "配置模型和插件，释放大语言模型的学术应用潜力。",
                svg: "file=themes/svg/Environmental Configuration Tutorial.svg",
                url: "https://github.com/binary-husky/gpt_academic",
            },
            {
                title: "Arxiv论文一键翻译",
                content: "无缝切换学术阅读语言，最优英文转中文的学术论文阅读体验。",
                svg: "file=themes/svg/arxiv-00aeff.svg",
                url: "https://github.com/binary-husky/gpt_academic",
            },
            {
                title: "多模态模型",
                content: "试试将截屏直接粘贴到输入框中，随后使用多模态模型提问。",
                svg: "file=themes/svg/Multimodal-00aeff.svg",
                url: "https://github.com/binary-husky/gpt_academic",
            },
            {
                title: "文档与源码批处理",
                content: "您可以将任意文件拖入「此处」，随后调用对应插件功能。",
                svg: "file=themes/svg/document-00aeff.svg",
                url: "https://github.com/binary-husky/gpt_academic",
            },
            {
                title: "图表与脑图绘制",
                content: "试试输入一段语料，然后点击「总结绘制脑图」。",
                svg: "file=themes/svg/brain_map_00aeff.svg",
                url: "https://github.com/binary-husky/gpt_academic",
            },
            {
                title: "虚空终端",
                content: "点击右侧插件区的「虚空终端」插件，然后直接输入您的想法。",
                svg: "file=themes/svg/plane-terminal-00aeff.svg",
                url: "https://github.com/binary-husky/gpt_academic",
            },
            {
                title: "DALLE图像生成",
                content: "接入DALLE生成插画或者项目Logo，辅助头脑风暴并激发灵感。",
                svg: "file=themes/svg/AIGC_ Image Generation_00aeff.svg",
                url: "https://github.com/binary-husky/gpt_academic",
            },
            {
                title: "TTS语音克隆",
                content: "借助SoVits，以你喜爱的角色的声音回答问题。",
                svg: "file=themes/svg/MPIS-TTS-00aeff.svg",
                url: "https://github.com/binary-husky/gpt_academic",
            }
        ];
        this.visible = false;

    }

    begin_render() {
        this.update();
        setInterval(() => { this.update() }, 5000); // 每5000毫秒执行一次
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
        major_title.classList.add('welcome-title');
        major_title.textContent = "欢迎使用GPT-Academic";
        // major_title.style.paddingBottom = '5px'
        welcome_card_container.appendChild(major_title)

        // 创建卡片
        this.static_welcome_message.forEach(function (message) {
            const card = document.createElement('div');
            card.classList.add('welcome-card');



            // 创建标题
            const title = document.createElement('div');
            title.classList.add('welcome-card-title');
                // 创建图标
                const svg = document.createElement('img');
                svg.classList.add('welcome-svg');
                svg.src = message.svg;
                svg.style.height = '30px';
                title.appendChild(svg);

                // 创建标题
                const text = document.createElement('a');
                text.textContent = message.title;
                text.classList.add('welcome-title-text');
                text.href = message.url;
                text.target = "_blank";
                title.appendChild(text)

            // 创建内容
            const content = document.createElement('div');
            content.classList.add('welcome-content');
            content.textContent = message.content;


            // 将标题和内容添加到卡片 div 中
            card.appendChild(title);
            card.appendChild(content);
            welcome_card_container.appendChild(card);
        });

        elem_chatbot.appendChild(welcome_card_container);
    
        // 添加显示动画
        requestAnimationFrame(() => {
            welcome_card_container.classList.add('show');
        });
    }

    async removeWelcome() {
        // remove welcome-card-container
        const elem_chatbot = document.getElementById('gpt-chatbot');
        const welcome_card_container = document.getElementsByClassName('welcome-card-container')[0];
        // 添加隐藏动画
        welcome_card_container.classList.add('hide');

        // 等待动画结束后再移除元素
        welcome_card_container.addEventListener('transitionend', () => {
            elem_chatbot.removeChild(welcome_card_container);
        }, { once: true });
    }

    async isChatbotEmpty() {
        return (await get_data_from_gradio_component("gpt-chatbot")).length == 0;
    }


}

