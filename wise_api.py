from typing import Any, Dict, Optional

from requests import request

import constants as c
from utils import strong_customer_authentication_decorator


class WiseAPI:

    BASE_URL = "https://api.transferwise.com"
    PROFILES_ENDPOINT = "/v1/profiles"
    BALANCE_ENDPOINT = "/v3/profiles/{profile-id}/balances"
    STATEMENT_ENDPOINT = "/v1/profiles/{profileId}/balance-statements/{balanceId}/statement.pdf"

    def __init__(self, api_key: str, profile_type: str = c.ACCOUNT_BUSINESS):
        self.api_key = api_key
        self.profile_type = profile_type
        self.profile_id = self.get_profile_id()

    def get_profile_id(self) -> int:
        url = self.BASE_URL + self.PROFILES_ENDPOINT
        response = self.make_request("GET", url).json()

        profile_id = [profile["id"] for profile in response if profile["type"] == self.profile_type][0]

        return profile_id

    def get_balance_ids(self) -> Dict[str, int]:
        balance_endpoint = self.BALANCE_ENDPOINT.format_map({"profile-id": self.profile_id})
        url = self.BASE_URL + balance_endpoint

        params = {"types": "STANDARD"}
        response = self.make_request("GET", url, params=params).json()

        balance_ids = {balance["currency"]: balance["id"] for balance in response}

        return balance_ids

    @strong_customer_authentication_decorator
    def download_statements(
        self, balance_id: int, type: str = c.STATEMENT_TYPE_ACCOUNTING, headers: Optional[Dict[str, str]] = None
    ):
        statement_endpoint = self.STATEMENT_ENDPOINT.format_map({"profileId": self.profile_id, "balanceId": balance_id})
        url = self.BASE_URL + statement_endpoint

        params = {"intervalStart": "2022-02-01T00:00:00.000Z", "intervalEnd": "2022-02-28T23:59:59.999Z", "type": type}
        result = self.make_request("GET", url, params=params, headers=headers, raise_for_status=False)

        return result

    def make_request(
        self,
        method: str,
        url,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
        raise_for_status: bool = True,
    ) -> Any:
        headers = headers or {}
        headers.update(self.get_headers())

        response = request(method, url, headers=headers, params=params)

        if raise_for_status:
            response.raise_for_status()

        return response

    def get_headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.api_key,
        }
