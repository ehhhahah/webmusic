const CATEGORIES = [{'tag': '12+', 'desc': 'For users older than 12.'}, {'tag': 'AI', 'desc': 'Artificial intelligence technologies used.'}, {'tag': 'DAW', 'desc': 'Digital audio workstation, a lot of audio modulation/creating functionality.'}, {'tag': 'DIY', 'desc': 'Do it yourself, app made by single person and/or low-budget.'}, {'tag': 'FreeSound', 'desc': 'Use of FreeSound samples library.'}, {'tag': 'accessible', 'desc': 'General accessible app - for users with any impairment.'}, {'tag': 'ambient', 'desc': 'Relaxing, soft or slow-paced music.'}, {'tag': 'backgroundMuzak', 'desc': 'Music to be put in background, low listening effort expected.'}, {'tag': 'bigTech', 'desc': 'Created by big technological company.'}, {'tag': 'classic', 'desc': 'Well-known, popular project, gained huge audacity.'}, {'tag': 'classical', 'desc': 'Related to classical music.'}, {'tag': 'commercial', 'desc': 'App made for profit purposes.'}, {'tag': 'composing', 'desc': 'Apps that allow to compose a new and unique piece of music by user.'}, {'tag': 'descriptive', 'desc': 'Reading description or attached text is needed, app is mainly based on text.'}, {'tag': 'forKids', 'desc': 'Good for kids in any age.'}, {'tag': 'game', 'desc': 'Playful, focused on having fun.'}, {'tag': 'learn', 'desc': 'App that shares some knowledge.'}, {'tag': 'longRead', 'desc': 'A lot of reading is needed.'}, {'tag': 'marpi', 'desc': 'With use of Marpi platform (Web3GL engine, not accessible for screen readers).'}, {'tag': 'math', 'desc': 'Some math knowledge is required.'}, {'tag': 'mustCheck', 'desc': 'The best apps selection.'}, {'tag': 'noveltyArt', 'desc': 'New and unique piece of art, presented in a form of website.'}, {'tag': 'openSource', 'desc': 'Source code is publicly available.'}, {'tag': 'physic', 'desc': 'Some physic knowledge is required.'}, {'tag': 'realTime', 'desc': 'Works on real time data.'}, {'tag': 'reconstruction', 'desc': 'Previously published piece, reconstructed in the form of webstie.'}, {'tag': 'seizureWarning', 'desc': 'May contain flashing lights.'}, {'tag': 'sequencer', 'desc': 'App based on simple sound sequences.'}, {'tag': 'tool', 'desc': 'Useful to musicians and producers.'}, {'tag': 'visual', 'desc': 'Nice for people with limited hearing, focused more on visual aspect.'}];
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
        btn.innerHTML = "#" + category['tag'];
        btn.type = "button"
        btn.classList = "tooltip button btn-link is-rounded toggle toggle-on toggle-" + category['tag']
        btn.title = category["desc"]
        btn.onclick = function() { hideShowClassElement(category['tag']); };

        const filteringSpan = document.getElementsByClassName("filtering")[0]
        filteringSpan.appendChild(btn);
    })
    hideTags()
}

function toggleAll() {
    let currState = document.getElementsByClassName("toggle-all")[0].classList.toggle('toggle-all-off');
    CATEGORIES.forEach((className) => {
        if (currState) document.getElementsByClassName(`toggle-${className['tag']}`)[0].classList.add('toggle-on');
        else document.getElementsByClassName(`toggle-${className['tag']}`)[0].classList.remove('toggle-on');
        const elements = document.getElementsByClassName(className['tag']);

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