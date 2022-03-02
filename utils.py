import functools
import subprocess
from typing import Callable

import constants as c


def generate_signature(one_time_token: str) -> str:
    """Generates the authentication signature based on the one-time-token. Assumes wise-private.pem is under "./keys"

    For more information, have a look at: https://api-docs.wise.com/payouts#strong-customer-authentication-personal-token

    Args:
        one_time_token (str): token for which we are generating the signature

    Returns:
        str: generated signature
    """
    token_command = f"printf {one_time_token}"
    tokken_result = subprocess.run(token_command.split(), stdout=subprocess.PIPE)

    open_ssl_command = "openssl sha256 -sign ./keys/wise-private.pem"
    open_ssl_result = subprocess.run(open_ssl_command.split(), input=tokken_result.stdout, stdout=subprocess.PIPE)

    base64_command = "base64"
    base64_result = subprocess.run(base64_command.split(), input=open_ssl_result.stdout, stdout=subprocess.PIPE)

    signature = base64_result.stdout.decode("utf-8").strip()

    return signature


def strong_customer_authentication_decorator(api_call: Callable) -> Callable:
    """Decorator that performs the given api call which will fail, grabs the one-time-token from the response,
    generates the signature and then performs the api_call again with the given signature

    Args:
        api_call (Callable): call to execute

    Returns:
        Callable: wrapped function
    """

    @functools.wraps(api_call)
    def wrapper(*args, **kwargs):
        result = api_call(*args, **kwargs)

        if result.status_code == 200:
            return result

        one_time_token = result.headers[c.ONE_TIME_TOKEN_HEADER]
        signature = generate_signature(one_time_token)
        headers = {c.ONE_TIME_TOKEN_HEADER: one_time_token, c.ONE_TIME_TOKEN_SIGNATURE_HEADER: signature}
        
        result = api_call(*args, headers=headers, **kwargs)

        return result

    return wrapper
