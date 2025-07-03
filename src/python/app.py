import argparse
import json
import time
from argparse import Namespace, ArgumentParser
from flask_parameter_validation import ValidateParameters, Query
from flask import Flask, request
from joserfc import jwt
from joserfc.jwk import KeySet, RSAKey

app = Flask(__name__)


def get_token_metadata(resource: str) -> dict:
    expires_in: int = 48 * 3600
    epoch_time: int = int(time.time())
    expires_on: int = epoch_time + expires_in

    header: dict = {
        "alg": "RS256"
    }

    claims: dict = {
        "iss": app.config.issuer,
        "aud": resource,
        "exp": expires_on,
        "nbf": epoch_time,
        "iat": epoch_time
    }

    return {
        "resource": resource,
        "access_token": jwt.encode(header, claims, app.config.key),
        "expires_in": expires_in,
        "expires_on": expires_on,
        "token_type": "Bearer"
    }


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


@app.route(rule='/metadata/identity/oauth2/token', methods=['GET'])
@app.route(rule='/metadata/identity/oauth2/token/', methods=['GET'])
@ValidateParameters()
def token(resource: str = Query(pattern=url_regexp)):
    return get_token_metadata(resource)


def process_arguments() -> Namespace:
    parser: ArgumentParser = argparse.ArgumentParser(description="Example script with arguments")
    parser.add_argument("--host", help="The host name you want to use", type=str, default="0.0.0.0")
    parser.add_argument("--issuer", help="The issuer you want to use", type=str, default="https://sts.windows.net/00000000-0000-0000-0000-000000000000/")
    parser.add_argument("--key", help="The key you want to use", type=str)
    parser.add_argument("--port", help="The port number you want to use", type=int, default=5000)
    return parser.parse_args()


if __name__ == '__main__':
    args: Namespace = process_arguments()

    app.config.issuer = args.issuer
    app.config.key = RSAKey.generate_key(2048, {"use": "sig"}) if args.key is None else import_key(args.key)
    app.run(args.host, args.port)
