### Scope

This project contains a commandline toolset based on Python 3 and Python Zeep and allows OX Cloud compatible provisioning.

Most of the tools use the same equivalent names as the original OX server commandline tools and try to use the same parameters where possible.

### Disclaimer

There is no expectation at all that this toolset is complete and functional all the time. It's main purpose is to provide examples and concepts how the API is to be used.

In addition its main purpose is to manage the OX Cloud service while the concepts can be used for provisioning of standalone OX App Suite installations which have a smaller set of APIs though.


### Install Python Zeep

- Make sure you have a Python 3 interpreter on your system
- run pip install -r requirements.txt or install the requirements listed there using your OS package manager

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
