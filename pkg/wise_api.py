from typing import ByteString, Dict, List, Optional, Union

import pkg.constants as c
from requests import Response, request
from pkg.utils import strong_customer_authentication_decorator


class WiseAPI:
    BASE_URL = "https://api.transferwise.com"
    PROFILES_ENDPOINT = "/v1/profiles"
    BALANCE_ENDPOINT = "/v3/profiles/{profile-id}/balances"
    STATEMENT_ENDPOINT = "/v1/profiles/{profileId}/balance-statements/{balanceId}/statement.pdf"

    def __init__(self, api_key: str, profile_type: str = c.ACCOUNT_BUSINESS):
        """Initializes the class by retrieving the profile id from the API key

        Args:
            api_key (str): wise API key
            profile_type (str): either business or personal
        """
        self.api_key = api_key
        self.profile_type = profile_type
        self.profile_id = self.get_profile_id()

    def get_profile_id(self) -> int:
        """Loads and returns the profile id for the associated account

        Returns:
            int: profile id
        """
        url = self.BASE_URL + self.PROFILES_ENDPOINT
        response = self.make_request(c.REQUEST_GET, url).json()

        profile_id = [profile["id"] for profile in response if profile["type"] == self.profile_type][0]

        return profile_id

    def get_balance_ids(self) -> Dict[str, int]:
        """Loads and returns the balance ids for the associated account"

        Returns:
            Dict[str, int]: keys are currencies, values are balance ids
        """
        balance_endpoint = self.BALANCE_ENDPOINT.format_map({"profile-id": self.profile_id})
        url = self.BASE_URL + balance_endpoint

        params = {"types": "STANDARD"}
        response = self.make_request(c.REQUEST_GET, url, params=params).json()

        balance_ids = {balance["currency"]: balance["id"] for balance in response}

        return balance_ids

    def generate_statements(
        self,
        currencies: Union[int, List[int]],
        start_date: str,
        end_date: str,
    ) -> Dict[str, ByteString]:
        """Generates and returns the statements for the given currency(es)

        Args:
            currencies (currencies: Union[int, List[int]]): currency(es) for which we are generating statements
            start_date (str): statements start date
            end_date (str): statements end date

        Returns:
            Dict[str, ByteString]: keys are currencies, values are pdf contents in bytestring
        """
        if not isinstance(currencies, list):
            currencies = [currencies]

        statements = {currency: None for currency in currencies}
        balance_ids = self.get_balance_ids()

        for currency in currencies:
            balance_id = balance_ids.get(currency)

            if not balance_id:
                print(f"No balance id found for {currency}")
                continue

            response = self._generate_statement(balance_id, start_date, end_date)
            
            statements[currency] = response.content

        return statements

    @strong_customer_authentication_decorator
    def _generate_statement(
        self,
        balance_id: int,
        start_date: str,
        end_date: str,
        type: str = c.STATEMENT_TYPE_ACCOUNTING,
        headers: Optional[Dict[str, str]] = None,
    ) -> Response:
        """Downloads a statement using the Wise API and returns it

        Args:
            balance_id (int): id of the balance for which we are downloading the statement
            start_date (str): statement start date
            end_date (str): statement end date
            type (str): type of statement we want to generate
            headers (Optional[Dict[str, str]]): extra headers we might need to send

        Returns:
            Response: request
        """
        statement_endpoint = self.STATEMENT_ENDPOINT.format_map({"profileId": self.profile_id, "balanceId": balance_id})
        url = self.BASE_URL + statement_endpoint

        params = {"intervalStart": start_date, "intervalEnd": end_date, "type": type}
        response = self.make_request(c.REQUEST_GET, url, params=params, headers=headers, raise_for_status=False)

        return response

    def make_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
        raise_for_status: bool = True,
    ) -> Response:
        """Performs a request to the Wise API and returns the response

        Args:
            method (str): one of the available request methods: "GET", "POST", etc.
            url (str): where to make the request
            headers (Optional[Dict[str, str]]): headers the request should send
            params (Optional[Dict[str, str]]): params the request should send
            raise_for_status (bool): whether to raise HTTPError if it occures

        Returns:
            Response: the response associated with the request
        """
        headers = headers or {}
        headers.update(self.get_headers())

        response = request(method, url, headers=headers, params=params)

        if raise_for_status:
            response.raise_for_status()

        return response

    def get_headers(self) -> Dict[str, str]:
        """Builds and returns the headers required by the Wise API

        Returns:
            Dict[str, str]: wise api headers
        """
        return {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.api_key,
        }
