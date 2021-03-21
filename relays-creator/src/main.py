# Copyright (c) 2021 BIoT. All rights reserved.

import pandas as pd
import requests
import argparse
import sys

SERVER_URL = "https://api.b-iot.ch:8080"


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

    session.post(f"{SERVER_URL}/api/relays", json=relay)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""
        Given an Excel file, it creates the relays in the client's company database.
        The Excel file need to have the following columns: relay_id, longitude, latitude, floor, username,
        password, wifi_ssid, wifi_password.
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
        df = pd.read_excel(
            filename,
            usecols=[
                "relay_id",
                "longitude",
                "latitude",
                "floor",
                "username",
                "password",
                "wifi_ssid",
                "wifi_password",
            ],
        )

        with requests.Session() as s:
            print("Authenticating...")
            token = s.post(
                f"{SERVER_URL}/oauth/token",
                json={"username": f"biot_{company}", "password": "biot"},
            ).text
            s.headers.update({"Authorization": f"Bearer {token}"})
            print("Authentication succeeded")

            print("Creating relays...")
            df.apply(lambda row: create_relay(s, row), axis=1)
            print(f"Created {len(df.index)} relays for company {company}")
    except FileNotFoundError:
        print("Error: file not found!")
    except:
        print("Unexpected error: ", sys.exc_info()[0])
