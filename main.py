import os

import constants as c
from config import Config
from wise_api import WiseAPI


def generate_statements(config: Config):
    API_KEY = os.getenv("API_KEY")
    if not API_KEY:
        raise RuntimeError("No API KEY found. Create a .env file based on .env.template and add your API key")

    wise_api = WiseAPI(API_KEY, c.ACCOUNT_BUSINESS)

    balance_ids = wise_api.get_balance_ids()
    for currency in [c.CURRENCY_USD, c.CURRENCY_RON, c.CURRENCY_EUR]:
        print(f"Generating for {currency}")
        balance_id = balance_ids.get(currency)

        if not currency:
            print(f"No balance id found for {currency}")
            continue

        response = wise_api.download_statements(balance_id, config.start_date, config.end_date)

        if response.status_code != 200:
            raise RuntimeError(response.text)

        os.makedirs(config.output_dir, exist_ok=True)
        with open(os.path.join(config.output_dir, f"wise_{currency}.pdf"), "wb") as f:
            f.write(response.content)


if __name__ == "__main__":
    config = Config.from_parser()

    if not os.path.isfile("./keys/wise-private.pem"):
        raise RuntimeError(
            "No private key found at: ./keys/wise-private.pem. Carefully read https://api-docs.wise.com/payouts#strong-customer-authentication-personal-token and add your private key"
        )

    generate_statements(config)
