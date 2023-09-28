Feature: Access protected information

  @fixture.settings_auth
  @fixture.engine
  @fixture.test_client
  Scenario: Access protected information as logged-in user
     Given I am logged in as a user
      When I navigate to the private route
      Then I get access to private data

  @fixture.settings_auth
  @fixture.engine
  @fixture.test_client
  Scenario: Access protected information as anonymous user
     Given I am not logged in as a user
      When I navigate to the private route
      Then I get access to private data denied
