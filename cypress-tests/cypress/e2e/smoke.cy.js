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

  it('shows apps that contain all selected tags (AND)', () => {
    cy.visit('/apps.html')
    cy.get('.hide-tags').click()
    cy.get('.toggle-all').click()
    cy.get('.toggle-ambient').click()
    cy.get('.toggle-ambient').should('have.class', 'toggle-on')
    cy.get('#22').should('be.visible')
    cy.get('#23').should('be.visible')
    cy.get('.toggle-DIY').click()
    cy.get('#22').should('be.visible')
    cy.get('#23').should('not.be.visible')
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
