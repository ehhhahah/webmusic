const CATEGORIES = ['seizureWarning', 'bigTech', 'openSource', 'kidsFriendly', 'classical', 'physic', 'descriptive', 'DIY', 'math', 'commercial', 'accessible', 'tonejs', 'mustCheck', 'ambient', 'AI', 'game', 'DAW', 'TeroParviainen', 'classic', '12+', 'FreeSound', 'tool'];
function hideShowClassElement(className) {
    let currState = document.getElementsByClassName(`toggle-${className}`)[0].classList.toggle('toggle-on');
    const elements  = document.getElementsByClassName(className);

    for (let i=0; i<elements.length; i++) {
        elements[i].style.display = currState ? "block" : "none"
    }
}

function renderFilteringButtons() {
    CATEGORIES.forEach((category) => {
        const btn = document.createElement("button");
        btn.innerHTML = "#" + category;
        btn.type = "button"
        btn.classList = "button btn-link is-rounded toggle toggle-on toggle-" + category
        btn.onclick = function() { hideShowClassElement(category); };
        const filteringSpan = document.getElementsByClassName("filtering")[0]
        filteringSpan.appendChild(btn);
    })
}

function toggleAll() {
    let currState = document.getElementsByClassName("toggle-all")[0].classList.toggle('toggle-all-off');
    CATEGORIES.forEach((className) => {
        if (currState) document.getElementsByClassName(`toggle-${className}`)[0].classList.add('toggle-on');
        else document.getElementsByClassName(`toggle-${className}`)[0].classList.remove('toggle-on');
        const elements = document.getElementsByClassName(className);

        for (let i=0; i<elements.length; i++) {
            elements[i].style.display = currState ? "block" : "none"
        }
    })
}

function changeFont(){
    function getColorCode() {
        var makeColorCode = '0123456789ABCDEF';
        var code = '#';
        for (var count = 0; count < 6; count++) {
           code = code+ makeColorCode[Math.floor(Math.random() * 8)];
        }
        return code;
     }
    const fonts = ["Impact", "Comic Sans MS", "Georgia", "Courier New", "Bebas Neue"]
    var x = document.getElementById("changable");
    // x.style.fontFamily = fonts[Math.floor(Math.random()*fonts.length)];
    x.style.color = getColorCode()
}

function collapseAllText(){
    const elements  = document.getElementsByClassName("card-text");
    for (let i=0; i<elements.length; i++) {
        elements[i].classList.toggle('d-inline-block text-truncate');
    }
}

window.onload = renderFilteringButtons, collapseAllText