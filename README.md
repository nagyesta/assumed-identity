
![AssumedIdentity](.github/assets/AssumedIdentity-Logo-512.png)

[![GitHub license](https://img.shields.io/github/license/nagyesta/assumed-identity?color=informational)](https://raw.githubusercontent.com/nagyesta/assumed-identity/main/LICENSE)
[![Build](https://img.shields.io/github/actions/workflow/status/nagyesta/assumed-identity/gradle-ci.yml?logo=github&branch=main)](https://github.com/nagyesta/assumed-identity/actions/workflows/gradle-ci.yml)
[![Docker Hub](https://img.shields.io/docker/v/nagyesta/assumed-identity?label=docker%20hub&logo=docker&sort=semver)](https://hub.docker.com/r/nagyesta/assumed-identity)
[![Docker Pulls](https://img.shields.io/docker/pulls/nagyesta/assumed-identity?logo=docker)](https://hub.docker.com/r/nagyesta/assumed-identity)

# Assumed Identity

This is a simple test double simulating how Azure Instance MetaData Service is handling Managed Identity Tokens.
If the Docker artifact is started on `169.254.169.254`, the locally executed tests can keep using the same 
authentication method as in case of the production code (assuming that the production code is using Managed Identity 
tokens).

### Usage

#### Starting the container

Assumed Identity must use the `169.254.169.254` IP in order to replace the real Managed Identity mechanism with the fake
token provider. To achieve this you need to first create an appropriate network with Docker.

```
# One time setup
docker network create --subnet=169.254.169.0/24 assumed-id
```

Then you need to make sure to use the right IP when running the container.

```
docker run --net assumed-id --ip 169.254.169.254 --rm nagyesta/assumed-identity:<version>
```

Please find the list of available versions [here](https://hub.docker.com/r/nagyesta/assumed-identity/tags).

Once the container is started, you can test it by navigating to 
[http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://localhost/](http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://localhost/)

It should respond with a token similar to this:

```json
{"access_token":"dummy","expires_in":172800,"expires_on":1693250639,"refresh_token":"dummy","resource":"https://localhost/","token_type":1}
```

#### Examples

For complete examples of how it can be used in action, please feel free to visit the Lowkey Vault examples which can
be found [here](https://github.com/nagyesta/lowkey-vault#example-projects).

### Limitations

This tool was never tested on a VM running in Azure, but probably it wouldn't work, because of the real Instance 
MetaData Service which is already using this IP. Please note that this is not the intended use-case and won't be
supported.
