const uml = async className => {

    // Custom element to encapsulate Mermaid content.
    class MermaidDiv extends HTMLElement {

        /**
        * Creates a special Mermaid div shadow DOM.
        * Works around issues of shared IDs.
        * @return {void}
        */
        constructor() {
            super()

            // Create the Shadow DOM and attach style
            const shadow = this.attachShadow({ mode: "open" })
            const style = document.createElement("style")
            style.textContent = `
        :host {
          display: block;
          line-height: initial;
          font-size: 16px;
        }
        div.diagram {
          margin: 0;
          overflow: visible;
        }`
            shadow.appendChild(style)
        }
    }

    if (typeof customElements.get("diagram-div") === "undefined") {
        customElements.define("diagram-div", MermaidDiv)
    }

    const getFromCode = parent => {
        // Handles <pre><code> text extraction.
        let text = ""
        for (let j = 0; j < parent.childNodes.length; j++) {
            const subEl = parent.childNodes[j]
            if (subEl.tagName.toLowerCase() === "code") {
                for (let k = 0; k < subEl.childNodes.length; k++) {
                    const child = subEl.childNodes[k]
                    const whitespace = /^\s*$/
                    if (child.nodeName === "#text" && !(whitespace.test(child.nodeValue))) {
                        text = child.nodeValue
                        break
                    }
                }
            }
        }
        return text
    }

    // 给出配置 Provide a default config in case one is not specified
    const defaultConfig = {
        startOnLoad: false,
        theme: "default",
        flowchart: {
            htmlLabels: false
        },
        er: {
            useMaxWidth: false
        },
        sequence: {
            useMaxWidth: false,
            noteFontWeight: "14px",
            actorFontSize: "14px",
            messageFontSize: "16px"
        }
    }
    // console.log('启动渲染');
    // 加载配置 Load up the config
    mermaid.mermaidAPI.globalReset() // 全局复位
    const config = (typeof mermaidConfig === "undefined") ? defaultConfig : mermaidConfig
    mermaid.initialize(config)

    // 查找需要渲染的元素 Find all of our Mermaid sources and render them.
    const blocks = document.querySelectorAll(`pre.${className}, diagram-div`);
    for (let i = 0; i < blocks.length; i++) {
        var block = blocks[i]
        // const res = await mermaid.render(`_diagram_${i}`, getFromCode(parentEl))
        var code = getFromCode(block);
        let code2Element = document.createElement("code2"); // 创建一个新的code2元素
        let existingCode2Element = block.querySelector("code2"); // 如果block下已存在code2元素，则获取它
        let codeContent = block.querySelector("code").textContent; // 获取code元素中的文本内容
        if(existingCode2Element){ // 如果block下已存在code2元素
            existingCode2Element.style.display = "none";
            if(existingCode2Element.textContent !== codeContent){
                existingCode2Element.textContent = codeContent; // 如果现有的code2元素中的内容与code元素中的内容不同，更新code2元素中的内容
            }
            else{
                continue;
            }
        } else { // 如果不存在code2元素，则将code元素中的内容添加到新创建的code2元素中
            code2Element.style.display = "none";
            code2Element.textContent = codeContent;
            block.appendChild(code2Element); // 将新创建的code2元素添加到block中
        }

        /////////////////////////////////////////////////////////////////
        //尝试获取已存在的<div class='mermaid_render'>
        let mermaidRender = block.querySelector(".mermaid_render");
        if (!mermaidRender) {
            mermaidRender = document.createElement("div");  // 不存在，创建新的<div class='mermaid_render'>
            mermaidRender.classList.add("mermaid_render");
            block.appendChild(mermaidRender);               // 将新创建的元素附加到block
        }
        /////////////////////////////////////////////////////////////////
        const content = await mermaid.render(`_diagram_${i}`, code)
        mermaidRender.innerHTML = content

    }
}
