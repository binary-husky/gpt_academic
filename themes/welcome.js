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
                title: "论文一键翻译",
                content: "利用「Arxiv论文精细翻译」或「精准翻译PDF论文」插件实现论文全文翻译。",
                svg: "file=themes/svg/arxiv-00aeff.svg",
                url: "https://github.com/binary-husky/gpt_academic",
            },
            {
                title: "多模态模型",
                content: "试试将图片直接粘贴到“输入区”下方输入框，随后在“更多函数插件”下方输入框输入“DALLE”选择相应插件按照指导使用。",
                svg: "file=themes/svg/Multimodal-00aeff.svg",
                url: "https://github.com/binary-husky/gpt_academic",
            },
            {
                title: "文档与源码批处理",
                content: "您可以将任意文件拖入“输入区”下方输入框，随后调用对应插件功能。",
                svg: "file=themes/svg/document-00aeff.svg",
                url: "https://github.com/binary-husky/gpt_academic",
            },
            {
                title: "图表与脑图绘制",
                content: "试试输入一段语料，然后在“基础功能区”中选择「总结绘制脑图」插件。",
                svg: "file=themes/svg/brain_map_00aeff.svg",
                url: "https://github.com/binary-husky/gpt_academic",
            },
            {
                title: "虚空终端",
                content: "首先点击右侧“函数插件区”的「虚空终端」插件，然后在“输入区”下方输入框输入您的想法例如“请帮我翻译arxiv论文，编号是1710.10903”，最后点击提交即可。",
                svg: "file=themes/svg/plane-terminal-00aeff.svg",
                url: "https://github.com/binary-husky/gpt_academic",
            },
            {
                title: "DALLE图像生成",
                content: "在“更多函数插件”下方输入框输入“DALLE”选择图像生成相关插件，然后在“输入区”下方输入框输入您的想法例如“请帮我画一只兔子”，最后点击「图片生成...」插件即可。",
                svg: "file=themes/svg/AIGC_ Image Generation_00aeff.svg",
                url: "https://github.com/binary-husky/gpt_academic",
            },
            {
                title: "TTS语音克隆",
                content: "借助SoVits，以你喜爱的角色的声音回答问题。",
                svg: "file=themes/svg/MPIS-TTS-00aeff.svg",
                url: "https://github.com/binary-husky/gpt_academic",
            },
            {
                title: "中英文论文Latex全文润色",
                content: "在“上传文件”区上传待润色latex源码，然后在“更多函数插件”下方输入框输入“润色”选择所需插件，最后点击所选择插件即可",
                svg: "file=themes/svg/ic-polish.svg",
                url: "https://github.com/binary-husky/gpt_academic",
            }
        ];
        this.visible = false;
        this.max_welcome_card_num = 6;
        this.card_array = [];
        this.static_welcome_message_previous = [];
    }

    begin_render() {
        this.update();
        this.startRefleshCards();
    }

    async startRefleshCards() {
        await this.reflesh_cards();
        setTimeout(() => {
            this.startRefleshCards.call(this);
        }, 15000);
    }
    
    async reflesh_cards() {
        if (!this.visible){
            return;
        }

        // re-rank this.static_welcome_message randomly
        this.static_welcome_message_temp = this.shuffle(this.static_welcome_message);

        // find items that in this.static_welcome_message_temp but not in this.static_welcome_message_previous
        const not_shown_previously = this.static_welcome_message_temp.filter(item => !this.static_welcome_message_previous.includes(item));
        const already_shown_previously = this.static_welcome_message_temp.filter(item => this.static_welcome_message_previous.includes(item));

        // combine two lists
        this.static_welcome_message_previous = not_shown_previously.concat(already_shown_previously);

        (async () => {
            // 使用 for...of 循环来处理异步操作
            for (let index = 0; index < this.card_array.length; index++) {
                if (index >= this.max_welcome_card_num) {
                    break;
                }
        
                const card = this.card_array[index];
        
                // 等待动画结束
                card.addEventListener('transitionend', () => {
                    // 更新卡片信息
                    const message = this.static_welcome_message_previous[index];
                    const title = card.getElementsByClassName('welcome-card-title')[0];
                    const content = card.getElementsByClassName('welcome-content')[0];
                    const svg = card.getElementsByClassName('welcome-svg')[0];
                    const text = card.getElementsByClassName('welcome-title-text')[0];
                    svg.src = message.svg;
                    text.textContent = message.title;
                    text.href = message.url;
                    content.textContent = message.content;
                    card.classList.remove('hide');
                    card.classList.add('show');
                }, { once: true });
        
                card.classList.add('hide');
        
                // 等待 500 毫秒
                await new Promise(r => setTimeout(r, 250));
            }
        })();
    }

    shuffle(array) {
        var currentIndex = array.length,  randomIndex;
      
        // While there remain elements to shuffle...
        while (currentIndex != 0) {
      
          // Pick a remaining element...
          randomIndex = Math.floor(Math.random() * currentIndex);
          currentIndex--;
      
          // And swap it with the current element.
          [array[currentIndex], array[randomIndex]] = [
            array[randomIndex], array[currentIndex]];
        }
      
        return array;
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

    showCard(message) {
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
        return card;
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
        welcome_card_container.appendChild(major_title)

        // 创建卡片
        this.static_welcome_message.forEach((message, index) => {
            if (index >= this.max_welcome_card_num) {
                return;
            }
            this.static_welcome_message_previous.push(message);
            const card = this.showCard(message);
            this.card_array.push(card);
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

