import os

import constants as c
from wise_api import WiseAPI


def generate_statements():
    API_KEY = os.getenv("API_KEY")
    wise_api = WiseAPI(API_KEY, c.ACCOUNT_BUSINESS)
    
    balance_ids = wise_api.get_balance_ids() 
    for currency in [c.CURRENCY_USD, c.CURRENCY_RON, c.CURRENCY_EUR]:
        print(f"Generating for {currency}")
        balance_id = balance_ids.get(currency)

        if not currency:
            print(f"No balance id found for {currency}")
            continue

        response = wise_api.download_statements(balance_id)
        with open(f"wise_{currency}.pdf", 'wb') as f:
            f.write(response.content)

if __name__ == "__main__":
    generate_statements()
