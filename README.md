# FastAPI Simple Security via SQLModel

[![codecov](https://codecov.io/github/cwang/fastapi_sqlmodel_security/branch/main/graph/badge.svg?token=LHTBNHFVKK)](https://codecov.io/github/cwang/fastapi_sqlmodel_security)
[![Python Tests](https://github.com/cwang/fastapi_sqlmodel_security/actions/workflows/pr_python_tests.yml/badge.svg)](https://github.com/cwang/fastapi_sqlmodel_security/actions/workflows/pr_python_tests.yml)
[![Linting](https://github.com/cwang/fastapi_sqlmodel_security/actions/workflows/push_linting.yml/badge.svg)](https://github.com/cwang/fastapi_sqlmodel_security/actions/workflows/push_linting.yml)

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pre-commit enabled][pre-commit badge]][pre-commit project]
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-%23FE5196?logo=conventionalcommits&logoColor=white)](https://conventionalcommits.org)

[pre-commit badge]: <https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white>
[pre-commit project]: <https://pre-commit.com/>

(This is forked from [FastAPI Simple Security](https://github.com/mrtolkien/fastapi_simple_security/) with an SQLModel adaption. Credits to the original author!)

API key based security package for FastAPI, focused on simplicity of use:

- Full functionality out of the box, no configuration required
- API key security with local `sqlite` backend, working with both header and query parameters
- Default 15 days deprecation for generated API keys
- Key creation, revocation, renewing, and usage logs handled through administrator endpoints
- No dependencies, only requiring `FastAPI` and the python standard library

This module cannot be used for any kind of distributed deployment. It's goal is to help have some basic security features
for simple one-server API deployments, mostly during development.

## Installation

`pip install fastapi_sqlmodel_security`

### Usage

### Creating an application

The key is to configure an instance of [data store](./fastapi_sqlmodel_security/data_store.py), which can usually be done with `SqlModelDataStore` as shown below.

```python
from fastapi_sqlmodel_security import create_auth_router, ApiKeySecurity, DataStore, SqlModelDataStore
from fastapi import Depends, FastAPI

app = FastAPI()

data_store = SqlModelDataStore(conn_url="sqlite3:///keys.db")

app.include_router(create_auth_router(data_store), prefix="/auth", tags=["_auth"])

@app.get("/secure", dependencies=[Depends(ApiKeySecurity(data_store))])
async def secure_endpoint():
    return {"message": "This is a secure endpoint"}
```

Both the auth router and your own routes would need dependencies to be configured with the aforementioned data store.

Resulting app is:

![app](./images/auth_endpoints.png)

More can be found in the [demo app](./app/main.py). 

### API key creation through docs

Start your API and check the logs for the automatically generated secret key if you did not provide one through
environment variables.

![secret](./images/secret.png)

Go to `/docs` on your API and inform this secret key in the `Authorize/Secret header` box.
All the administrator endpoints only support header security to make sure the secret key is not inadvertently
shared when sharing an URL.

![secret_header](./images/secret_header.png)

Then, you can use `/auth/new` to generate a new API key.

![api key](./images/new_api_key.png)

And finally, you can use this API key to access the secure endpoint.

![secure endpoint](./images/secure_endpoint.png)

### API key creation in python

You can of course automate API key acquisition through python with `requests` and directly querying the endpoints.

If you do so, you can hide the endpoints from your API documentation with the environment variable
`FASTAPI_SQLMODEL_SECURITY_HIDE_DOCS`.

### Testing

You may want to use a *no-auth* api key security filter `NoAuthApiKeySecurity` as an alternative to the real filter. 

It does not do any key verification and will never block any requests, as long as they carry an API key of any value.

## Configuration

Environment variables:

- `FASTAPI_SQLMODEL_SECURITY_SECRET`: Secret administrator key

  - Generated automatically on server startup if not provided
  - Allows generation of new API keys, revoking of existing ones, and API key usage view
  - It being compromised compromises the security of the API

- `FASTAPI_SQLMODEL_SECURITY_HIDE_DOCS`: Whether or not to hide the API key related endpoints from the documentation

- `FASTAPI_SQLMODEL_SECURITY_AUTOMATIC_EXPIRATION`: Duration, in days, until an API key is deemed expired
  - 15 days by default

## Contributing

### Setting up python environment

```shell script
poetry install
poetry shell
```

### Setting up pre-commit hooks

```shell script
pre-commit install
```

### Running tests

```shell script
pytest
```

### Running the dev environment

The attached docker image runs a test app on `localhost:8080` with secret key `TEST_SECRET`. Run it with:

```shell script
docker-compose build && docker-compose up
```

## Needed contributions

- More options with sensible defaults
- Logging per API key?
- More back-end options for API key storage?
