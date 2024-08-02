// -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
//  TTS语音生成函数
// -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
audio_debug = false;
class AudioPlayer {
    constructor() {
        this.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        this.queue = [];
        this.isPlaying = false;
        this.currentSource = null; // 添加属性来保存当前播放的源
    }

    // Base64 编码的字符串转换为 ArrayBuffer
    base64ToArrayBuffer(base64) {
        const binaryString = window.atob(base64);
        const len = binaryString.length;
        const bytes = new Uint8Array(len);
        for (let i = 0; i < len; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }
        return bytes.buffer;
    }

    // 检查音频播放队列并播放音频
    checkQueue() {
        if (!this.isPlaying && this.queue.length > 0) {
            this.isPlaying = true;
            const nextAudio = this.queue.shift();
            this.play_wave(nextAudio);
        }
    }

    // 将音频添加到播放队列
    enqueueAudio(audio_buf_wave) {
        if (allow_auto_read_tts_flag) {
            this.queue.push(audio_buf_wave);
            this.checkQueue();
        }
    }

    // 播放音频
    async play_wave(encodedAudio) {
        //const audioData = this.base64ToArrayBuffer(encodedAudio);
        const audioData = encodedAudio;
        try {
            const buffer = await this.audioCtx.decodeAudioData(audioData);
            const source = this.audioCtx.createBufferSource();
            source.buffer = buffer;
            source.connect(this.audioCtx.destination);
            source.onended = () => {
                if (allow_auto_read_tts_flag) {
                    this.isPlaying = false;
                    this.currentSource = null; // 播放结束后清空当前源
                    this.checkQueue();
                }
            };
            this.currentSource = source; // 保存当前播放的源
            source.start();
        } catch (e) {
            console.log("Audio error!", e);
            this.isPlaying = false;
            this.currentSource = null; // 出错时也应清空当前源
            this.checkQueue();
        }
    }

    // 新增：立即停止播放音频的方法
    stop() {
        if (this.currentSource) {
            this.queue = []; // 清空队列
            this.currentSource.stop(); // 停止当前源
            this.currentSource = null; // 清空当前源
            this.isPlaying = false; // 更新播放状态
            // 关闭音频上下文可能会导致无法再次播放音频，因此仅停止当前源
            // this.audioCtx.close(); // 可选：如果需要可以关闭音频上下文
        }
    }
}

const audioPlayer = new AudioPlayer();

class FIFOLock {
    constructor() {
        this.queue = [];
        this.currentTaskExecuting = false;
    }

    lock() {
        let resolveLock;
        const lock = new Promise(resolve => {
            resolveLock = resolve;
        });

        this.queue.push(resolveLock);

        if (!this.currentTaskExecuting) {
            this._dequeueNext();
        }

        return lock;
    }

    _dequeueNext() {
        if (this.queue.length === 0) {
            this.currentTaskExecuting = false;
            return;
        }
        this.currentTaskExecuting = true;
        const resolveLock = this.queue.shift();
        resolveLock();
    }

    unlock() {
        this.currentTaskExecuting = false;
        this._dequeueNext();
    }
}








function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Define the trigger function with delay parameter T in milliseconds
function trigger(T, fire) {
    // Variable to keep track of the timer ID
    let timeoutID = null;
    // Variable to store the latest arguments
    let lastArgs = null;

    return function (...args) {
        // Update lastArgs with the latest arguments
        lastArgs = args;
        // Clear the existing timer if the function is called again
        if (timeoutID !== null) {
            clearTimeout(timeoutID);
        }
        // Set a new timer that calls the `fire` function with the latest arguments after T milliseconds
        timeoutID = setTimeout(() => {
            fire(...lastArgs);
        }, T);
    };
}


prev_text = ""; // previous text, this is used to check chat changes
prev_text_already_pushed = ""; // previous text already pushed to audio, this is used to check where we should continue to play audio
prev_chatbot_index = -1;
const delay_live_text_update = trigger(3000, on_live_stream_terminate);

