
var rangeInputs = null;
var numberInputs = null;


function setSlider() {
    function setSliderRange() {
        var range = document.querySelectorAll('input[type="range"]');
        range.forEach(range => {
            range.style.backgroundSize = (range.value - range.min) / (range.max - range.min) * 100 + '% 100%';
        });
    }
    rangeInputs = document.querySelectorAll('input[type="range"]');
    numberInputs = document.querySelectorAll('input[type="number"]')
    setSliderRange();
    rangeInputs.forEach(rangeInput => {
        rangeInput.addEventListener('input', setSliderRange);
    });
    numberInputs.forEach(numberInput => {
        numberInput.addEventListener('input', setSliderRange);
    })
}
