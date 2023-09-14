
var updateInfoGotten = false;
var isLatestVersion = localStorage.getItem('isLatestVersion') || false;

function setUpdater() {
    const enableCheckUpdate = gradioApp().querySelector('#enableCheckUpdate_config').innerText;

    if (enableCheckUpdate == "False" || enableCheckUpdate == "false") {
        gradioApp().classList.add('disable-update');
        return;
    }

    const lastCheckTime = localStorage.getItem('lastCheckTime') || 0;
    const longTimeNoCheck = currentTime - lastCheckTime > 3 * 24 * 60 * 60 * 1000;
    if (longTimeNoCheck && !updateInfoGotten && !isLatestVersion || isLatestVersion && !updateInfoGotten) {
        updateLatestVersion();
    }
}

var statusObserver = new MutationObserver(function (mutationsList) {
    for (const mutation of mutationsList) {
        if (mutation.type === 'attributes' || mutation.type === 'childList') {
            if (statusDisplay.innerHTML.includes('<span id="update-status"')) {
                if (getUpdateStatus() === "success") {
                    updatingInfoElement.innerText = i18n(updateSuccess_i18n);
                    noUpdateHtml();
                    localStorage.setItem('isLatestVersion', 'true');
                    isLatestVersion = true;
                    enableUpdateBtns();
                } else if (getUpdateStatus() === "failure") {
                    updatingInfoElement.innerHTML = i18n(updateFailure_i18n);
                    disableUpdateBtn_enableCancelBtn();
                } else if (getUpdateStatus() != "") {
                    updatingInfoElement.innerText = getUpdateStatus();
                    enableUpdateBtns();
                }
                updateStatus.parentNode.removeChild(updateStatus);
                if (updateSpinner) updateSpinner.stop();
            }
        }
    }
});

var showingUpdateInfo = false;
async function getLatestRelease() {
    try {
        const response = await fetch('https://api.github.com/repos/gaizhenbiao/chuanhuchatgpt/releases/latest');
        if (!response.ok) {
            console.log(`Error: ${response.status} - ${response.statusText}`);
            updateInfoGotten = true;
            return null;
        }
        const data = await response.json();
        updateInfoGotten = true;
        return data;
    } catch (error) {
        console.log(`Error: ${error}`);
        updateInfoGotten = true;
        return null;
    }
}

var releaseNoteElement = document.getElementById('release-note-content');
var updatingInfoElement = document.getElementById('updating-info');
async function updateLatestVersion() {
    const currentVersionElement = document.getElementById('current-version');
    const reVersion = /<a[^>]*>([^<]*)<\/a>/g;
    const versionMatch = reVersion.exec(currentVersionElement.innerHTML);
    const currentVersion = (versionMatch && versionMatch[1].length == 8) ? versionMatch[1] : null;
    const latestVersionElement = document.getElementById('latest-version-title');
    const versionInfoElement = document.getElementById('version-info-title');
    releaseNoteElement = document.getElementById('release-note-content');
    updatingInfoElement = document.getElementById('updating-info');
    
    const versionTime = document.getElementById('version-time').innerText;
    const localVersionTime = versionTime !== "unknown" ? (new Date(versionTime)).getTime() : 0;
    disableUpdateBtns();
    updateInfoGotten = true; //无论成功与否都只执行一次，否则容易api超限...
    try {
        const data = await getLatestRelease();
        const releaseNote = data.body;
        if (releaseNote) {
            releaseNoteElement.innerHTML = marked.parse(releaseNote, {mangle: false, headerIds: false});
        }
        const latestVersion = data.tag_name;
        if (currentVersion) {
            if (latestVersion <= currentVersion) {
                noUpdate();
            } else {
                latestVersionElement.textContent = latestVersion;
                console.log(`New version ${latestVersion} found!`);
                if (!isInIframe) openUpdateToast();
                gradioApp().classList.add('is-outdated');
            }
            enableUpdateBtns();
        } else { //如果当前版本号获取失败，使用时间比较
            const latestVersionTime = (new Date(data.created_at)).getTime();
            if (latestVersionTime) {
                const latestVersionInfo = `<a href="https://github.com/gaizhenbiao/chuanhuchatgpt/releases/latest" target="_blank" id="latest-version-title" style="text-decoration: none;">${latestVersion}</a>`
                const manualUpdateInfo = `<a href="https://github.com/GaiZhenbiao/ChuanhuChatGPT/wiki/使用教程#手动更新" target="_blanks" style="text-decoration: none;">manual update</a>`
                if (localVersionTime == 0) {
                    const infoMessage = `Local version check failed. \nBut latest revision is ${latestVersionInfo}. \n\nWhen Update needed, \n- If you are using Docker, try to update package. \n- If you didn't use git, try ${manualUpdateInfo}.`
                    versionInfoElement.innerHTML = marked.parse(infoMessage, {mangle: false, headerIds: false});
                    console.log(`New version ${latestVersion} found!`);
                    disableUpdateBtn_enableCancelBtn();
                    localStorage.setItem('isLatestVersion', 'false');
                    isLatestVersion = false;
                    gradioApp().classList.add('is-outdated');
                } else if (localVersionTime < latestVersionTime) {
                    const infoMessage = `Local version check failed, it seems to be a local rivision. \n\nBut latest revision is ${latestVersionInfo}. Try ${manualUpdateInfo}.`
                    versionInfoElement.innerHTML = marked.parse(infoMessage, {mangle: false, headerIds: false});
                    console.log(`New version ${latestVersion} found!`);
                    disableUpdateBtn_enableCancelBtn();
                    // if (!isInIframe) openUpdateToast();
                    localStorage.setItem('isLatestVersion', 'false');
                    isLatestVersion = false;
                    gradioApp().classList.add('is-outdated');
                } else {
                    noUpdate("Local version check failed, it seems to be a local rivision. <br>But your revision is newer than the latest release.");
                    gradioApp().classList.add('is-outdated');
                }
            }
        }
        currentTime = new Date().getTime();
        localStorage.setItem('lastCheckTime', currentTime);
        disableUpdateBtn_enableCancelBtn()
    } catch (error) {
        console.error(error);
        disableUpdateBtn_enableCancelBtn()
    }
}

