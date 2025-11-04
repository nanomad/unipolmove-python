#!/usr/bin/env python3
"""
Unipol Move API Client Library
Provides programmatic access to Unipol Move API for toll movements and expense reports
"""

import json
import uuid
from datetime import datetime, date
from typing import List, Dict, Any, Optional
import requests


class UnipolMoveClient:
    """
    Client for Unipol Move API

    Handles authentication, movement fetching, and PDF report generation.
    """

    BASE_URL = "https://www.unipolmove.it"

    # API endpoints
    ENV_ENDPOINT = '/app/config/environment.json'
    MOVEMENTS_ENDPOINT = "/api/ut/prv/unipolmove/portale-tlpd/servizi-mobilita/v6/contratti/{contract_id}/movimenti"
    PDF_ENDPOINT = "/api/us/prv/tpd/telepedaggio-us/post-vendita/v1/contratti/{contract_id}/movimenti/stampa"
    LOGIN_ENDPOINT = "/login"

    def __init__(self, contract_id: str, mrh_session: Optional[str] = None,
                 last_mrh_session: Optional[str] = None,
                 session_id: Optional[str] = None):
        """
        Initialize the client

        Args:
            contract_id: Your Unipol Move contract ID (e.g., 'P000000000')
            mrh_session: MRHSession cookie value (optional if using login())
            last_mrh_session: LastMRH_Session cookie value (optional if using login())
            session_id: Optional X-UNIPOL-SESSIONID (will be generated if not provided)
        """
        self.contract_id = contract_id
        self.mrh_session = mrh_session
        self.last_mrh_session = last_mrh_session
        self.session_id = session_id or str(uuid.uuid4())
        env_config = requests.get(self.BASE_URL + self.ENV_ENDPOINT).json()
        self.movements_client_id = env_config['apiConnect']['headers_ut_prv_mobility_service']['x-ibm-client-id']
        self.movements_client_secret = env_config['apiConnect']['headers_ut_prv_mobility_service']['x-ibm-client-secret']
        self.pdf_client_id = env_config['apiConnect']['headers_us']['x-ibm-client-id']
        self.pdf_client_secret = env_config['apiConnect']['headers_us']['x-ibm-client-secret']

    def _get_headers(self, client_id: str, client_secret: str,
                     referer: str = None) -> Dict[str, str]:
        """Generate request headers"""
        headers = {
            "Accept": "application/json",
            "Accept-Language": "it-IT,it;q=0.8,en-US;q=0.5,en;q=0.3",
            "X-UNIPOL-REQUESTID": str(uuid.uuid4()),
            "X-UNIPOL-SEQUENCEID": "0",
            "X-UNIPOL-SESSIONID": self.session_id,
            "x-ibm-client-id": client_id,
            "x-ibm-client-secret": client_secret,
            "X-UNIPOL-CANALE": "WEB",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:144.0) Gecko/20100101 Firefox/144.0",
        }
        if referer:
            headers["Referer"] = referer
        return headers

    def _get_cookies(self) -> Dict[str, str]:
        """Generate request cookies"""
        return {
            "MRHSession": self.mrh_session,
            "LastMRH_Session": self.last_mrh_session,
            "isLogged": "true"
        }

    def login(self, username: str, password: str) -> bool:
        """
        Authenticate and obtain session cookies

        Args:
            username: Your Unipol Move username (email)
            password: Your Unipol Move password

        Returns:
            True if login successful, False otherwise

        Raises:
            requests.exceptions.HTTPError: If login fails
        """
        login_url = f"{self.BASE_URL}{self.LOGIN_ENDPOINT}"

        # Login endpoint doesn't use client ID/secret
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "it-IT,it;q=0.8,en-US;q=0.5,en;q=0.3",
            "X-UNIPOL-REQUESTID": str(uuid.uuid4()),
            "X-UNIPOL-SEQUENCEID": "0",
            "X-UNIPOL-SESSIONID": self.session_id,
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:144.0) Gecko/20100101 Firefox/144.0",
            "Referer": "https://www.unipolmove.it/app/login"
        }

        data = {
            "username": username,
            "password": password
        }

        response = requests.post(login_url, headers=headers, data=data)
        response.raise_for_status()

        # Extract cookies from response
        cookies = response.cookies
        if "MRHSession" in cookies and "LastMRH_Session" in cookies:
            self.mrh_session = cookies["MRHSession"]
            self.last_mrh_session = cookies["LastMRH_Session"]
            return True
        else:
            return False

    def fetch_movements(self,
                       offset: int = 1,
                       limit: int = 100,
                       interval: str = "ULTIMO_ANNO",
                       order_by: str = "date-D",
                       payment_status: str = "0,1,3,4") -> Dict[str, Any]:
        """
        Fetch toll movements from the API

        Args:
            offset: Starting offset for pagination (default: 1)
            limit: Maximum number of records to fetch (default: 100)
            interval: Time interval (default: 'ULTIMO_ANNO' = last year)
            order_by: Sorting order (default: 'date-D' = date descending)
            payment_status: Payment status filter (default: '0,1,3,4')
                           0=DA_ADDEBITARE, 1=ADDEBITATO, 3=?, 4=?

        Returns:
            Dictionary containing the API response with 'dispositivi' and 'listaMovimenti'
        """
        url = self.BASE_URL + self.MOVEMENTS_ENDPOINT.format(contract_id=self.contract_id)

        params = {
            "offset": offset,
            "limite": limit,
            "intervallo": interval,
            "ordinaPer": order_by,
            "statoPagamento": payment_status
        }

        response = requests.get(
            url,
            headers=self._get_headers(
                self.movements_client_id,
                self.movements_client_secret,
                "https://www.unipolmove.it/app/post-vendita/homepage/movements"
            ),
            cookies=self._get_cookies(),
            params=params
        )

        response.raise_for_status()
        return response.json()

    def fetch_all_movements(self,
                           batch_size: int = 100,
                           interval: str = "ULTIMO_ANNO") -> List[Dict[str, Any]]:
        """
        Fetch all toll movements with automatic pagination

        Args:
            batch_size: Number of records to fetch per request (default: 100)
            interval: Time interval (default: 'ULTIMO_ANNO')

        Returns:
            List of all movements
        """
        all_movements = []
        offset = 1

        while True:
            response = self.fetch_movements(
                offset=offset,
                limit=batch_size,
                interval=interval
            )

            movements = response.get("listaMovimenti", [])

            if not movements:
                break

            all_movements.extend(movements)

            # If we got fewer results than the batch size, we've reached the end
            if len(movements) < batch_size:
                break

            offset += batch_size

        return all_movements

    def generate_pdf_report(self,
                           movements: List[Dict[str, Any]],
                           intestatario: str,
                           output_filename: Optional[str] = None) -> bytes:
        """
        Generate PDF expense report for selected movements

        Args:
            movements: List of movement dictionaries to include in the report
            intestatario: Name to display as the report recipient/header
            output_filename: Optional filename to save the PDF (if None, returns bytes only)

        Returns:
            PDF file content as bytes

        Raises:
            requests.exceptions.HTTPError: If PDF generation fails
        """
        url = self.BASE_URL + self.PDF_ENDPOINT.format(contract_id=self.contract_id)

        # Add 'checked: true' and 'id' fields to movements for the API
        movements_with_check = []
        for idx, movement in enumerate(movements):
            movement_copy = movement.copy()
            movement_copy['checked'] = True
            movement_copy['id'] = str(idx)
            movements_with_check.append(movement_copy)

        payload = {
            "intestatario": intestatario,
            "listaMovimenti": movements_with_check
        }

        response = requests.post(
            url,
            headers=self._get_headers(
                self.pdf_client_id,
                self.pdf_client_secret,
                "https://www.unipolmove.it/app/post-vendita/homepage/movements"
            ),
            cookies=self._get_cookies(),
            json=payload
        )

        response.raise_for_status()

        # Save to file if filename provided
        if output_filename:
            with open(output_filename, 'wb') as f:
                f.write(response.content)

        return response.content

    def filter_movements_by_date(self,
                                movements: List[Dict[str, Any]],
                                start_date: date,
                                end_date: date) -> List[Dict[str, Any]]:
        """
        Filter movements by date range

        Args:
            movements: List of movement dictionaries
            start_date: Start date (inclusive)
            end_date: End date (inclusive)

        Returns:
            Filtered list of movements within the date range
        """
        filtered_movements = []

        for movement in movements:
            # Try dataIngresso first, fallback to dataUscita
            movement_date_str = movement.get("dataIngresso") or movement.get("dataUscita", "")
            if movement_date_str:
                try:
                    # Handle various date formats
                    if "T" in movement_date_str:
                        movement_date = datetime.fromisoformat(
                            movement_date_str.replace("Z", "+00:00")
                        ).date()
                    else:
                        movement_date = datetime.strptime(movement_date_str, "%Y-%m-%d").date()

                    # Check if movement is within date range
                    if start_date <= movement_date <= end_date:
                        filtered_movements.append(movement)
                except (ValueError, AttributeError):
                    # If date parsing fails, skip the movement
                    pass

        return filtered_movements
