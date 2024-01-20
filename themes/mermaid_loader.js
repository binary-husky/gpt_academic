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

    function createOrUpdateHyperlink(parentElement, linkText, linkHref) {
        // Search for an existing anchor element within the parentElement
        let existingAnchor = parentElement.querySelector("a");

        // Check if an anchor element already exists
        if (existingAnchor) {
            // Update the hyperlink reference if it's different from the current one
            if (existingAnchor.href !== linkHref) {
                existingAnchor.href = linkHref;
            }
            // Update the target attribute to ensure it opens in a new tab
            existingAnchor.target = '_blank';

            // If the text must be dynamic, uncomment and use the following line:
            // existingAnchor.textContent = linkText;
        } else {
            // If no anchor exists, create one and append it to the parentElement
            let anchorElement = document.createElement("a");
            anchorElement.href = linkHref; // Set hyperlink reference
            anchorElement.textContent = linkText; // Set text displayed
            anchorElement.target = '_blank'; // Ensure it opens in a new tab
            parentElement.appendChild(anchorElement); // Append the new anchor element to the parent
        }
    }

    function removeLastLine(str) {
        // 将字符串按换行符分割成数组
        var lines = str.split('\n');
        lines.pop();
        // 将数组重新连接成字符串，并按换行符连接
        var result = lines.join('\n');
        return result;
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
    if (document.body.classList.contains("dark")) {
        defaultConfig.theme = "dark"
    }
    
    const Module = await import('./file=themes/mermaid_editor.js');

    function do_render(block, code, codeContent, cnt) {
        var rendered_content = mermaid.render(`_diagram_${cnt}`, code);
        ////////////////////////////// 记录有哪些代码已经被渲染了 ///////////////////////////////////
        let codeFinishRenderElement = block.querySelector("code_finish_render"); // 如果block下已存在code_already_rendered元素，则获取它
        if (codeFinishRenderElement) {                                             // 如果block下已存在code_already_rendered元素
            codeFinishRenderElement.style.display = "none";
        } else {
            // 如果不存在code_finish_render元素，则将code元素中的内容添加到新创建的code_finish_render元素中
            let codeFinishRenderElementNew = document.createElement("code_finish_render"); // 创建一个新的code_already_rendered元素
            codeFinishRenderElementNew.style.display = "none";
            codeFinishRenderElementNew.textContent = "";
            block.appendChild(codeFinishRenderElementNew); // 将新创建的code_already_rendered元素添加到block中
            codeFinishRenderElement = codeFinishRenderElementNew;
        }

        ////////////////////////////// 创建一个用于渲染的容器 ///////////////////////////////////
        let mermaidRender = block.querySelector(".mermaid_render"); // 尝试获取已存在的<div class='mermaid_render'>
        if (!mermaidRender) {
            mermaidRender = document.createElement("div");  // 不存在，创建新的<div class='mermaid_render'>
            mermaidRender.classList.add("mermaid_render");
            block.appendChild(mermaidRender);               // 将新创建的元素附加到block
        }
        mermaidRender.innerHTML = rendered_content
        codeFinishRenderElement.textContent = code  // 标记已经渲染的部分

        ////////////////////////////// 创建一个“点击这里编辑脑图” ///////////////////////////////
        let pako_encode = Module.serializeState({
            "code": codeContent,
            "mermaid": "{\n  \"theme\": \"default\"\n}",
            "autoSync": true,
            "updateDiagram": false
        });
        createOrUpdateHyperlink(block, "点击这里编辑脑图", "https://mermaid.live/edit#" + pako_encode)
    }

    // 加载配置 Load up the config
    mermaid.mermaidAPI.globalReset() // 全局复位
    const config = (typeof mermaidConfig === "undefined") ? defaultConfig : mermaidConfig
    mermaid.initialize(config)
    // 查找需要渲染的元素 Find all of our Mermaid sources and render them.
    const blocks = document.querySelectorAll(`pre.mermaid`);

    for (let i = 0; i < blocks.length; i++) {
        var block = blocks[i]
        ////////////////////////////// 如果代码没有发生变化，就不渲染了 ///////////////////////////////////
        var code = getFromCode(block);
        let code_elem = block.querySelector("code");
        let codeContent = code_elem.textContent; // 获取code元素中的文本内容

        // 判断codeContent是否包含'<gpt_academic_hide_mermaid_code>'，如果是，则使code_elem隐藏
        if (codeContent.indexOf('<gpt_academic_hide_mermaid_code>') !== -1) {
            code_elem.style.display = "none";
        }

        // 如果block下已存在code_already_rendered元素，则获取它
        let codePendingRenderElement = block.querySelector("code_pending_render");
        if (codePendingRenderElement) {                               // 如果block下已存在code_pending_render元素
            codePendingRenderElement.style.display = "none";
            if (codePendingRenderElement.textContent !== codeContent) {
                codePendingRenderElement.textContent = codeContent; // 如果现有的code_pending_render元素中的内容与code元素中的内容不同，更新code_pending_render元素中的内容
            }
            else {
                continue; // 如果相同，就不处理了
            }
        } else { // 如果不存在code_pending_render元素，则将code元素中的内容添加到新创建的code_pending_render元素中
            let codePendingRenderElementNew = document.createElement("code_pending_render"); // 创建一个新的code_already_rendered元素
            codePendingRenderElementNew.style.display = "none";
            codePendingRenderElementNew.textContent = codeContent;
            block.appendChild(codePendingRenderElementNew); // 将新创建的code_pending_render元素添加到block中
            codePendingRenderElement = codePendingRenderElementNew;
        }

        ////////////////////////////// 在这里才真正开始渲染 ///////////////////////////////////
        try {
            do_render(block, code, codeContent, i);
            // console.log("渲染", codeContent);
        } catch (err) {
            try {
                var lines = code.split('\n'); if (lines.length < 2) { continue; }
                do_render(block, removeLastLine(code), codeContent, i);
                // console.log("渲染", codeContent);
            } catch (err) {
                console.log("以下代码不能渲染", code, removeLastLine(code), err);
            }
        }
    }
}
