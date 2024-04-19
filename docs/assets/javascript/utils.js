

function isImgUrl(url) {
    const imageExtensions = /\.(jpg|jpeg|png|gif|bmp|webp)$/i;
    if (url.startsWith('data:image/')) {
        return true;
    }
    if (url.match(imageExtensions)) {
        return true;
    }
    if (url.startsWith('http://') || url.startsWith('https://')) {
        return true;
    }

    return false;
}

function downloadHistory(gradioUsername, historyname, format=".json") {
    let fileUrl;
    if (gradioUsername === null || gradioUsername.trim() === "") {
        fileUrl = `/file=./history/${historyname}`;
    } else {
        fileUrl = `/file=./history/${gradioUsername}/${historyname}`;
    }
    downloadFile(fileUrl, historyname, format);
}

function downloadFile(fileUrl, filename = "", format = "", retryTimeout = 200, maxAttempts = 10) {

    fileUrl = fileUrl + format;
    filename = filename + format;

    let attempts = 0;

    async function tryDownload() {
        if (attempts >= maxAttempts) {
            console.error('Max attempts reached, download failed.');
            alert('Download failed:' + filename);
            return;
        }
        try {
            const response = await fetch(fileUrl);
            if (!response.ok) {
                attempts++;
                console.error("Error fetching file, retrying...");
                setTimeout(tryDownload, retryTimeout);
            } else {
                response.blob()
                    .then(blob => {
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.style.display = 'none';
                        a.href = url;
                        a.download = filename;
                        document.body.appendChild(a);
                        a.click();
                        URL.revokeObjectURL(url);
                        document.body.removeChild(a);
                    })
                    .catch(error => {
                        console.error('Error downloading file:', error);
                    });
            }
        } catch (error) {
            attempts++;
            setTimeout(tryDownload, retryTimeout);
        }
    }

    tryDownload();
}
    


/* NOTE: These reload functions are not used in the current version of the code.
 *       From stable-diffusion-webui
 */
function restart_reload() {
    document.body.innerHTML = '<h1 style="font-family:ui-monospace,monospace;margin-top:20%;color:lightgray;text-align:center;">Reloading...</h1>';

    var requestPing = function () {
        requestGet("./internal/ping", {}, function (data) {
            location.reload();
        }, function () {
            setTimeout(requestPing, 500);
        });
    };

    setTimeout(requestPing, 2000);

    return [];
}

function requestGet(url, data, handler, errorHandler) {
    var xhr = new XMLHttpRequest();
    var args = Object.keys(data).map(function (k) {
        return encodeURIComponent(k) + '=' + encodeURIComponent(data[k]);
    }).join('&');
    xhr.open("GET", url + "?" + args, true);

    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                try {
                    var js = JSON.parse(xhr.responseText);
                    handler(js);
                } catch (error) {
                    console.error(error);
                    errorHandler();
                }
            } else {
                errorHandler();
            }
        }
    };
    var js = JSON.stringify(data);
    xhr.send(js);
}
