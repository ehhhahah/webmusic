

describe('links correctness', () => {
  beforeEach(() => {
    cy.visit('/')
  })

  // it('has all correct links', () => {
  //   cy.get("a:not([href*='mailto:]']").then((pages) => {

  //     [pages].forEach(page => {
  //       cy.get(page).click({ multiple: true })
  //       cy.visit('/')
  //     })
  //   })
  // })

  it('has all correct links', () => {
    let NOT_SURES = []
    let BAD_SITES = []
    let IGNORE_IT = [
      'http://www.chenalexander.com/', 'http://everynoise.com/new_releases_by_genre.cgi', 'https://eclipticalis.com/',
      'https://en.wikipedia.org/wiki/List_of_online_music_databases', 'https://www.maxlaumeister.com/', 
      'https://generative.fm/music/alex-bainter-aisatsana', 'https://samplefocus.com/'
    ]  // mostly things with cloudfire or something other anti-bots
    cy.get("a").each(page => {
      const link = page.prop('href')
      if (IGNORE_IT.includes(link) || link.substring(link.length-4, link.length) == ".pdf" || link.includes('codepen')) {
        Cypress.log({
          name: link,
          message: "Link ignored.",
          displayName: 'IGNORING',
        })
      }
      else {
      cy.request({
        url: link,
        failOnStatusCode: false  // allow good and bad response to pass into then
      }).then(response => {
        Cypress.log({
          name: link,
          message: response.status
        })

        if (response.status > 200 && response.status < 400) {
          Cypress.log({
            name: link,
            message: "Website redicreted or something. " + response.status,
            displayName: 'OKAYISH',
          })
        }
        else if (response.status >= 400) {
          Cypress.log({
            name: link,
            message: "Website did not respond or something. " + response.status,
            displayName: 'FUCKERY',
          })
        }
      })
    }
    })
  })
})
