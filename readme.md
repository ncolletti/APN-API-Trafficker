# Appnexus API SCRIPT**

>Traffic IO, LI, Creatives for a Prebid Header Bidding configuration with Appnexus Ad Server.

## How to run 💻
* Python3 required
* dependency: pip install python-dotenv
* Add your Appnexus credentials in a .env along with specifics: (Pub name, adv id, bidder list, placement id to target)
* Adjust line_items.yaml to match your desired config of line items and creative sizes
* run apn.py

## **TO DO**
* Add category trafficking and apply to campaign? Or just use profiles to target placements?
* Fix DRY in traffic_key_value function and traffic_campaign and traffic line item functions
* Logging. Log events. Log results and display when complete
* Refactor into classes/oop?

## Questions
* key value targeting API does not accept id targeting?!

## Completed
* Error handling for false return from api_wrapper
* Fix DRY of grabbing response data with .json()
* Need to add trailing zero to float in line items
* Handle if keys/objects already exists (check_existence_key created. Need to add to check in trafficking function)
* Create a content category/profile service for placement targeting for all campaigns for key value
* Add targeting key trafficking
* Error Handling - try excepts with responses from API
* For each Line Item need to associate a creative and key to it. Create a dict map
* Allow for api calls to check 429 response call and wait for the retry-after field if needed [LINK](https://wiki.appnexus.com/display/api/API+Best+Practices#APIBestPractices-Throttleyourcalls)
* Check for successful status responses