function getUpdateInfo() {
    window.open('https://github.com/gaizhenbiao/chuanhuchatgpt/releases/latest', '_blank');
    closeUpdateToast();
}

var updateSpinner = null;

function bgUpdateChuanhu() {
    updateChuanhuBtn.click();
    updatingInfoElement.innerText = i18n(updatingMsg_i18n);
    var updatingSpinner = document.getElementById('updating-spinner');
    try {
        updateSpinner = new Spin.Spinner({color:'#06AE56',top:'45%',lines:9}).spin(updatingSpinner);
    } catch (error) {
        console.error("Can't create spinner")
    }
    updatingInfoElement.classList.remove('hideK');
    disableUpdateBtns();
    const releaseNoteWrap = document.getElementById('release-note-wrap');
    releaseNoteWrap.style.setProperty('display', 'none');
    statusObserver.observe(statusDisplay, { childList: true, subtree: true, characterData: true});
}
function cancelUpdate() {
    closeUpdateToast();
}
function openUpdateToast() {
    showingUpdateInfo = true;
    updateToast.style.setProperty('top', '0px');
    showMask("update-toast");
}
function closeUpdateToast() {
    updateToast.style.setProperty('top', '-600px');
    showingUpdateInfo = false;
    if (updatingInfoElement.classList.contains('hideK') === false) {
        updatingInfoElement.classList.add('hideK');
    }
    document.querySelector('.chuanhu-mask')?.remove();
}
function manualCheckUpdate() {
    openUpdateToast();
    updateLatestVersion();
    currentTime = new Date().getTime();
    localStorage.setItem('lastCheckTime', currentTime);
}
function noUpdate(message="") {
    localStorage.setItem('isLatestVersion', 'true');
    isLatestVersion = true;
    noUpdateHtml(message);
}
function noUpdateHtml(message="") {
    const versionInfoElement = document.getElementById('version-info-title');
    const gotoUpdateBtn = document.getElementById('goto-update-btn');
    const closeUpdateBtn = document.getElementById('close-update-btn');
    const releaseNoteWrap = document.getElementById('release-note-wrap');
    releaseNoteWrap.style.setProperty('display', 'none');
    if (message === "") {
        versionInfoElement.textContent = i18n(usingLatest_i18n)
    } else {
        versionInfoElement.innerHTML = message;
    }
    gotoUpdateBtn.classList.add('hideK');
    closeUpdateBtn.classList.remove('hideK');
}

var updateStatus = null;
function getUpdateStatus() {
    updateStatus = statusDisplay.querySelector("#update-status");
    if (updateStatus) {
        return updateStatus.innerText;
    } else {
        return "unknown";
    }
}

function disableUpdateBtns() {
    const updatesButtons = document.querySelectorAll('.btn-update');
    updatesButtons.forEach( function (btn) {
        btn.disabled = true;
    });
}
function enableUpdateBtns() {
    const updatesButtons = document.querySelectorAll('.btn-update');
    updatesButtons.forEach( function (btn) {
        btn.disabled = false;
    });
}
function disableUpdateBtn_enableCancelBtn() {
    document.querySelector('#update-button.btn-update').disabled = true;
    document.querySelector('#cancel-button.btn-update').disabled = false;
}

// function setUpdateWindowHeight() {
//     if (!showingUpdateInfo) {return;}
//     const scrollPosition = window.scrollY;
//     // const originalTop = updateToast.style.getPropertyValue('top');
//     const resultTop = scrollPosition - 20 + 'px';
//     updateToast.style.setProperty('top', resultTop);
// }
