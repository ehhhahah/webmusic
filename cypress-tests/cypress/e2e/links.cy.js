describe('links correctness', () => {
  beforeEach(() => {
    cy.visit('/index.html')
  })

  it('has all correct links', () => {
    const IGNORE_IT = [
      'http://www.chenalexander.com/',
      'https://en.wikipedia.org/wiki/List_of_online_music_databases',
      'https://samplefocus.com/',
    ] // mostly things with cloudflare or other anti-bots

    cy.get('a').each(($page) => {
      const link = $page.prop('href')
      if (
        !link ||
        link.startsWith('mailto:') ||
        IGNORE_IT.includes(link) ||
        link.endsWith('.pdf') ||
        link.includes('codepen')
      ) {
        Cypress.log({
          name: link || '(empty)',
          message: 'Link ignored.',
          displayName: 'IGNORING',
        })
        return
      }

      cy.request({
        url: link,
        failOnStatusCode: false,
      }).then((response) => {
        Cypress.log({
          name: link,
          message: String(response.status),
        })

        if (response.status > 200 && response.status < 400) {
          Cypress.log({
            name: link,
            message: `Website redirected or something. ${response.status}`,
            displayName: 'OKAYISH',
          })
        } else if (response.status >= 400) {
          Cypress.log({
            name: link,
            message: `Website did not respond or something. ${response.status}`,
            displayName: 'FUCKERY',
          })
        }
      })
    })
  })
})
