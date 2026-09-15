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

  it('loads evaluation, submit, and tags pages', () => {
    cy.visit('/evaluation.html')
    cy.get('body').should('be.visible')
    cy.visit('/submit.html')
    cy.get('body').should('be.visible')
    cy.visit('/tagsinfo.html')
    cy.contains('#mustCheck').should('exist')
  })
})
