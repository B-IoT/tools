# Copyright (c) 2021 BIoT. All rights reserved.

import pandas as pd
import requests
import argparse
from decouple import config

SERVER_URL = "https://api.b-iot.ch:8080"
PASSWORD = config("PASSWORD")


def create_relay(session, row):
    relay = {
        "mqttID": row["relay_id"],
        "mqttUsername": row["username"],
        "mqttPassword": row["password"],
        "relayID": row["relay_id"],
        "ledStatus": True,
        "latitude": row["latitude"],
        "longitude": row["longitude"],
        "floor": row["floor"],
        "wifi": {"ssid": row["wifi_ssid"], "password": row["password"]},
    }

    try:
        r = session.post(f"{SERVER_URL}/api/relays", json=relay)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""
        Given an Excel file, it creates the relays in the client's company database.
        The Excel file need to have the following columns: relay_id, longitude, latitude, floor, username, 
        password, wifi_ssid, wifi_password. All other columns are ignored.
        """
    )
    parser.add_argument("file", metavar="file", type=str, help="the Excel file")
    parser.add_argument(
        "company", metavar="company", type=str, help="the client's company"
    )
    args = parser.parse_args()
    try:
        filename = args.file
        company = args.company
        columns = [
            "relay_id",
            "longitude",
            "latitude",
            "floor",
            "username",
            "password",
            "wifi_ssid",
            "wifi_password",
        ]
        df = pd.read_excel(filename, usecols=columns)

        with requests.Session() as s:
            print("Authenticating...")
            token = s.post(
                f"{SERVER_URL}/oauth/token",
                json={"username": f"biot_{company}", "password": PASSWORD},
            ).text
            s.headers.update({"Authorization": f"Bearer {token}"})
            print("Authentication succeeded")

            print("Creating relays...")
            df.apply(lambda row: create_relay(s, row), axis=1)

            print(f"Created {len(df.index)} relays for company {company}")
    except FileNotFoundError:
        print("Error -> File not found!")
    except BaseException as e:
        print("Error ->", e.args[0])
