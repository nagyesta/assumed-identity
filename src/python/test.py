import time
import unittest

import app


def test_client():
    application = app.app
    application.config.update({
        "TESTING": True,
    })
    return application.test_client()


class AppTestCase(unittest.TestCase):
    def test_json_should_contain_expected_Fields_when_called_with_valid_url(self):
        # given
        resource: str = "https://localhost:8443"

        # when
        actual: dict = app.get_token_metadata(resource=resource)

        # then
        self.assertEqual(actual.keys(),
                         {"resource", "access_token", "refresh_token", "expires_in", "expires_on", "token_type"},
                         "Response should have been a token metadata JSON object")
        self.assertEqual(1, actual["token_type"], "Response should have been a Bearer token")
        self.assertIsNotNone(actual["access_token"], "Response should have an access token")
        self.assertIsNotNone(actual["refresh_token"], "Response should have a refresh token")
        self.assertGreater(actual["expires_in"], 3600, "Response should have at least 1 hour expiry")
        self.assertGreater(actual["expires_on"], time.time() + 3600, "Response should have a valid expiry time")
        self.assertEqual(resource, actual["resource"], "Response should have the expected resource")

    def test_input_validation_should_raise_error_when_invalid_url_is_passed(self):
        # given
        resource: str = "file://localhost"

        # when
        actual = test_client().get("/metadata/identity/oauth2/token?resource={}".format(resource))

        # then
        self.assertEqual(400, actual.status_code, "Response status should have been 400")
        self.assertTrue(str(actual.json["error"]).startswith("Parameter 'resource' pattern does not match:"),
                        "Response should have been an error message")

    def test_endpoint_should_return_token_when_valid_url_is_passed(self):
        # given
        resource: str = "https://localhost:8443"

        # when
        actual = test_client().get("/metadata/identity/oauth2/token?resource={}".format(resource))

        # then
        self.assertEqual(200, actual.status_code, "Response status should have been 200")
        self.assertEqual(resource, str(actual.json["resource"]), "Response should have the expected resource")


if __name__ == '__main__':
    unittest.main()
