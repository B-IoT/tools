# Copyright (c) 2021 BIoT. All rights reserved.

import pandas as pd
import requests
import argparse
from decouple import config

SERVER_URL = "https://api.b-iot.ch:8080"
PASSWORD = config("PASSWORD")


def is_valid(row):
    relay_id = row["relay_id"].strip()
    if " " in relay_id:
        return False

    if float(row["latitude"]) == 0 or float(row["longitude"]) == 0:
        return False

    return True


def create_relay(session, row):
    if is_valid(row):
        relay_id = row["relay_id"].strip()
        relay = {
            "mqttID": relay_id,
            "mqttUsername": row["username"].strip(),
            "mqttPassword": row["password"].strip(),
            "relayID": relay_id,
            "ledStatus": True,
            "latitude": row["latitude"],
            "longitude": row["longitude"],
            "floor": row["floor"],
            "wifi": {
                "ssid": row["wifi_ssid"].strip(),
                "password": row["password"].strip(),
            },
        }

        try:
            r = session.post(f"{SERVER_URL}/api/relays", json=relay)
            r.raise_for_status()
            count_created += 1
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)
    else:
        print(
            f"Error -> Skipping invalid row:\n{row}\nWhitespaces are not allowed in the relay_id, and latitude and longitude need to be different from 0\n"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""
        Given an Excel file, it creates the relays in the client's company database.
        The Excel file need to have the following columns: relay_id, longitude, latitude, floor, username, 
        password, wifi_ssid, wifi_password. All other columns are ignored.
        Whitespace are not allowed in relay_id, and latitude and longitude need to be different from 0.
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
            print("Authentication succeeded\n")

            print("Creating relays...")
            count_created = 0
            df.apply(lambda row: create_relay(s, row), axis=1)

            print(f"Created {count_created} relays for company {company}")
    except FileNotFoundError:
        print("Error -> File not found!")
    except BaseException as e:
        print("Error ->", e.args[0])
