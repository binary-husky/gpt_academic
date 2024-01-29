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
    if (parentCodeElement.querySelector('.mermaid_render')) {
        parentCodeElement.querySelector('.mermaid_render').outerHTML = mermaid_div.outerHTML;
    } else {
        parentCodeElement.appendChild(mermaid_div);
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
    console.log('mermaidReplaceOld', codeFinishRenderElement)
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
    let foreign = svgElement.querySelector('foreignObject')
    if (!foreign) {
        let svg_width = svgElement.width.animVal.value;
        let svg_height = svgElement.height.animVal.value;
        svg_height = svg_height < 200 ? 200 : svg_height;  // 最低200
        let init_params = {
            zoomEnabled: true,
            controlIconsEnabled: true,
        };
        svgElement.style = `width: ${svg_width}px; height: ${svg_height}px;`;
        window.panZoomTiger = svgPanZoom(svgElement, init_params);
        let pako_encode_link = await pako_encode(content)
        let fore_btn = await createForeignObject(svg_width, svgEditIcon, pako_encode_link)
        if (foreign) {
            svgElement.outerHTML = fore_btn.outerHTML
        } else {
           svgElement.appendChild(fore_btn)
        }
        console.log(svgElement)
    }
}


async function createForeignObject(svg_width, svgIcon, link) {
    // 创建 <foreignObject> 元素
    let foreignObject = document.createElementNS("http://www.w3.org/2000/svg", "foreignObject");
    foreignObject.setAttribute("x", `${svg_width - 45}`);
    foreignObject.setAttribute("y", "10");
    foreignObject.setAttribute("width", "20");
    foreignObject.setAttribute("height", "20");
    // 添加编辑图标到 <foreignObject>
    foreignObject.innerHTML = `
       <button onclick="window.open('${link}', '_blank')">${svgIcon}</button>
        `;
    return foreignObject
}

var svgEditIcon = `
<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-pencil-square" viewBox="0 0 16 16">
  <path d="M15.502 1.94a.5.5 0 0 1 0 .706L14.459 3.69l-2-2L13.502.646a.5.5 0 0 1 .707 0l1.293 1.293zm-1.75 2.456-2-2L4.939 9.21a.5.5 0 0 0-.121.196l-.805 2.414a.25.25 0 0 0 .316.316l2.414-.805a.5.5 0 0 0 .196-.12l6.813-6.814z"/>
  <path fill-rule="evenodd" d="M1 13.5A1.5 1.5 0 0 0 2.5 15h11a1.5 1.5 0 0 0 1.5-1.5v-6a.5.5 0 0 0-1 0v6a.5.5 0 0 1-.5.5h-11a.5.5 0 0 1-.5-.5v-11a.5.5 0 0 1 .5-.5H9a.5.5 0 0 0 0-1H2.5A1.5 1.5 0 0 0 1 2.5z"/>
</svg>
`