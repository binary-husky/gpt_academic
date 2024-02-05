const mermaidConfig = {
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
const svg_init_params = {
    zoomEnabled: true,
    controlIconsEnabled: true,
    mouseWheelZoomEnabled: false
};

function getRandomInt(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min + 1)) + min;
}


async function do_render(parentCodeElement, codeContent) {
    let mermaid_div = document.createElement('div');
    let diagram = await mermaid.render(`_diagram_${getRandomInt(1000, 9999)}`, codeContent);
    mermaid_div.classList.add('mermaid_render');
    mermaid_div.innerHTML = diagram.svg;
    let chatbot_top = chatbotWrap.scrollTop
    if (parentCodeElement.querySelector('.mermaid_render')) {
        parentCodeElement.querySelector('.mermaid_render').outerHTML = mermaid_div.outerHTML;
    } else {
        parentCodeElement.appendChild(mermaid_div);
    }
    if (chatbotWrap.scrollTop - chatbot_top < 500) {
        // 避免重复滚动
        chatbotWrap.scrollTop = chatbotWrap.scrollHeight - chatbotWrap.clientHeight;
    }
    let codeFinishRenderElement = chatbot.querySelector("code_finish_render");
    if (codeFinishRenderElement) {        // 如果block下已存在code_already_rendered元素
        codeFinishRenderElement.style.display = "none";
        codeFinishRenderElement.innerHTML = diagram.svg;
    } else {
        // 如果不存在code_finish_render元素，则将code元素中的内容添加到新创建的code_finish_render元素中
        let codeFinishRenderElement = document.createElement("code_finish_render"); // 创建一个新的code_already_rendered元素
        codeFinishRenderElement.style.display = "none";
        codeFinishRenderElement.innerHTML = diagram.svg;
        chatbot.appendChild(codeFinishRenderElement); // 将新创建的code_already_rendered元素添加到block中
    }
    console.log('mermaid render success')
}

async function mermaidReplaceOld(parentCodeElement) {
    let old_mermaid_div = document.createElement('div');
    old_mermaid_div.classList.add('mermaid_render');
    let codeFinishRenderElement = chatbot.querySelector("code_finish_render svg");
    // console.log('mermaidReplaceOld', codeFinishRenderElement)
    if (codeFinishRenderElement) {
        old_mermaid_div.innerHTML = codeFinishRenderElement.outerHTML;
    }
    parentCodeElement.appendChild(old_mermaid_div);
}

async function mermaidCodeAdd(codeElement) {
    let parentCodeElement = codeElement.parentElement.parentElement
    let old_mermaid_div = parentCodeElement.querySelector('.mermaid_render');
    if (!old_mermaid_div) {
        mermaid.initialize(mermaidConfig);
        // 获取bot_mermaid的值
        let bot_mermaid_content = codeElement.textContent || codeElement.innerText;
        try {
            await do_render(parentCodeElement, bot_mermaid_content)
        } catch (e) {
            let finish_render = chatbot.querySelector("code_finish_render")
            if (finish_render) {
                await mermaidReplaceOld(parentCodeElement)
            }
            var error_elements = document.querySelector('[id^="d_diagram"]');
            if (error_elements) {
                error_elements.remove()
            }
        }
    }

}

async function mermaidEditAdd(codeElement) {
    let parentCodeElement = codeElement.parentElement.parentElement
    let old_mermaid_svg = parentCodeElement.querySelector('.mermaid_render svg');
    if (old_mermaid_svg) {
        await svgInitPz(old_mermaid_svg, codeElement.textContent)
    }
}


// 创建MutationObserver对象
const chatbotObserverMsg = new MutationObserver(function (mutationsList, observer) {
    if (chatbotMsg) {
        chatbotMsg.querySelectorAll('.bot .language-mermaid').forEach(mermaidCodeAdd)
    }
});

async function pako_encode(codeContent) {
    const Module = await import('./mermaid_editor.mjs');
    let pako_encode = Module.serializeState({
        "code": codeContent,
        "mermaid": "{\n  \"theme\": \"default\"\n}",
        "autoSync": true,
        "updateDiagram": false
    })
    return "https://mermaid.live/edit#" + pako_encode
}


