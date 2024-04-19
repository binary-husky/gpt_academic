
// i18n

const language = navigator.language.slice(0,2);

var forView_i18n;
var deleteConfirm_i18n_pref;
var deleteConfirm_i18n_suff;
var usingLatest_i18n;
var updatingMsg_i18n;
var updateSuccess_i18n;
var updateFailure_i18n;
var regenerate_i18n;
var deleteRound_i18n;
var renameChat_i18n;
var validFileName_i18n;

function setLoclize() {
    forView_i18n = gradioApp().querySelector('#forView_i18n').innerText;
    deleteConfirm_i18n_pref = gradioApp().querySelector('#deleteConfirm_i18n_pref').innerText;
    deleteConfirm_i18n_suff = gradioApp().querySelector('#deleteConfirm_i18n_suff').innerText;
    usingLatest_i18n = gradioApp().querySelector('#usingLatest_i18n').innerText;
    updatingMsg_i18n = gradioApp().querySelector('#updatingMsg_i18n').innerText;
    updateSuccess_i18n = gradioApp().querySelector('#updateSuccess_i18n').innerText;
    updateFailure_i18n = gradioApp().querySelector('#updateFailure_i18n').innerText;
    regenerate_i18n = gradioApp().querySelector('#regenerate_i18n').innerText;
    deleteRound_i18n = gradioApp().querySelector('#deleteRound_i18n').innerText;
    renameChat_i18n = gradioApp().querySelector('#renameChat_i18n').innerText;
    validFileName_i18n = gradioApp().querySelector('#validFileName_i18n').innerText;
}

function i18n(msg) {
    return msg;
    // return msg.hasOwnProperty(language) ? msg[language] : msg['en'];
}
