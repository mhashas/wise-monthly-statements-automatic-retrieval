# Work in Progress

* Rename .env.template into .env and set your API key. Read https://api-docs.wise.com/payouts#wise-payouts-api-documentation-getting-started
* Add your private key under keys with the name wise-private.pem. Read https://api-docs.wise.com/payouts#strong-customer-authentication-personal-token
* In main.py define the currencies for which you want to extract pdf documents
* In wise_api.py download_statements function change to the date that you want

## Todo

* argument for output_dir
* generating start_date, end_date based on input argumenet automatically, i.e. feb -> generates 1feb -> 28 feb