from behave import use_fixture

from tests.features.fixtures import settings_auth, test_client


def before_tag(context, tag):
    if tag == "fixture.settings_auth":
        use_fixture(settings_auth, context)
    elif tag == "fixture.test_client":
        use_fixture(test_client, context)
