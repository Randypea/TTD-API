# About
A very thin wrapper around the The Trade Desk API.

- leverages `requests.Session`
  - reuses TCP connection
  - handles authentication headers and refreshes token on upon expiration

## Example usage

```python
from ttdapi import TTDClient


# You can choose sandbox with this parameter
# base_url="https://apisb.thetradedesk.com/v3/"
client = TTDClient(login=LOGIN, password=PWD, )

# consult the api docs for a valid payload example
payload = {
  "CampaignName": "Foo",
  "Description": "BARBAR"
}
#it's a requests.Session subclass
with client:
    created_camapign = client.create_campaign(payload)
    # A json with the created campaign details
print(created_campaign['Description'])
# "BARBAR"
```

## Extending
if the endpoint you need is not available make an issue or  or implement a method directly in `ttdapi.client.TTDClient` and make PR

## How to install

`pip install git+https://github.com/pocin/thetradingdesk-python-client`

### For development
```
$ git clone https://github.com/pocin/thetradingdesk-python-client
$ cd thetradingdesk-python-client
$ export TDD_USERNAME='foo' TDD_PASSWORD='bar'
$ python setup.py test
$ pip install . 
```
