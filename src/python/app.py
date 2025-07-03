import argparse
import json
import time
from argparse import Namespace, ArgumentParser

import flask
from flask_parameter_validation import ValidateParameters, Query
from flask import Flask, request
from joserfc import jwt
from joserfc._keys import KeySetSerialization
from joserfc.jwk import KeySet, RSAKey
from joserfc.rfc7518.rsa_key import RSAKey

app = Flask(__name__)


def get_token_metadata(resource: str) -> dict:
    expires_in: int = 48 * 3600
    epoch_time: int = int(time.time())
    expires_on: int = epoch_time + expires_in

    header: dict = {
        "alg": "RS256"
    }

    claims: dict = {
        "iss": app.config.get("AID_ISSUER"),
        "aud": resource,
        "exp": expires_on,
        "nbf": epoch_time,
        "iat": epoch_time
    }

    token_value = jwt.encode(header, claims, app.config.get("AID_KEY"))

    return {
        "resource": resource,
        "access_token": token_value,
        "refresh_token": token_value,
        "expires_in": expires_in,
        "expires_on": expires_on,
        "token_type": "Bearer"
    }


def init_key(key_path: str) -> RSAKey:
    return generate_key() if key_path is None else import_key(key_path)


def generate_key() -> RSAKey:
    return RSAKey.generate_key(2048, {"use": "sig"})


def import_key(path: str) -> RSAKey:
    file = open(path, "rb")
    key = RSAKey.import_key(file.read(), {"use": "sig"})
    file.close()
    return key


url_regexp = ('^(http(s)?)://'
              '('
              '(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}'
              '([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])'
              '(:[0-9]+)?'
              '|'
              '(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\\-]*[a-zA-Z0-9])\\.)*'
              '([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\\-]*[A-Za-z0-9])'
              '(:[0-9]+)?'
              ')'
              '(/[A-Za-z0-9.\\-_/]*)?$')


def as_json_response(json_content: dict | KeySetSerialization) -> flask.Response:
    resp = flask.Response(json.dumps(json_content))
    resp.headers['Content-Type'] = 'application/json'
    return resp


@app.route(rule='/metadata/identity/.well-known/openid-configuration', methods=['GET'])
@app.route(rule='/metadata/identity/.well-known/openid-configuration/', methods=['GET'])
@ValidateParameters()
def configuration():
    return as_json_response({
        "issuer": app.config.get("AID_ISSUER"),
        "jwks_uri": f"{request.scheme}://{request.host}/metadata/identity/.well-known/openid-configuration/jwks"
    })


@app.route(rule='/metadata/identity/.well-known/openid-configuration/jwks', methods=['GET'])
@app.route(rule='/metadata/identity/.well-known/openid-configuration/jwks/', methods=['GET'])
@ValidateParameters()
def jwks():
    return as_json_response(KeySet([app.config.get("AID_KEY")]).as_dict())


@app.route(rule='/metadata/identity/oauth2/token', methods=['GET'])
@app.route(rule='/metadata/identity/oauth2/token/', methods=['GET'])
@ValidateParameters()
def token(resource: str = Query(pattern=url_regexp)):
    return as_json_response(get_token_metadata(resource))


def process_arguments() -> Namespace:
    parser: ArgumentParser = argparse.ArgumentParser(description="Example script with arguments")
    parser.add_argument("--host", help="The host name you want to use", type=str,
                        default="0.0.0.0")
    parser.add_argument("--issuer", help="The issuer you want to use", type=str,
                        default="https://sts.windows.net/00000000-0000-0000-0000-000000000000/")
    parser.add_argument("--key", help="The key you want to use", type=str)
    parser.add_argument("--port", help="The port number you want to use", type=int,
                        default=5000)
    return parser.parse_args()


if __name__ == '__main__':
    args: Namespace = process_arguments()

    app.config.update({
        "AID_ISSUER": args.issuer,
        "AID_KEY": init_key(args.key)
    })
    app.run(args.host, args.port)
