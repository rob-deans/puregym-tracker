import os
import json

import requests
from dotenv import load_dotenv


class PuregymAPIClient:
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "PureGym/1523 CFNetwork/1312 Darwin/21.0.0",
    }
    authed = False
    home_gym_id = os.getenv("PUREGYM_GYM_ID")
    session = None
    BASE_URL = "https://capi.puregym.com/api/v1"
    AUTH_URL = "https://auth.puregym.com/connect/token"

    def login(self, email: str, pin: str, force_login: bool = False) -> None:
        if self.session is None:
            self.session = requests.session()

        self.auth_json = self.load_session()
        if not force_login and self.auth_json is not None:
            self.authed = True
            self.headers["Authorization"] = f"Bearer {self.auth_json['access_token']}"
            return

        data = {
            "grant_type": "password",
            "username": email,
            "password": pin,
            "scope": "pgcapi",
            "client_id": "ro.client",
        }

        response = self.session.post(self.AUTH_URL, headers=self.headers, data=data)

        response.raise_for_status()

        self.auth_json = response.json()

        self.authed = True
        self.headers["Authorization"] = f"Bearer {self.auth_json['access_token']}"
        self.save_session(self.auth_json)

    def get_home_gym(self) -> None:
        if not self.authed:
            return PermissionError("Not authed: call login(email, pin)")

        response = self.session.get(f"{self.BASE_URL}/member", headers=self.headers)
        response.raise_for_status()

        self.home_gym_id = response.json()["homeGymId"]
    
    def get_activity(self):
        if not self.authed:
            return PermissionError("Not authed: call login(email, pin)")

        response = self.session.get(f"{self.BASE_URL}/member/activity", headers=self.headers)
        response.raise_for_status()
        return response.json()


    def get_gym_attendance(self) -> int:
        if not self.authed:
            raise PermissionError("Not authed: call login(email, pin)")
        if self.home_gym_id is None:
            self.get_home_gym()

        response = self.session.get(
            f"{self.BASE_URL}/gyms/{self.home_gym_id}/attendance",
            headers=self.headers,
        )
        response.raise_for_status()

        return response.json()["totalPeopleInGym"]

    def save_session(self, auth_json) -> None:
        with open("session.json", "w") as f:
            json.dump(auth_json, f)

    def load_session(self) -> requests.Session:
        try:
            with open("session.json", "r") as f:
                self.authed = True
                return json.load(f)
        except FileNotFoundError as e:
            return None
