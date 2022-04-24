const CATEGORIES = ["classic", "physic", "openSource", "commercial", "FreeSound", "tonejs", "DIY", "AI", "ambient", "TeroParviainen", "descriptive", "math", "DAW", "bigTech", "classical", "mustCheck"]

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
        btn.classList = "button is-rounded  toggle toggle-on toggle-" + category
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

window.onload = renderFilteringButtons