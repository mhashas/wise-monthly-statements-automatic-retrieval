import os

import constants as c
from wise_api import WiseAPI
from config import Config


def generate_statements(config):
    API_KEY = os.getenv("API_KEY")
    wise_api = WiseAPI(API_KEY, c.ACCOUNT_BUSINESS)
    
    balance_ids = wise_api.get_balance_ids() 
    for currency in [c.CURRENCY_USD, c.CURRENCY_RON, c.CURRENCY_EUR]:
        print(f"Generating for {currency}")
        balance_id = balance_ids.get(currency)

        if not currency:
            print(f"No balance id found for {currency}")
            continue

        response = wise_api.download_statements(balance_id, config.start_date, config.end_date)
        
        os.makedirs(config.output_dir, exist_ok=True)
        with open(os.path.join(config.output_dir, f"wise_{currency}.pdf"), 'wb') as f:
            f.write(response.content)

if __name__ == "__main__":
    config = Config.from_parser()
    generate_statements(config)
