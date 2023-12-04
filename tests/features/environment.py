from behave import use_fixture

from tests.features.fixtures import app_settings_test, engine, test_client


def before_tag(context, tag):
    if tag == "fixture.app_settings_test":
        use_fixture(app_settings_test, context)
    elif tag == "fixture.engine":
        use_fixture(engine, context)
    elif tag == "fixture.test_client":
        use_fixture(test_client, context)
