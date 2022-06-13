const CATEGORIES = ['12+', 'AI', 'DAW', 'DIY', 'FreeSound', 'accessible', 'ambient', 'backgroundMuzak', 'bigTech', 'classic', 'classical', 'commercial', 'composing', 'descriptive', 'forKids', 'game', 'learn', 'longRead', 'marpi', 'math', 'mustCheck', 'noveltyArt', 'openSource', 'physic', 'realTime', 'reconstruction', 'seizureWarning', 'sequencer', 'tool', 'visual'];
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
        btn.classList = "tooltip button btn-link is-rounded toggle toggle-on toggle-" + category
        btn.onclick = function() { hideShowClassElement(category); };

        const tooltiptext = document.createElement("span");
        tooltiptext.innerHTML = "TODO add tooltips over tags, currently please refer to /tagsinfo page"
        tooltiptext.type = "span"
        tooltiptext.classList = "tooltiptext"
        btn.appendChild(tooltiptext)

        const filteringSpan = document.getElementsByClassName("filtering")[0]
        filteringSpan.appendChild(btn);
    })
    hideTags()
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

function hideTags() {
    let currState = document.getElementsByClassName("hide-tags")[0].classList.toggle('hide-all-off');
    document.getElementsByClassName("show-tags")[0].classList.toggle('hide-all-off');

    CATEGORIES.forEach((className) => {
        const elements = document.getElementsByClassName("filtering");

        for (let i=0; i<elements.length; i++) {
            elements[i].style.display = currState ? "grid" : "none"
        }
    })
    
}

window.onload = renderFilteringButtons