
// var userLogged = false;
var usernameGotten = false;
var usernameTmp = null;
var username = null;


function getUserInfo() {
    if (usernameGotten) {
        return;
    }
    // userLogged = localStorage.getItem('userLogged');
    // if (userLogged) {
    usernameTmp = userInfoDiv.innerText;
    if (usernameTmp) {
        if (usernameTmp.includes("getting user info")) {
            setTimeout(getUserInfo, 500);
            return;
        } else if (usernameTmp === " ") {
            localStorage.removeItem("username");
            // localStorage.removeItem("userLogged")
            // userLogged = false;
            usernameGotten = true;
            return;
        } else {
            usernameTmp = usernameTmp.match(/User:\s*(.*)/)[1] || usernameTmp;
            localStorage.setItem("username", usernameTmp);
            username = usernameTmp;
            usernameGotten = true;
            clearHistoryHtml();
        }
    }
    // }
}

function showOrHideUserInfo() {
    function toggleUserInfoVisibility(shouldHide) {
        if (userInfoDiv) {
            if (shouldHide) {
                userInfoDiv.classList.add("info-transparent");
            } else {
                userInfoDiv.classList.remove("info-transparent");
            }
        }
    }

    // When webpage loaded, hide user info after 2 second
    setTimeout(function () {
        toggleUserInfoVisibility(true);
    }, 2000);

    // let triggerElements = {appTitleDiv, userInfoDiv, sendBtn};
    let triggerElements = {userInfoDiv, statusDisplay};
    for (let elem in triggerElements) {
        triggerElements[elem].addEventListener("mouseenter", function () {
            toggleUserInfoVisibility(false);
        });
        triggerElements[elem].addEventListener("mouseleave", function () {
            toggleUserInfoVisibility(true);
        });
        triggerElements[elem].ontouchstart = function () {
            toggleUserInfoVisibility(false);
        };
        triggerElements[elem].ontouchend = function () {
            setTimeout(function () {
                toggleUserInfoVisibility(true);
            }, 3000);
        };
    }
}
