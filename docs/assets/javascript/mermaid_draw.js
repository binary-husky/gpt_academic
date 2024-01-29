var mermaidConfig = {
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
    old_mermaid_div = parentCodeElement.querySelector('.mermaid_render');
    if (old_mermaid_div) {
        old_mermaid_div.outerHTML = mermaid_div.outerHTML;
    } else {
        parentCodeElement.appendChild(mermaid_div)
    }
    let codeFinishRenderElement = parentCodeElement.querySelector("code_finish_render");
    if (codeFinishRenderElement) {        // 如果block下已存在code_already_rendered元素
        codeFinishRenderElement.style.display = "none";
        codeFinishRenderElement.textContent = codeContent;
    } else {
        // 如果不存在code_finish_render元素，则将code元素中的内容添加到新创建的code_finish_render元素中
        let codeFinishRenderElement = document.createElement("code_finish_render"); // 创建一个新的code_already_rendered元素
        codeFinishRenderElement.style.display = "none";
        codeFinishRenderElement.textContent = codeContent;
        parentCodeElement.appendChild(codeFinishRenderElementNew); // 将新创建的code_already_rendered元素添加到block中
    }
    console.log('mermaid render success')
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
            let finish_render= parentCodeElement.querySelector("code_finish_render")
            if (finish_render) {
                await do_render(parentCodeElement, finish_render.textContent)
            }
            var error_elements = document.querySelector('[id^="d_diagram"]');
            if (error_elements) {
                error_elements.remove()
            }
        }
    }

}

// 创建MutationObserver对象
const chatbotObserverMsg = new MutationObserver(function (mutationsList, observer) {
    if (chatbotMsg) {
        chatbotMsg.querySelectorAll('.bot .language-mermaid').forEach(mermaidCodeAdd)
    }
});


function svgInitPz(svgElement) {
    let svg_width = svgElement.width.animVal.value;
    let svg_height =  svgElement.height.animVal.value;
    let init_params = {
        zoomEnabled: true,
        controlIconsEnabled: true,
    };
    svgElement.style = `width: ${svg_width}px; height: ${svg_height}px;`;
    window.panZoomTiger = svgPanZoom(svgElement, init_params);
}