function on_live_stream_terminate(latest_text) {
    // remove `prev_text_already_pushed` from `latest_text`
    if (audio_debug) console.log("on_live_stream_terminate", latest_text);
    remaining_text = latest_text.slice(prev_text_already_pushed.length);
    if ((!isEmptyOrWhitespaceOnly(remaining_text)) && remaining_text.length != 0) {
        prev_text_already_pushed = latest_text;
        push_text_to_audio(remaining_text);
    }
}
function is_continue_from_prev(text, prev_text) {
    abl = 5
    if (text.length < prev_text.length - abl) {
        return false;
    }
    if (prev_text.length > 10) {
        return text.startsWith(prev_text.slice(0, Math.min(prev_text.length - abl, 100)));
    } else {
        return text.startsWith(prev_text);
    }
}
function isEmptyOrWhitespaceOnly(remaining_text) {
    // Replace \n and 。 with empty strings
    let textWithoutSpecifiedCharacters = remaining_text.replace(/[\n。]/g, '');
    // Check if the remaining string is empty
    return textWithoutSpecifiedCharacters.trim().length === 0;
}
function process_increased_text(remaining_text) {
    // console.log('[is continue], remaining_text: ', remaining_text)
    // remaining_text starts with \n or 。, then move these chars into prev_text_already_pushed
    while (remaining_text.startsWith('\n') || remaining_text.startsWith('。')) {
        prev_text_already_pushed = prev_text_already_pushed + remaining_text[0];
        remaining_text = remaining_text.slice(1);
    }
    if (remaining_text.includes('\n') || remaining_text.includes('。')) { // determine remaining_text contain \n or 。
        // new message begin!
        index_of_last_sep = Math.max(remaining_text.lastIndexOf('\n'), remaining_text.lastIndexOf('。'));
        // break the text into two parts
        tobe_pushed = remaining_text.slice(0, index_of_last_sep + 1);
        prev_text_already_pushed = prev_text_already_pushed + tobe_pushed;
        // console.log('[is continue], push: ', tobe_pushed)
        // console.log('[is continue], update prev_text_already_pushed: ', prev_text_already_pushed)
        if (!isEmptyOrWhitespaceOnly(tobe_pushed)) {
            // console.log('[is continue], remaining_text is empty')
            push_text_to_audio(tobe_pushed);
        }
    }
}
function process_latest_text_output(text, chatbot_index) {
    if (text.length == 0) {
        prev_text = text;
        prev_text_mask = text;
        // console.log('empty text')
        return;
    }
    if (text == prev_text) {
        // console.log('[nothing changed]')
        return;
    }

    var is_continue = is_continue_from_prev(text, prev_text_already_pushed);
    if (chatbot_index == prev_chatbot_index && is_continue) {
        // on_text_continue_grow
        remaining_text = text.slice(prev_text_already_pushed.length);
        process_increased_text(remaining_text);
        delay_live_text_update(text); // in case of no \n or 。 in the text, this timer will finally commit
    }
    else if (chatbot_index == prev_chatbot_index && !is_continue) {
        if (audio_debug) console.log('---------------------');
        if (audio_debug) console.log('text twisting!');
        if (audio_debug) console.log('[new message begin]', 'text', text, 'prev_text_already_pushed', prev_text_already_pushed);
        if (audio_debug) console.log('---------------------');
        prev_text_already_pushed = "";
        delay_live_text_update(text); // in case of no \n or 。 in the text, this timer will finally commit
    }
    else {
        // on_new_message_begin, we have to clear `prev_text_already_pushed`
        if (audio_debug) console.log('---------------------');
        if (audio_debug) console.log('new message begin!');
        if (audio_debug) console.log('[new message begin]', 'text', text, 'prev_text_already_pushed', prev_text_already_pushed);
        if (audio_debug) console.log('---------------------');
        prev_text_already_pushed = "";
        process_increased_text(text);
        delay_live_text_update(text); // in case of no \n or 。 in the text, this timer will finally commit
    }
    prev_text = text;
    prev_chatbot_index = chatbot_index;
}

const audio_push_lock = new FIFOLock();
async function push_text_to_audio(text) {
    if (!allow_auto_read_tts_flag) {
        return;
    }
    await audio_push_lock.lock();
    var lines = text.split(/[\n。]/);
    for (const audio_buf_text of lines) {
        if (audio_buf_text) {
            // Append '/vits' to the current URL to form the target endpoint
            const url = `${window.location.href}vits`;
            // Define the payload to be sent in the POST request
            const payload = {
                text: audio_buf_text, // Ensure 'audio_buf_text' is defined with valid data
                text_language: "zh"
            };
            // Call the async postData function and log the response
            post_text(url, payload, send_index);
            send_index = send_index + 1;
            if (audio_debug) console.log(send_index, audio_buf_text);
            // sleep 2 seconds
            if (allow_auto_read_tts_flag) {
                await delay(3000);
            }
        }
    }
    audio_push_lock.unlock();
}


send_index = 0;
recv_index = 0;
to_be_processed = [];
async function UpdatePlayQueue(cnt, audio_buf_wave) {
    if (cnt != recv_index) {
        to_be_processed.push([cnt, audio_buf_wave]);
        if (audio_debug) console.log('cache', cnt);
    }
    else {
        if (audio_debug) console.log('processing', cnt);
        recv_index = recv_index + 1;
        if (audio_buf_wave) {
            audioPlayer.enqueueAudio(audio_buf_wave);
        }
        // deal with other cached audio
        while (true) {
            find_any = false;
            for (i = to_be_processed.length - 1; i >= 0; i--) {
                if (to_be_processed[i][0] == recv_index) {
                    if (audio_debug) console.log('processing cached', recv_index);
                    if (to_be_processed[i][1]) {
                        audioPlayer.enqueueAudio(to_be_processed[i][1]);
                    }
                    to_be_processed.pop(i);
                    find_any = true;
                    recv_index = recv_index + 1;
                }
            }
            if (!find_any) { break; }
        }
    }
}

function post_text(url, payload, cnt) {
    if (allow_auto_read_tts_flag) {
        postData(url, payload, cnt)
        .then(data => {
            UpdatePlayQueue(cnt, data);
            return;
        });
    } else {
        UpdatePlayQueue(cnt, null);
        return;
    }
}

notify_user_error = false
// Create an async function to perform the POST request
async function postData(url = '', data = {}) {
    try {
        // Use the Fetch API with await
        const response = await fetch(url, {
            method: 'POST', // Specify the request method
            body: JSON.stringify(data), // Convert the JavaScript object to a JSON string
        });
        // Check if the response is ok (status in the range 200-299)
        if (!response.ok) {
            // If not OK, throw an error
            console.info('There was a problem during audio generation requests:', response.status);
            // if (!notify_user_error){
            //     notify_user_error = true;
            //     alert('There was a problem during audio generation requests:', response.status);
            // }
            return null;
        }
        // If OK, parse and return the JSON response
        return await response.arrayBuffer();
    } catch (error) {
        // Log any errors that occur during the fetch operation
        console.info('There was a problem during audio generation requests:', error);
        // if (!notify_user_error){
        //     notify_user_error = true;
        //     alert('There was a problem during audio generation requests:', error);
        // }
        return null;
    }
}