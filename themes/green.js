
var academic_chat = null;

var sliders = null;
var rangeInputs = null;
var numberInputs = null;

function set_elements() {
    academic_chat = document.querySelector('gradio-app');
    async function get_sliders() {
        sliders = document.querySelectorAll('input[type="range"]');
        while (sliders.length == 0) {
            await new Promise(r => setTimeout(r, 100));
            sliders = document.querySelectorAll('input[type="range"]');
        }
        setSlider();
    }
    get_sliders();
}

function setSlider() {
    rangeInputs = document.querySelectorAll('input[type="range"]');
    numberInputs = document.querySelectorAll('input[type="number"]')
    function setSliderRange() {
        var range = document.querySelectorAll('input[type="range"]');
        range.forEach(range => {
            range.style.backgroundSize = (range.value - range.min) / (range.max - range.min) * 100 + '% 100%';
        });
    }
    setSliderRange();
    rangeInputs.forEach(rangeInput => {
        rangeInput.addEventListener('input', setSliderRange);
    });
    numberInputs.forEach(numberInput => {
        numberInput.addEventListener('input', setSliderRange);
    })
}

window.addEventListener("DOMContentLoaded", () => {
    set_elements();
});
