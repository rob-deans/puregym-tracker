import os

from dotenv import load_dotenv
import requests
import paho.mqtt.publish as publish

from puregym import PuregymAPIClient

load_dotenv()
EMAIL = os.getenv("PUREGYM_EMAIL")
PIN = os.getenv("PUREGYM_PIN")
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
BROKER_IP = os.getenv("BROKER_IP")


def main() -> None:
    client = PuregymAPIClient()
    client.login(EMAIL, PIN, force_login=False)
    gym_attendance = None
    try:
        gym_attendance = client.get_gym_attendance()
    except requests.exceptions.HTTPError as e:
        # Attempt to re-login once if the token runs out
        if e.response.status_code == 401:
            client.login(EMAIL, PIN, force_login=True)
            gym_attendance = client.get_gym_attendance()

    if gym_attendance is not None:
        # Publish message
        print("Publishing")
        publish.single(
            topic="puregym/count/marylebone",
            payload=gym_attendance,
            hostname=BROKER_IP,
            qos=1,
            auth={"username": MQTT_USERNAME, "password": MQTT_PASSWORD},
        )
    return gym_attendance


if __name__ == "__main__":
    print(main())
