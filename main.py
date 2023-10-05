import os

import constants as c
from config import Config
from wise_api import WiseAPI


def generate_statements(config: Config):
    API_KEY = os.getenv("API_KEY")
    if not API_KEY:
        raise RuntimeError("No API KEY found. Create a .env file based on .env.template and add your API key")

    wise_api = WiseAPI(API_KEY, c.ACCOUNT_BUSINESS)
    currencies = [c.CURRENCY_USD, c.CURRENCY_RON, c.CURRENCY_EUR]
    statements = wise_api.generate_statements(currencies, config.start_date, config.end_date)

    for currency, statement in statements.items():
        with open(os.path.join(config.output_dir, f"wise_{currency}.pdf"), "wb") as f:
            f.write(statement)


if __name__ == "__main__":
    config = Config.from_parser()

    if not os.path.isfile("./keys/wise-private.pem"):
        raise RuntimeError(
            "No private key found at: ./keys/wise-private.pem. Carefully read https://api-docs.wise.com/payouts#strong-customer-authentication-personal-token and add your private key"
        )

    generate_statements(config)