async function svgInitPz(svgElement, content) {
    if (!svgElement.querySelector('foreignObject')) {
        let svg_width = '100%';
        let svg_height = svgElement.height.animVal.value;
        svg_height = svg_height < 200 ? 200 : svg_height;  // 最低200
        svgElement.style = `width: ${svg_width}px; height: ${svg_height}px;`;
        let panZoomTiger = svgPanZoom(svgElement, svg_init_params);
        let pako_encode_link = await pako_encode(content)
        if (!svgElement.querySelector('#foreign-edit')) {
            // 增加编辑按钮
            let fore_edit_btn = await createForeignObject()
            fore_edit_btn.innerHTML = `<button id="foreign-edit" 
                                        onclick="window.open('${pako_encode_link}', '_blank')">${svgEditIcon}</button>`
            svgElement.appendChild(fore_edit_btn)
        }
        addClickEvent(svgElement, panZoomTiger)
    }
}

function addClickEvent(svgElement, panZoomTiger) {
    // 支持双击选择SVG文本
    let svgTextEle = svgElement.querySelectorAll('text')
    for (let i = 0; i < svgTextEle.length; i++) {
// 监听鼠标悬停事件
        svgTextEle[i].addEventListener('mouseover', function (e) {
            // 当鼠标悬停时禁用双击缩放功能
            panZoomTiger.disableDblClickZoom();
            // 当鼠标悬停时禁用平移功能
            panZoomTiger.disablePan();
            // 当鼠标悬停时启用鼠标滚轮缩放功能
            panZoomTiger.enableMouseWheelZoom();
        });
        svgTextEle[i].addEventListener('mouseout', function (e) {
            // 当鼠标移出时启用双击缩放功能
            panZoomTiger.enableDblClickZoom();
            // 当鼠标移出时启用平移功能
            panZoomTiger.enablePan();
            // 当鼠标移出时禁用鼠标滚轮缩放功能
            panZoomTiger.disableMouseWheelZoom();
        });
        svgTextEle[i].addEventListener('dblclick', function (e) {
            // 双击选中文本内容
            let range = document.createRange();
            range.selectNodeContents(svgTextEle[i]);
            let sel = window.getSelection();
            sel.removeAllRanges();
            sel.addRange(range);
        });
        // console.log(svgElement)
    }
    svgElement.addEventListener('click', function (e) {
        // 如果点击的不是 svgTextEle 元素则移出选择
        if (!e.target.closest('svg text')) {
            let sel = window.getSelection ? window.getSelection() : document.selection;
            if (sel) {
                if (sel.removeAllRanges) {
                    sel.removeAllRanges();
                } else if (sel.empty) {  // IE 浏览器
                    sel.empty();
                }
            }
        }
    });
}

async function createForeignObject(x = `94%`, y = "10") {
    // 创建 <foreignObject> 元素
    let foreignObject = document.createElementNS("http://www.w3.org/2000/svg",
        "foreignObject");
    foreignObject.setAttribute("x", x);
    foreignObject.setAttribute("y", y);
    foreignObject.setAttribute("width", "20");
    foreignObject.setAttribute("height", "20");
    return foreignObject
}

const svgEditIcon = `
<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-pencil-square" viewBox="0 0 16 16">
  <path d="M15.502 1.94a.5.5 0 0 1 0 .706L14.459 3.69l-2-2L13.502.646a.5.5 0 0 1 .707 0l1.293 1.293zm-1.75 2.456-2-2L4.939 9.21a.5.5 0 0 0-.121.196l-.805 2.414a.25.25 0 0 0 .316.316l2.414-.805a.5.5 0 0 0 .196-.12l6.813-6.814z"/>
  <path fill-rule="evenodd" d="M1 13.5A1.5 1.5 0 0 0 2.5 15h11a1.5 1.5 0 0 0 1.5-1.5v-6a.5.5 0 0 0-1 0v6a.5.5 0 0 1-.5.5h-11a.5.5 0 0 1-.5-.5v-11a.5.5 0 0 1 .5-.5H9a.5.5 0 0 0 0-1H2.5A1.5 1.5 0 0 0 1 2.5z"/>
</svg>
`