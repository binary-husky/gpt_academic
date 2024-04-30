async function toastConvert2Img() {
    let pElement = statusDisplay.querySelector('p');
    pElement.innerHTML = '🏃🏻‍正在将对话记录转换为图片，请稍等';
    toast_push('🏃🏻‍正正在将对话记录转换为图片', 2000);
    await convert2canvas(null, pElement)
}

async function convert2canvas(shareContent = null, pElement) {
    if (shareContent == null) {
        shareContent = chatbot.querySelector('.message-wrap') //获取囊括所有元素的最大的div元素
    }
    let width = shareContent.scrollWidth * 2; //获取dom宽度（包括元素宽度、内边距和边框，不包括外边距）
    let height = shareContent.scrollHeight * 2; //获取dom高度（包括元素高度、内边距和边框，不包括外边距）
    let canvas = document.createElement("canvas"); //创建一个canvas标签元素
    let scale = 2; //定义放大倍数，可以支持小数
    let imgType = "image/png";//设置默认下载的图片格式

    canvas.width = width * scale; //定义canvas宽度 * 倍数（图片的清晰度优化），默认宽度为300px
    canvas.height = height * scale; //定义canvas高度 * 倍数，默认高度为150px
    canvas.getContext("2d").scale(scale, scale); //创建canvas的context对象，设置scale，相当于画布的“画笔”拥有多种绘制路径、矩形、圆形、字符以及添加图像的方法

    let backgroundColor = window.getComputedStyle(chatbot).backgroundColor;

    let opts = { //初始化对象
        backgroundColor: backgroundColor,//设置canvas背景为透明
        scale: scale, //添加的scale参数
        canvas: canvas, //自定义canvas
        logging: true, //日志开关，便于查看html2canvas的内部执行流程
        width: width, //dom的原始宽度和高度
        height: height,
        useCORS: true, //开启html2canvas的useCORS配置，跨域配置，以解决图片跨域的问题
        x: 0,              // 确保从左上角开始绘制，防止偏移
        y: 0               // 同样，确保从顶端开始绘制
    };
    html2canvas(shareContent, opts).then(function (canvas) {
        let context = canvas.getContext('2d');
        // 在放大倍数作用以前设置背景色
        // 【重要】关闭抗锯齿，进一步优化清晰度
        context.mozImageSmoothingEnabled = false;
        context.webkitImageSmoothingEnabled = false;
        context.msImageSmoothingEnabled = false;
        context.imageSmoothingEnabled = false;

        let img = Canvas2image.convertToImage(canvas, canvas.width, canvas.height, imgType); //将绘制好的画布转换为img标签,默认图片格式为PNG.
        // document.body.appendChild(img); //在body元素后追加的图片元素至页面，也可以不追加，直接做处理

        $(img).css({ //设置图片元素的宽高属性
            "width": canvas.width / 2 + "px",
            "height": canvas.height / 2 + "px",
        })
        $(img).attr("id", "img1"); //为图片元素添加id属性
        // 将已有<p>标签中原来的内容清空，并插入我们新创建的<a>元素
        copyToClipboard(img);  // 将图片复制到剪切板
        pElement.innerHTML = '';         // 先清空<p>标签内的所有内容
        pElement.appendChild(createALink(img));  // 然后将<a>标签添加进去
    });
    return pElement.outerHTML;
}

function copyToClipboard(image) {
    // 尝试使用 Clipboard API 写入剪切板
    if (navigator.clipboard && window.isSecureContext) {
        // 将image转换成Blob对象
        fetch(image.src)
            .then(res => res.blob())
            .then(blob => {
                // Write the blob image to clipboard
                navigator.clipboard.write([new ClipboardItem({'image/png': blob})])
                    .then(() => console.log('Image copied!'))
                    .catch(err => console.error('Could not copy image: ', err));
            });
    } else {
        console.error('The Clipboard API is not available.');
    }
}

function get_history_name(){
    let history_select = historySelector.querySelector('.chat-selected-btns').parentElement
    return history_select.querySelector('input').value.replace(/\s/g, '')
}


function createALink(img) {
    // 生成一个a超链接元素
    let linkElement = document.createElement('a');
    // 将a的download属性设置为我们想要下载的图片名称，若name不存在则使用‘下载图片名称’作为默认名称
    history_value = get_history_name()
    linkElement.download = history_value + '.png';
    linkElement.innerHTML = history_value + '.png'
    linkElement.href = img.src;//将img的src值设置为a.href属性，img.src为base64编码值
    return linkElement
}
