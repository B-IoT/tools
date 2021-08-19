# Copyright (c) 2021 BioT. All rights reserved.

import pandas as pd
import requests
import argparse
from decouple import config

SERVER_URL = "https://api.b-iot.ch:443"
PASSWORD = config("PASSWORD")


def is_valid(row):
    if any(row.isna()):
        return False

    relay_id = row["relay_id"].strip()
    if " " in relay_id:
        return False

    if float(row["latitude"]) == 0 or float(row["longitude"]) == 0:
        return False

    return True


def create_or_update_relay(session, row, ids_created, ids_updated):
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
            "floor": int(row["floor"]),
            "wifi": {
                "ssid": row["wifi_ssid"].strip(),
                "password": row["wifi_password"].strip(),
            },
        }

        try:
            # First check if it already exists
            get_req = session.get(f"{SERVER_URL}/api/relays/{relay_id}")
            if get_req.status_code == 200:
                # If yes, update
                # We need to remove the password, otherwise it will overwrite the encrypted one already stored
                update_relay = relay.copy()
                update_relay.pop("mqttPassword")
                update_req = session.put(
                    f"{SERVER_URL}/api/relays/{relay_id}", json=update_relay
                )
                update_req.raise_for_status()
                ids_updated.append(relay_id)
            else:
                # Otherwise, create
                create_req = session.post(f"{SERVER_URL}/api/relays", json=relay)
                create_req.raise_for_status()
                ids_created.append(relay_id)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)
    else:
        print(
            f"Error -> Skipping invalid row:\n{row}\nEmpty (or NaN) fields are not allowed, whitespaces are not allowed in the relay_id, and latitude and longitude need to be different from 0.\n"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""
        Given an Excel file, it creates (or updates if already present) the relays in the client's company database.
        The Excel file need to have the following columns as header: relay_id, longitude, latitude, floor, username, 
        password, wifi_ssid, wifi_password. All other columns are ignored.
        The header should start at the first row of the Excel.
        Empty fields are not allowed.
        Whitespaces are not allowed in relay_id.
        Latitude and longitude need to be different from 0.
        """
    )
    parser.add_argument("file", metavar="file", type=str, help="the Excel file")
    parser.add_argument(
        "company", metavar="company", type=str, help="the client's company"
    )
    args = parser.parse_args()
    print("Welcome to the BioT relays creator!\n")
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

            print("Creating (or updating) relays...")
            ids_created = []
            ids_updated = []
            df.apply(
                lambda row: create_or_update_relay(s, row, ids_created, ids_updated),
                axis=1,
            )

            if ids_created:
                print(
                    f"Created {len(ids_created)} relays for company {company}:\n{ids_created}\n"
                )

            if ids_updated:
                print(
                    f"Updated {len(ids_updated)} relays for company {company}:\n{ids_updated}\n"
                )

            print("Bye!")
    except FileNotFoundError:
        print("Error -> File not found!")
    except BaseException as e:
        print("Error ->", e.args[0])
