import argparse
import time
from argparse import Namespace, ArgumentParser

from flask_parameter_validation import ValidateParameters, Query
from flask import Flask

app = Flask(__name__)


def get_token_metadata(resource: str) -> dict:
    expires_in: int = 48 * 3600
    epoch_time: int = int(time.time())
    expires_on: int = epoch_time + expires_in

    return {
        "resource": resource,
        "access_token": "dummy",
        "refresh_token": "dummy",
        "expires_in": expires_in,
        "expires_on": expires_on,
        "token_type": "Bearer"
    }


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
    parser.add_argument("--port", help="The port number you want to use", type=int, default=5000)
    return parser.parse_args()


if __name__ == '__main__':
    args: Namespace = process_arguments()

    app.run(args.host, args.port)
