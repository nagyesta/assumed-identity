![AssumedIdentity](.github/assets/AssumedIdentity-Logo-512.png)

[![GitHub license](https://img.shields.io/github/license/nagyesta/assumed-identity?color=informational)](https://raw.githubusercontent.com/nagyesta/assumed-identity/main/LICENSE)
[![Build](https://img.shields.io/github/actions/workflow/status/nagyesta/assumed-identity/gradle-ci.yml?logo=github&branch=main)](https://github.com/nagyesta/assumed-identity/actions/workflows/gradle-ci.yml)
[![Docker Hub](https://img.shields.io/docker/v/nagyesta/assumed-identity?label=docker%20hub&logo=docker&sort=semver)](https://hub.docker.com/r/nagyesta/assumed-identity)
[![Docker Pulls](https://img.shields.io/docker/pulls/nagyesta/assumed-identity?logo=docker)](https://hub.docker.com/r/nagyesta/assumed-identity)

# Assumed Identity

This is a simple test double simulating how Azure Instance MetaData Service is handling Managed Identity Tokens.
If the Docker artifact is started on `169.254.169.254`, the locally executed tests can keep using the same
authentication method as in case of the production code (assuming that the production code is using Manage Identity
tokens).

## Usage

### Starting the container (on a developer machine)

Assumed Identity must use the `169.254.169.254` IP in order to simulate the real Managed Identity mechanism with the fake
token provider. To achieve this you need to first create an appropriate network with Docker.

```cmd
# One time setup
docker network create --subnet=169.254.169.0/24 assumed-id
```

Then you need to make sure to use the right IP when running the container.

```cmd
docker run --net assumed-id --ip 169.254.169.254 --rm nagyesta/assumed-identity:<version>
```

Please find the list of available versions [here](https://hub.docker.com/r/nagyesta/assumed-identity/tags).

Once the container is started, you can test it by navigating to
[http://169.254.169.254/metadata/identity/oauth2/token?api-verson=2018-02-01&resource=https://localhost/](http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://localhost/)

It should respond with a token.

### Starting the container (on a cloud hosted VM)

The default configuration (as detailed in the usage section) does not work on cloud VMs because they are using the
`169.254.169.254` IP for the real service providing instance metadata. As a workaround, you can simply start the
Assumed Identity container with the default, automatically assigned IP and configure it to use a non-default port.
For example by using the following command:

```cmd
docker run -e ASSUMED_ID_PORT=8080 -p 8080:8080 --rm nagyesta/assumed-identity:<version>
```

Please find the list of available versions [here](https://hub.docker.com/r/nagyesta/assumed-identity/tags).

Once the container is started, you can test it by navigating to
[http://localhost:8080/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://localhost/](http://localhost:8080/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://localhost/)

It should respond with a token.

When you have verified that your Assumed Identity instance is working as expected, you can configure the tested
application to use it by adding the appropriate environment variables depending on the language and the client
implementation. These are specifically mentioned in the Lowkey Vault examples
[here](https://github.com/nagyesta/lowkey-vault#example-projects).

### Optional parameters

You can pass environmental variables with the following names and functions to alter Assumed Identity configuration

| Name                | Default                                                       | Description                                                                                                    |
|---------------------|---------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------|
| ASSUMED_ID_PORT     | 80                                                            | The port where Assumed Identity will listen to requests.                                                       |
| ASSUMED_ID_HOST     | 0.0.0.0                                                       | The host/IP Assumed Identity will use to listen to requests. 0.0.0.0 means any.                                |
| ASSUMED_ID_ISSUER   | https://sts.windows.net/00000000-0000-0000-0000-000000000000/ | The name of the issuer used in the tokens                                                                      |
| ASSUMED_ID_KEY_PATH | \<use random generated key>                                   | The path where the RSA key file is mounted (inside the container) that needs to be used for signing the tokens | 

### All endpoints

#### `GET /metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://resource-host/`

Returns the tokens which can be automatically used by the Azure clients. For example:

```json
{
  "resource": "https://localhost",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC8wMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDAvIiwiYXVkIjoiaHR0cHM6Ly9sb2NhbGhvc3QiLCJleHAiOjE3NTE3NTI2NDYsIm5iZiI6MTc1MTU3OTg0NiwiaWF0IjoxNzUxNTc5ODQ2fQ.bP5U7cdrydPihjmkWO8-ekdfxkegt77wXD6DGZevMOGcH5LafMMdilZTKbCmenRrQqCeeJf5Z2WgNyb4dFbQVEYb2MU16yU0nDCsC-QyFQhszeuz8M7osbeC2wYyKTDc3dDzlJiU5cvrHeaMfFSpPpDap0IwkJv4DlP59Pg2uG3mQEtyDPyG1WwJLqNolCTYdkWjWpi5xlQb90hlyBLzOAIq77VP9Z3-AWYURcYhJQVM2cu0j-a0CB53VReKjMGxVpP3st9d8R8cTbvcJLQAcT5L7yMtJoONLgPAasOlcnGi5d6ExWBK2hxa6dVP2fvTmvuvn7nYRCV1l07yrZNgEg",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC8wMDAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDAvIiwiYXVkIjoiaHR0cHM6Ly9sb2NhbGhvc3QiLCJleHAiOjE3NTE3NTI2NDYsIm5iZiI6MTc1MTU3OTg0NiwiaWF0IjoxNzUxNTc5ODQ2fQ.bP5U7cdrydPihjmkWO8-ekdfxkegt77wXD6DGZevMOGcH5LafMMdilZTKbCmenRrQqCeeJf5Z2WgNyb4dFbQVEYb2MU16yU0nDCsC-QyFQhszeuz8M7osbeC2wYyKTDc3dDzlJiU5cvrHeaMfFSpPpDap0IwkJv4DlP59Pg2uG3mQEtyDPyG1WwJLqNolCTYdkWjWpi5xlQb90hlyBLzOAIq77VP9Z3-AWYURcYhJQVM2cu0j-a0CB53VReKjMGxVpP3st9d8R8cTbvcJLQAcT5L7yMtJoONLgPAasOlcnGi5d6ExWBK2hxa6dVP2fvTmvuvn7nYRCV1l07yrZNgEg",
  "expires_in": 172800,
  "expires_on": 1751752646,
  "token_type": "Bearer"
}
```
 
#### `GET /metadata/identity/.well-known/openid-configuration`

Returns the OpenID configuration. For example:

```json
{
  "issuer": "https://sts.windows.net/00000000-0000-0000-0000-000000000000/",
  "jwks_uri": "http://localhost:8080/metadata/identity/.well-known/openid-configuration/jwks"
}
```

#### `GET /metadata/identity/.well-known/openid-configuration/jwks`

Returns the details of the key used for signing the tokens. For example:

```json
{
  "keys": [
    {
      "n": "uZroJhgk7ZR9y1eK4y-KmbuXI5qWuofj_TjMnr6UamrOnORakUgWrroeSA4524L2-tG572JTRIFzblcgaZcBBpICXFYvlHPG1IwuH04GydmmkprXKAqJXoyo-UKQEmP8D0C-f7blmTQlufeZ5GB6pGGR6c3z7NNUUli77irglFS7u-EsTEsF4E9Hb9jVpnrjeZRsb4N7OFNLP31yf7zLd0rp6Qy0w3g_wWMYjJCj32FHpdFJBKAv2C8QzO6P-kEvYKmgaOeuGVNkVvra36q0rNnfdKFjMdsB-h6hFYzS8uDBeKPgzXmeiIDPskVUARIzHi262ghgvhWOV7lwgwt5jQ",
      "e": "AQAB",
      "d": "Ao_FQXVW2SKSA-Lu60jGMG363YZuKx_iASYuCMjXkopr1JWAPH4SthGihlsP6Fwr3XVUjB2-yXTB65VvQJXRcU5FkxGrcXCRn3BZ2JvCkzmaR260pnxSvgfR8zK8e0x-95TsrCWRkKY8GQ92Q8UjHC6ujVwG0E9wW_yWh2h3FgT5V-n-RvSX6v0WV14TaOhDCG-DzvFoEoT0-qr5dgP0pdoTB4ByaeiZ_gVieB9c5C5-h2pj0CQgY1u2OhpOul3_Q8ojxS8cTvVissnOASd_6sy-GwhE3mAP-OsudbLYX3ChSCfvEeLtURygoL_SQIdlaSPZmV_KqMwZsQW2Myj3UQ",
      "p": "3EdOKklaqhKctM2mfPQ3ML9ll1aQGwgc5NaC-_SpZ8ZDABrRvRhfQoJoXk3GKBHlqJ0d3tIQamGbm84lfT-l-oYny3pzN1365E0Pf0T2lgdutRmcGuvAenJPfO8_GgmyEF6kkPgJ_LbFfmhsjrAE8JRGFvDSJTJhexScIBMcIkU",
      "q": "17QpGczqu95lEiathvn2uymKmzradv4_4caIXaO5Do3fVQ1aRCCM6vS4E64146lt1a8lIL4cti8VM6r_vuceot7rzy3jIWEBJCWDi3KnXPgo0mWrctQ0L8v5xYKgWL3gy8RR5HmYDDovbuZgV2bx0rtcdrRQ-CjaSZGuunfQEqk",
      "dp": "WS8tgIVuhck_VRymOZUO-1eipCFR-v_P4v7OzYADTpbA7bvuCydg-iaeZwAKKJMGbrweKebW6ptWS0CtgQZSBxpl5kZPe607NU_V5GthguDDe-NAhs3Igkrhz-11mO8v_tyyuFcUhBLj5wgUW7j8ZwNBVWxvSMwbF6ACjiHulBk",
      "dq": "HppO4nwyKWlKCaM3J1k7ah5grdlRuWQlCBE0s6RQ0wHJ17VHQzcjBwqlOxWSS7R0AscQi26tgCN57JSsKBd-PzlFV2V5PfkXQluYKCaiHAyRLhiClI4KwWU9EIqR2UVHKWG3BKVDryhqJl_E92GBmZY_bg_zFOIm5h0nHwl0mdE",
      "qi": "a3DC9GwUG0SIeWJ_ur-SJ4Fp_WM4mmvdMxkWJvv6FVsn9bHwXSsM1PbiMH1zsPUmg_xvCzBX2oUQa6WV8RHkHouBTqGeMqpK-wVDwkQQTIx8zPEOHbgcd5sk2HSQz-JjpPPRr7qVXSTajEGllB0dipY5E3USEUZsYiaLZ4mBxhY",
      "use": "sig",
      "kty": "RSA",
      "kid": "79bQ2WFLybaduKC6XUkY6wdYPbKkRJwkswmKE52Ot9w"
    }
  ]
}
```

### Examples

For complete examples of how it can be used in action, please feel free to visit the Lowkey Vault examples which can
be found [here](https://github.com/nagyesta/lowkey-vault#example-projects).
