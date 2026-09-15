describe('site smoke', () => {
  it('loads the about page', () => {
    cy.visit('/index.html')
    cy.contains('WEB MUSIC APPS FOR EVERYBODY').should('be.visible')
    cy.get('.navbary a').should('have.length.at.least', 4)
  })

  it('loads apps and renders filter buttons', () => {
    cy.visit('/apps.html')
    cy.get('#webapps .webapp').should('have.length.at.least', 1)
    cy.get('.filtering button.toggle').should('have.length.at.least', 1)
  })

  it('hides multi-tag apps when any of their tags is turned off (AND)', () => {
    cy.visit('/apps.html')
    cy.get('.hide-tags').click()
    cy.get('#2').should('be.visible')
    cy.get('.toggle-DIY').click()
    cy.get('.toggle-DIY').should('not.have.class', 'toggle-on')
    cy.get('.toggle-mustCheck').should('have.class', 'toggle-on')
    cy.get('#2').should('not.be.visible')
    cy.get('.toggle-DIY').click()
    cy.get('#2').should('be.visible')
  })

  it('loads evaluation, submit, and tags pages', () => {
    cy.visit('/evaluation.html')
    cy.get('body').should('be.visible')
    cy.visit('/submit.html')
    cy.get('body').should('be.visible')
    cy.visit('/tagsinfo.html')
    cy.contains('#mustCheck').should('exist')
  })
})
