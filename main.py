import time
import logging
import requests
from config import (
    sync_file_url,
    base_url,
    lights_uniqueIds,
    POLLING_INTERVAL,
    homebridge_username,
    homebridge_password,
)


class HomeBridgeController:
    def __init__(self):
        self.base_url = base_url
        self.auth_token = self.authenticate()

    def make_request(self, method, url, **kwargs):
        try:
            response = method(url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Request to {url} failed with error: {e}")
            if response.status_code == 401:
                # If the response status code is 401 (Unauthorized), re-authenticate
                logging.info("Re-authenticating...")
                self.auth_token = self.authenticate()  # Re-authenticate
                # Retry the request with the new token
                kwargs['headers'] = {"Authorization": f"Bearer {self.auth_token}"}
                response = method(url, **kwargs)
                response.raise_for_status()
                return response.json()
            else:
                logging.error("Non-401 error encountered. Request cannot be retried.")
                return None

    def authenticate(self):
        payload = {"username": homebridge_username, "password": homebridge_password}
        data = self.make_request(
            requests.post, f"{self.base_url}/api/auth/login", json=payload
        )
        if data is None:
            raise Exception("Failed to authenticate")
        return data.get("access_token")

    @staticmethod
    def is_phone_home():
        for _ in range(3):
            try:
                response = requests.get(sync_file_url)
                response.raise_for_status()
                return response.text.split("\n")[-1].strip() == "1"
            except requests.exceptions.RequestException as e:
                logging.error(f"Request failed with {e}, retrying...")
                time.sleep(1)
        logging.error("Failed to fetch phone home status after 3 attempts.")
        return False

    def get_accessories(self):
        return self.make_request(
            requests.get,
            f"{self.base_url}/api/accessories",
            headers={"Authorization": f"Bearer {self.auth_token}"},
        )

    def set_accessory_value(self, unique_id, characteristic_type, value):
        payload = {"characteristicType": characteristic_type, "value": value}
        response = self.make_request(
            requests.put,
            f"{self.base_url}/api/accessories/{unique_id}",
            headers={"Authorization": f"Bearer {self.auth_token}"},
            json=payload,
        )
        return response is not None

    def save_light_states(self, accessories):
        return {
            acc["uniqueId"]: acc["values"]["On"]
            for acc in accessories
            if acc.get("uniqueId") in lights_uniqueIds
        }

    def restore_lights(self, light_states):
        for uniqueId, state in light_states.items():
            self.set_accessory_value(uniqueId, "On", state)

    def turn_off_lights(self):
        for uniqueId in lights_uniqueIds:
            self.set_accessory_value(uniqueId, "On", False)


if __name__ == "__main__":
    time.sleep(30)
    logging.basicConfig(
        filename="app.log",
        filemode="w",
        format="%(name)s - %(levelname)s - %(message)s",
        level=logging.DEBUG,
    )
    controller = HomeBridgeController()
    light_states = {}
    old_phone_is_home = None
    while True:
        accessories = controller.get_accessories()
        if not accessories:
            logging.info("Accessories could not be fetched. Retrying...")
            time.sleep(1)
            continue

        phone_is_home = controller.is_phone_home()
        if phone_is_home != old_phone_is_home:
            if phone_is_home:
                logging.info("phone arrived home.")
                controller.restore_lights(light_states)
            else:
                logging.info("phone left home.")
                light_states = controller.save_light_states(accessories)
                controller.turn_off_lights()

            old_phone_is_home = phone_is_home

        time.sleep(POLLING_INTERVAL)
