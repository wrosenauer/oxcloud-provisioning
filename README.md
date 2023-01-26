### Scope

This project contains a commandline toolset based on Python 3 and allows OX Cloud compatible provisioning via the REST-based Cloud API.

Most of the tools use the same equivalent names as the original OX server commandline tools and try to use the same parameters where possible.

### Disclaimer

There is no expectation at all that this toolset is complete and functional all the time. It's main purpose is to provide examples and concepts how the API is to be used.

The scripts are currently reimplemented for the new REST API but some scripts still rely on Python Zeep and the SOAP API. This is work in progress!


### Create a target.py

`target.py` must be created to contain the SOAP endpoint and credentials.

The file must contain the following variables:

```python
soapHost = "https://provisioning.eu.appsuite.cloud/"
login = "$BRANDADMIN"
password = "$BRANDPASSWORD"
restHost = "https://eu.appsuite.cloud/"
restPassword = "$TENANT_PASSWORD" # currently not used and can be empty
```

Optionally it can contain the following attributes:

```python
proxy = "$PROXY_ADDRESS"
verifyTls = False/True  # define if TLS host validation will be disabled (per default ON)
```
