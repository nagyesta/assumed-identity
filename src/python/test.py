import sys
import time
import unittest
import unittest.mock
import pytest

import app


@pytest.mark.skip(reason="helper method")
def test_client():
    application = app.app
    application.config.update({
        "TESTING": True
    })
    return application.test_client()


class AppTestCase(unittest.TestCase):
    def test_process_arguments_should_parse_ssl_certificate_parameters(self):
        # when
        with unittest.mock.patch.object(sys, "argv", ["app.py", "--ssl-certificate-path", "certificate.pem", "--ssl-certificate-key-path", "key.pem"]):
            actual = app.process_arguments()

        # then
        self.assertEqual("certificate.pem", actual.ssl_certificate_path, "SSL certificate path should have been parsed")
        self.assertEqual("key.pem", actual.ssl_certificate_key_path, "SSL certificate key path should have been parsed")

    def test_init_ssl_context_should_return_none_when_ssl_certificate_is_not_provided(self):
        # when
        actual = app.init_ssl_context(None, None)

        # then
        self.assertIsNone(actual, "SSL context should be None when no SSL certificate is provided")

    def test_init_ssl_context_should_raise_error_when_ssl_certificate_key_is_provided_without_ssl_certificate(self):
        # when / then
        with self.assertRaisesRegex(ValueError, "SSL certificate key path can only be used together with SSL certificate path"):
            app.init_ssl_context(None, "key.pem")

    def test_init_ssl_context_should_load_ssl_certificate_chain_when_ssl_certificate_is_provided(self):
        # given
        expected_context = unittest.mock.MagicMock()

        # when
        with unittest.mock.patch("app.ssl.SSLContext", return_value=expected_context) as ssl_context_constructor:
            actual = app.init_ssl_context("certificate.pem", "key.pem")

        # then
        ssl_context_constructor.assert_called_once_with(app.ssl.PROTOCOL_TLS_SERVER)
        expected_context.load_cert_chain.assert_called_once_with(certfile="certificate.pem", keyfile="key.pem")
        self.assertEqual(expected_context, actual, "Returned SSL context should have been the initialized context")

    def test_token_endpoint_json_should_contain_expected_Fields_when_called_with_valid_url(self):
        # given
        resource: str = "https://localhost:8443"
        app.app.config.update({
            "AID_ISSUER": "https://sts.windows.net/00000000-0000-0000-0000-000000000000",
            "AID_KEY": app.generate_key()
        })

        # when
        actual: dict = app.get_token_metadata(resource=resource)

        # then
        self.assertEqual(actual.keys(),
                         {"resource", "access_token", "refresh_token", "expires_in", "expires_on", "token_type"},
                         "Response should have been a token metadata JSON object")
        self.assertEqual("Bearer", actual["token_type"], "Response should have been a Bearer token")
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

    def test_token_endpoint_should_return_token_when_valid_url_is_passed(self):
        # given
        resource: str = "https://localhost:8443"
        app.app.config.update({
            "AID_ISSUER": "https://sts.windows.net/00000000-0000-0000-0000-000000000000",
            "AID_KEY": app.generate_key()
        })

        # when
        actual = test_client().get("/metadata/identity/oauth2/token?resource={}".format(resource))

        # then
        self.assertEqual(200, actual.status_code, "Response status should have been 200")
        self.assertEqual(resource, str(actual.json["resource"]), "Response should have the expected resource")

    def test_configuration_endpoint_should_return_list_of_urls_when_called(self):
        # given
        issuer = "https://sts.windows.net/00000000-0000-0000-0000-000000000001"
        app.app.config.update({
            "AID_ISSUER": issuer,
            "AID_KEY": app.generate_key()
        })

        # when
        actual = test_client().get("/metadata/identity/.well-known/openid-configuration")

        # then
        self.assertEqual(200, actual.status_code, "Response status should have been 200")
        self.assertEqual(issuer, str(actual.json["issuer"]), "Response should have the expected issuer")
        self.assertTrue(
            str(actual.json["jwks_uri"]).endswith("/metadata/identity/.well-known/openid-configuration/jwks"),
            "Response should have the expected jwks_uri")

    def test_jwks_endpoint_should_contain_key_details_when_called(self):
        # given
        app.app.config.update({
            "AID_ISSUER": "https://sts.windows.net/00000000-0000-0000-0000-000000000000",
            "AID_KEY": app.generate_key()
        })

        # when
        actual = test_client().get("/metadata/identity/.well-known/openid-configuration/jwks")

        # then
        self.assertEqual(200, actual.status_code, "Response status should have been 200")
        self.assertEqual(actual.json["keys"][0].keys(),
                         {"n", "e", "d", "p", "q", "dp", "dq", "qi", "use", "kty", "kid"},
                         "Response should have contained the key details")


if __name__ == '__main__':
    unittest.main()
