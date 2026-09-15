const CATEGORIES = [{'tag': '12+', 'desc': 'For users older than 12.'}, {'tag': 'accessible', 'desc': 'General accessible app - for users with any impairment.'}, {'tag': 'AI', 'desc': 'Artificial intelligence technologies used.'}, {'tag': 'ambient', 'desc': 'Relaxing, soft or slow-paced music.'}, {'tag': 'backgroundMuzak', 'desc': 'Music to be put in background, low listening effort expected.'}, {'tag': 'bigTech', 'desc': 'Created by big technological company.'}, {'tag': 'classic', 'desc': 'Well-known, popular project, gained huge audacity.'}, {'tag': 'classical', 'desc': 'Related to classical music.'}, {'tag': 'commercial', 'desc': 'App made for profit purposes.'}, {'tag': 'composing', 'desc': 'Apps that allow to compose a new and unique piece of music by user.'}, {'tag': 'DAW', 'desc': 'Digital audio workstation, a lot of audio modulation/creating functionality.'}, {'tag': 'descriptive', 'desc': 'Reading description or attached text is needed, app is mainly based on text.'}, {'tag': 'DIY', 'desc': 'Do it yourself, app made by single person and/or low-budget.'}, {'tag': 'forKids', 'desc': 'Good for kids in any age.'}, {'tag': 'FreeSound', 'desc': 'Use of FreeSound samples library.'}, {'tag': 'game', 'desc': 'Playful, focused on having fun.'}, {'tag': 'learn', 'desc': 'App that shares some knowledge.'}, {'tag': 'limitedVision', 'desc': 'Accessible for users with vision impairment (for example good contrast ratios, font size is big enought).'}, {'tag': 'longRead', 'desc': 'A lot of reading is needed.'}, {'tag': 'marpi', 'desc': 'With use of Marpi platform (Web3GL engine, not accessible for screen readers).'}, {'tag': 'math', 'desc': 'Some math knowledge is required.'}, {'tag': 'mustCheck', 'desc': 'The best apps selection.'}, {'tag': 'noveltyArt', 'desc': 'New and unique piece of art, presented in a form of website.'}, {'tag': 'openSource', 'desc': 'Source code is publicly available.'}, {'tag': 'physic', 'desc': 'Some physic knowledge is required.'}, {'tag': 'realTime', 'desc': 'Works on real time data.'}, {'tag': 'reconstruction', 'desc': 'Previously published piece, reconstructed in the form of webstie.'}, {'tag': 'seizureWarning', 'desc': 'May contain flashing lights.'}, {'tag': 'sequencer', 'desc': 'App based on simple sound sequences.'}, {'tag': 'smallBandwidth', 'desc': 'Slow network users should not have issues with opening and using the app.'}, {'tag': 'tool', 'desc': 'Useful to musicians and producers.'}, {'tag': 'visual', 'desc': 'Nice for people with limited hearing, focused more on visual aspect.'}];

function syncToggleAria(btn) {
    btn.setAttribute('aria-pressed', btn.classList.contains('toggle-on') ? 'true' : 'false');
}

function syncTagsExpandedAria() {
    const filtering = document.getElementsByClassName('filtering')[0];
    const expanded = Boolean(filtering && filtering.style.display !== 'none');
    const hideBtn = document.getElementsByClassName('hide-tags')[0];
    const showBtn = document.getElementsByClassName('show-tags')[0];
    if (hideBtn) hideBtn.setAttribute('aria-expanded', expanded ? 'true' : 'false');
    if (showBtn) showBtn.setAttribute('aria-expanded', expanded ? 'true' : 'false');
}

function getActiveTags() {
    return CATEGORIES
        .map((category) => category.tag)
        .filter((tag) => document.getElementsByClassName(`toggle-${tag}`)[0].classList.contains('toggle-on'));
}

function applyTagFilter() {
    const activeTags = getActiveTags();
    const cards = document.getElementsByClassName('webapp');

    for (let i = 0; i < cards.length; i++) {
        const card = cards[i];
        // AND: app must contain every selected tag (and may have more).
        // All on → full catalog; none on → empty; otherwise selected ⊆ card tags.
        let matches;
        if (activeTags.length === 0) {
            matches = false;
        } else if (activeTags.length === CATEGORIES.length) {
            matches = true;
        } else {
            matches = activeTags.every((tag) => card.classList.contains(tag));
        }
        card.style.display = matches ? 'block' : 'none';
    }
}

function hideShowClassElement(className) {
    const btn = document.getElementsByClassName(`toggle-${className}`)[0];
    btn.classList.toggle('toggle-on');
    syncToggleAria(btn);
    applyTagFilter();
}

function renderFilteringButtons() {
    CATEGORIES.forEach((category) => {
        const btn = document.createElement('button');
        btn.textContent = '#' + category.tag;
        btn.type = 'button';
        btn.className = 'button btn-link is-rounded toggle toggle-on toggle-' + category.tag;
        btn.title = category.desc;
        btn.setAttribute('aria-label', '#' + category.tag + ': ' + category.desc);
        btn.setAttribute('aria-pressed', 'true');
        btn.onclick = function () { hideShowClassElement(category.tag); };

        const filteringSpan = document.getElementsByClassName('filtering')[0];
        filteringSpan.appendChild(btn);
    });
    hideTags();
}

function toggleAll() {
    const toggleAllBtn = document.getElementsByClassName('toggle-all')[0];
    let currState = toggleAllBtn.classList.toggle('toggle-all-off');
    toggleAllBtn.setAttribute('aria-pressed', currState ? 'true' : 'false');
    CATEGORIES.forEach((className) => {
        const btn = document.getElementsByClassName(`toggle-${className.tag}`)[0];
        if (currState) btn.classList.add('toggle-on');
        else btn.classList.remove('toggle-on');
        syncToggleAria(btn);
    });
    applyTagFilter();
}

function hideTags() {
    let currState = document.getElementsByClassName('hide-tags')[0].classList.toggle('hide-all-off');
    document.getElementsByClassName('show-tags')[0].classList.toggle('hide-all-off');

    const elements = document.getElementsByClassName('filtering');
    for (let i = 0; i < elements.length; i++) {
        elements[i].style.display = currState ? 'grid' : 'none';
    }
    syncTagsExpandedAria();
}

function enhanceTagLabels() {
    document.querySelectorAll('.tag[title]').forEach((el) => {
        if (!el.getAttribute('aria-label')) {
            el.setAttribute('aria-label', el.textContent.trim() + ': ' + el.title);
        }
    });
}

window.onload = function () {
    renderFilteringButtons();
    enhanceTagLabels();
};
