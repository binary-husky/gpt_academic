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


    function addZoomEffect(svgElement) {
        svgElement.addEventListener('wheel', event => {
            event.preventDefault();
            const scaleAmount = event.deltaY * -0.01;
            const currentScale = Number(svgElement.getAttribute('data-scale') || 1);
            const newScale = Math.max(0.1, currentScale + scaleAmount);
            svgElement.style.transform = `scale(${newScale})`;
            svgElement.setAttribute('data-scale', newScale.toString());
        });
    }

    function addDragEffect(svgElement) {
        let isDragging = false;
        let lastPosX = 0;
        let lastPosY = 0;

        svgElement.addEventListener('mousedown', event => {
            isDragging = true;
            lastPosX = event.clientX;
            lastPosY = event.clientY;
        });

        window.addEventListener('mousemove', event => {
            if (isDragging) {
                const dx = event.clientX - lastPosX;
                const dy = event.clientY - lastPosY;
                const currentTransform = svgElement.style.transform;
                svgElement.style.transform = `${currentTransform} translate(${dx}px, ${dy}px)`;
                lastPosX = event.clientX;
                lastPosY = event.clientY;
            }
        });

        window.addEventListener('mouseup', () => {
            isDragging = false;
        });
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

    const Module = await import('/file=themes/mermaid_editor.js');

    function do_render(block, code, codeContent, cnt) {
        var svgCode = mermaid.render(`_diagram_${cnt}`, code);
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
        let first_time_create = false;
        if (!mermaidRender) {
            first_time_create = true;
            mermaidRender = document.createElement("div");  // 不存在，创建新的<div class='mermaid_render'>
            mermaidRender.classList.add("mermaid_render");
            // 增加style overflow auto
            mermaidRender.style.overflow = "auto";
            mermaidRender.style.position = "relative";
            mermaidRender.style.display = "flex";
            block.appendChild(mermaidRender);               // 将新创建的元素附加到block
        }
        mermaidRender.innerHTML = svgCode;
        codeFinishRenderElement.textContent = code          // 标记已经渲染的部分
        if (first_time_create){
            const svgElement = mermaidRender.querySelector('svg');
            if (svgElement) {
                svgElement.setAttribute('data-scale', '1');
                // addZoomEffect(svgElement);
                addDragEffect(svgElement);
                // 左上角，增加放大，缩小，重置按钮
                let div = make_zoom_btn(svgElement)
                mermaidRender.appendChild(div);
            }
        }

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
        if (codePendingRenderElement) {                                 // 如果block下已存在code_pending_render元素
            codePendingRenderElement.style.display = "none";
            if (codePendingRenderElement.textContent !== codeContent) {
                codePendingRenderElement.textContent = codeContent;     // 如果现有的code_pending_render元素中的内容与code元素中的内容不同，更新code_pending_render元素中的内容
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
                // codeContent 用来生成编辑链接
                do_render(block, removeLastLine(code), codeContent, i);
                // console.log("渲染", codeContent);
            } catch (err) {
                console.log("以下代码不能渲染", code, removeLastLine(code), err);
            }
        }
    }
}


