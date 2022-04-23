const CATEGORIES = ['Physic', 'bigTech', 'classic', 'openSource', 'descriptive', 'AI', 'commercial', 'FreeSound', 'DIY', 'math', 'mustCheck']

function hideShowClassElement(className) {
    let currState = document.getElementsByClassName(`toggle-${className}`)[0].classList.toggle('toggle-on');
    const elements  = document.getElementsByClassName(className);

    for (let i=0; i<elements.length; i++) {
        elements[i].style.display = currState ? "block" : "none"
    }
}
