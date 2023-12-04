from behave import given, then, when
from behave.runner import Context

from tests.setup import get_bearer_token


@given("I am logged in as a user")
def logged_in_precondition(context: Context):
    token = get_bearer_token(settings_auth=context.app_settings_test)
    context.test_client.cookies = {"access_token": f'Bearer {token["access_token"]}'}


@given("I am not logged in as a user")
def not_logged_in_precondition(context: Context):
    pass


@when("I navigate to the private route")
def navigate_to_private_action(context: Context):
    response = context.test_client.get("/private")
    context.response = response


@then("I get access to private data")
def access_private_data_outcome(context: Context):
    assert context.response
    assert context.response.status_code == 200
    assert context.response.json()


@then("I get access to private data denied")
def access_private_data_denied_outcome(context: Context):
    assert context.response
    assert context.response.status_code == 401
