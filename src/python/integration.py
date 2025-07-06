import os
import unittest
import requests
from requests import Response


class AppTestCase(unittest.TestCase):
    def test_token_endpoint_json_should_contain_expected_Fields_when_called_with_valid_url(self):
        # given
        container_host: str = "http://localhost:8080"
        resource: str = "https://localhost:8443"

        # when
        response: Response = requests.get(url=f"{container_host}/metadata/identity/oauth2/token", params={"resource": resource})

        # then
        self.assertEqual(200, response.status_code, "Response status is not 200.")
        actual: dict = response.json()
        response.close()
        self.assertIsNotNone(actual["access_token"], "Response should have an access token")
        self.assertEqual(resource, actual["resource"], "Response should have the expected resource")

    def test_input_validation_should_raise_error_when_invalid_url_is_passed(self):
        # given
        container_host: str = "http://localhost:8080"
        resource: str = "file://localhost"

        # when
        response: Response = requests.get(url=f"{container_host}/metadata/identity/oauth2/token", params={"resource": resource})

        # then
        self.assertEqual(400, response.status_code, "Response status is not 400.")
        actual: dict = response.json()
        response.close()
        self.assertTrue(str(actual["error"]).startswith("Parameter 'resource' pattern does not match:"),
                        "Response should have been an error message")

    def test_configuration_endpoint_should_return_list_of_urls_when_called(self):
        # given
        container_host: str = "http://localhost:8080"
        issuer = "https://sts.windows.net/00000000-0000-0000-0000-000000000001/"

        # when
        response: Response = requests.get(url=f"{container_host}/metadata/identity/.well-known/openid-configuration")

        # then
        self.assertEqual(200, response.status_code, "Response status is not 200.")
        actual: dict = response.json()
        response.close()
        self.assertEqual(issuer, str(actual["issuer"]), "Response should have the expected issuer")
        self.assertTrue(
            str(actual["jwks_uri"]).endswith("/metadata/identity/.well-known/openid-configuration/jwks"),
            "Response should have the expected jwks_uri")

    def test_jwks_endpoint_should_contain_key_details_when_called(self):
        # given
        container_host: str = "http://localhost:8080"

        # when
        response: Response = requests.get(url=f"{container_host}/metadata/identity/.well-known/openid-configuration/jwks")

        # then
        self.assertEqual(200, response.status_code, "Response status is not 200.")
        actual: dict = response.json()
        response.close()
        self.assertEqual(actual["keys"][0].keys(),
                         {"n", "e", "d", "p", "q", "dp", "dq", "qi", "use", "kty", "kid"},
                         "Response should have contained the key details")


if __name__ == '__main__':
    unittest.main()