function make_zoom_btn(svgElement) {
    let zoomInButton = document.createElement("button")

    let zoomInSvg = document.createElementNS("http://www.w3.org/2000/svg", "svg")
    zoomInSvg.setAttribute("viewBox", "0 0 1024 1024")
    zoomInSvg.setAttribute("width", "20") // 设置合适的尺寸
    zoomInSvg.setAttribute("height", "20")
    zoomInSvg.setAttribute("version", "1.1")
    zoomInSvg.style.fill = "white" // 设置颜色
    const zoomInPath = document.createElementNS("http://www.w3.org/2000/svg", "path")
    zoomInPath.setAttribute('d', 'M463.238095 146.285714c175.055238 0 316.952381 141.897143 316.952381 316.952381 0 77.775238-28.038095 149.040762-74.532571 204.214857l188.440381 194.535619-55.247238 57.002667-191.536762-197.705143A315.489524 315.489524 0 0 1 463.238095 780.190476c-175.055238 0-316.952381-141.897143-316.952381-316.952381S288.182857 146.285714 463.238095 146.285714z m0 73.142857C328.582095 219.428571 219.428571 328.582095 219.428571 463.238095s109.153524 243.809524 243.809524 243.809524a242.883048 242.883048 0 0 0 161.889524-61.513143l25.551238-26.355809A242.834286 242.834286 0 0 0 707.047619 463.238095c0-134.656-109.153524-243.809524-243.809524-243.809524z m36.571429 97.52381v109.714286H609.52381v73.142857h-109.714286V609.52381h-73.142857v-109.738667L316.952381 499.809524v-73.142857l109.714286-0.024381V316.952381h73.142857z')
    zoomInSvg.append(zoomInPath)

    zoomInButton.appendChild(zoomInSvg)
    zoomInButton.onclick = function () {
        // 放大逻辑
        let currentScale = Number(svgElement.getAttribute('data-scale') || 1)
        let newScale = Math.min(10, currentScale + 0.1)
        svgElement.style.transform = `scale(${newScale})`
        svgElement.setAttribute('data-scale', newScale.toString())
    }

    let zoomOutButton = document.createElement("button")
    let zoomOutSvg = document.createElementNS("http://www.w3.org/2000/svg", "svg")
    zoomOutSvg.setAttribute("viewBox", "0 0 1024 1024")
    zoomOutSvg.setAttribute("width", "20") // 设置合适的尺寸
    zoomOutSvg.setAttribute("height", "20")
    zoomOutSvg.setAttribute("version", "1.1")
    zoomOutSvg.style.fill = "white" // 设置颜色
    const zoomOutPath = document.createElementNS("http://www.w3.org/2000/svg", "path")
    zoomOutPath.setAttribute('d', 'M463.238095 146.285714c175.055238 0 316.952381 141.897143 316.952381 316.952381 0 77.775238-28.038095 149.040762-74.532571 204.214857l188.440381 194.535619-55.247238 57.002667-191.536762-197.705143A315.489524 315.489524 0 0 1 463.238095 780.190476c-175.055238 0-316.952381-141.897143-316.952381-316.952381S288.182857 146.285714 463.238095 146.285714z m0 73.142857C328.582095 219.428571 219.428571 328.582095 219.428571 463.238095s109.153524 243.809524 243.809524 243.809524a242.883048 242.883048 0 0 0 161.889524-61.513143l25.551238-26.355809A242.834286 242.834286 0 0 0 707.047619 463.238095c0-134.656-109.153524-243.809524-243.809524-243.809524z m152.210286 219.428572v73.142857H316.952381v-73.142857h298.496z')
    zoomOutSvg.append(zoomOutPath)
    zoomOutButton.onclick = function () {
        // 缩小逻辑
        let currentScale = Number(svgElement.getAttribute('data-scale') || 1)
        let newScale = Math.max(0.1, currentScale - 0.1)
        svgElement.style.transform = `scale(${newScale})`
        svgElement.setAttribute('data-scale', newScale.toString())
    }
    zoomOutButton.appendChild(zoomOutSvg)

    let resetButton = document.createElement("button")
    let resetSvg = document.createElementNS("http://www.w3.org/2000/svg", "svg")
    resetSvg.setAttribute("viewBox", "0 0 1024 1024")
    resetSvg.setAttribute("width", "16") // 设置合适的尺寸
    resetSvg.setAttribute("height", "16")
    resetSvg.setAttribute("version", "1.1")
    resetSvg.style.fill = "white" // 设置颜色
    const resetPath = document.createElementNS("http://www.w3.org/2000/svg", "path")
    resetPath.setAttribute('d', 'M512 950.86c-210.65 0-386.92-149.21-429.35-347.43H190.9L74.61 486.4 8.78 420.57C2.92 449.83 0 480.55 0 512s2.92 62.17 8.78 91.43C51.2 842.6 260.39 1024 512 1024c208.46 0 386.92-123.61 466.65-302.08l-55.59-55.59C860.16 832.37 699.98 950.86 512 950.86zM1015.22 420.57C972.8 181.39 763.61 0 512 0 303.54 0 125.08 123.61 45.35 302.08l55.59 56.32C163.11 192.37 324.02 73.14 512 73.14c210.65 0 386.92 149.21 429.35 347.43H833.1l116.29 116.29 65.83 65.83c5.85-29.26 8.78-59.25 8.78-90.7s-2.92-62.16-8.78-91.42z')

    resetSvg.append(resetPath)
    resetButton.appendChild(resetSvg)
    resetButton.onclick = function () {
        // 重置逻辑
        svgElement.style.transform = `scale(1)`
        svgElement.setAttribute('data-scale', '1')
    }

    // 这三个按钮包裹在一个div,这个div绝对定位，使用flex,元素间距为10
    let div = document.createElement("div")
    div.style.position = "absolute"
    div.style.top = "10px"
    div.style.left = "10px"
    div.style.display = "flex"
    div.style.gap = "10px"
    div.style.flexDirection = "row"
    div.style.alignItems = "center"
    div.appendChild(zoomInButton)
    div.appendChild(zoomOutButton)
    div.appendChild(resetButton)
    return div
}

