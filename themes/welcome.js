class WelcomeMessage {
    constructor() {
        this.static_welcome_message = [

        ];
        this.visible = false;
        this.max_welcome_card_num = 6;
        this.card_array = [];
        this.static_welcome_message_previous = [];
        this.reflesh_time_interval = 15*1000;


        const reflesh_render_status = () => {
            for (let index = 0; index < this.card_array.length; index++) {
                const card = this.card_array[index];
                card.classList.remove('hide');
                card.classList.remove('show');
            }
        };
        const pageFocusHandler = new PageFocusHandler();
        pageFocusHandler.addFocusCallback(reflesh_render_status);
    }

    begin_render() {
        this.update();
    }

    async startRefleshCards() {
        await new Promise(r => setTimeout(r, this.reflesh_time_interval));
        await this.reflesh_cards();
        if (this.visible){
            setTimeout(() => {
                this.startRefleshCards.call(this);
            }, 1);
        }
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
                // 已经包含了 hide 属性？
                if (card.classList.contains('hide') || card.classList.contains('show')) {
                    card.classList.remove('hide');
                    card.classList.remove('show');
                    continue;
                }

                // 等待动画结束
                card.addEventListener('transitionend', () => {
                    // 更新卡片信息
                    const message = this.static_welcome_message_previous[index];
                    const title = card.getElementsByClassName('welcome-card-title')[0];
                    const content = card.getElementsByClassName('welcome-content-c')[0];
                    const svg = card.getElementsByClassName('welcome-svg')[0];
                    const text = card.getElementsByClassName('welcome-title-text')[0];
                    svg.src = message.svg;
                    text.textContent = message.title;
                    text.href = message.url;
                    content.textContent = message.content;
                    card.classList.remove('hide');

                    // 等待动画结束
                    card.addEventListener('transitionend', () => {
                        card.classList.remove('show');
                    }, { once: true });
                    card.classList.add('show');

                }, { once: true });

                card.classList.add('hide');

                // 等待 250 毫秒
                await new Promise(r => setTimeout(r, 200));
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
        // console.log('update')
        var page_width = document.documentElement.clientWidth;
        const width_to_hide_welcome = 1200;
        if (!await this.isChatbotEmpty() || page_width < width_to_hide_welcome) {
            if (this.visible) {
                this.removeWelcome();
                this.visible = false;
                this.card_array = [];
                this.static_welcome_message_previous = [];
            }
            return;
        }
        if (this.visible){
            return;
        }
        // console.log("welcome");
        this.showWelcome();
        this.visible = true;
        this.startRefleshCards();
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
            const content_c = document.createElement('div');
            content_c.classList.add('welcome-content-c');
            content_c.textContent = message.content;
            content.appendChild(content_c);

        // 将标题和内容添加到卡片 div 中
        card.appendChild(title);
        card.appendChild(content);
        return card;
    }

    async showWelcome() {

        // 首先，找到想要添加子元素的父元素
        const elem_chatbot = document.getElementById('gpt-chatbot');

        // 创建一个新的div元素
        const welcome_card_container = document.createElement('div');
        welcome_card_container.classList.add('welcome-card-container');

        // 创建主标题
        const major_title = document.createElement('div');
        major_title.classList.add('welcome-title');
        major_title.textContent = "欢迎使用";
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




class PageFocusHandler {
    constructor() {
      this.hasReturned = false;
      this.focusCallbacks = [];

      // Bind the focus and blur event handlers
      window.addEventListener('visibilitychange', this.handleFocus.bind(this));
    }

    // Method to handle the focus event
    handleFocus() {
      if (this.hasReturned) {
        this.focusCallbacks.forEach(callback => callback());
      }
      this.hasReturned = true;
    }

    // Method to add a custom callback function
    addFocusCallback(callback) {
      if (typeof callback === 'function') {
        this.focusCallbacks.push(callback);
      } else {
        throw new Error('Callback must be a function');
      }
    }
}


