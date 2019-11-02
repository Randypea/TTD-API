# About
A very thin wrapper around the The Trade Desk API.  
I am using this to test what can be done.  RJP

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

# if an endpoint supports pagination (in POST )
# such as https://apisb.thetradedesk.com/v3/doc/api/post-adgroup-query-advertiser
# you can use
with client:
    advertisers = client.post_paginated(
        "advertiser/query/partner",
        json_payload={
            "Availabilities": ['Available', 'Archived'],
            'PartnerId': 'my_partner_id',
        }
    )
    # which will get all results in a (default) pageSize of 100
    # different pageSizes and pagesStartIndex can be used
    # client.post_paginated(endpoint, json_payload, page_start_index=1, page_size=42)
```

## Delta endpoints
hardcoded are adgroups and campaigns


```python

delta_adgroup_iterator = client.fetch_all_delta_adgroups_for_advertiser(advertiser_id='abc1234', last_change_tracking_version=None):

for adgroup, tracking_version in delta_adgroup_iterator:
    print(adgroup, tracking_version)
    
```
Under the hood this handles pagination since one call to delta-endpoint not necessarily returns all data but multplie calls might be required (utilizing the newly returned tracking versions)

There is equivalent `client.fetch_all_delta_campaigns_for_advertiser` function for campaigns

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
