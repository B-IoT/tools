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


def create_relay(session, row, ids_created):
    if is_valid(row):
        relay_id = row["relay_id"].strip()
        relay = {
            "mqttID": relay_id,
            "relayID": relay_id,
            "ledStatus": True,
            "latitude": float(row["latitude"]),
            "longitude": float(row["longitude"]),
            "floor": int(row["floor"]),
            "wifi": {
                "ssid": str(row["wifi_ssid"]).strip(),
                "password": str(row["wifi_password"]).strip(),
                "reset": False
            },
            "reboot": False,
            "forceReset": False,
        }

        try:
            # Create
            create_req = session.post(f"{SERVER_URL}/api/relays", json=relay)
            create_req.raise_for_status()
            ids_created.append(relay_id)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)
    else:
        print(
            f"Error -> Skipping invalid row:\n{row}\nEmpty (or NaN) fields are not allowed, whitespaces are not allowed in the relay_id, and latitude and longitude need to be different from 0.\nRelayID must not already exist in the DB."
        )

def delete_all_relays(session, company):
    try:
        get_req = session.get(f"{SERVER_URL}/api/relays")
        get_req.raise_for_status()

        json = get_req.json()
    except Exception as e:
        print(f"Cannot get relays from the DB: {e}")

    ids_to_delete = []
    for e in json:
        id_to_delete = e["relayID"]
        if id_to_delete != "relay_0" and id_to_delete != "relay_biot":
            ids_to_delete.append(e["relayID"])
    print(f"IDs of items that will be deleted: {ids_to_delete}")

    try:
        for id in ids_to_delete:
            create_req = session.delete(f"{SERVER_URL}/api/relays/{id}")
            create_req.raise_for_status()
    except Exception as e:
        print(f"Cannot delete at least one relay from the DB: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""
        Given an Excel file, it creates (or updates if already present) the relays in the client's company database.
        The Excel file need to have the following columns as header: relay_id, longitude, latitude, floor, wifi_ssid, wifi_password. 
        All other columns are ignored.
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
    parser.add_argument('--delete', dest='delete', action='store_const',
                    const=True, default=False,
                    help='Delete all relays (except relay_0 and relay_biot) from the DB before adding the new relays (default: False)')
    args = parser.parse_args()
    print("Welcome to the BioT relays creator!\n")
    try:
        filename = args.file
        company = args.company
        delete = args.delete
        columns = [
            "relay_id",
            "longitude",
            "latitude",
            "floor",
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

            if delete:
                confirmation = input(f"WARNING: this operation will delete all relays from the DB for the company '{company}'! Are you sure you want to continue? [y/N]: ")
                if confirmation == "y" or confirmation == "Y":
                    print(f"Deleting all relays from DB of company '{company}'")
                    delete_all_relays(s, company)
                    print(f"Done! Deleted all relays from DB of company '{company}'")
                else:
                    print("Okay, exiting...")
                    exit()

            print("Creating relays...")
            ids_created = []
            df.apply(
                lambda row: create_relay(s, row, ids_created),
                axis=1,
            )

            if ids_created:
                print(
                    f"Created {len(ids_created)} relays for company '{company}':\n{ids_created}\n"
                )

            print("Bye!")
    except FileNotFoundError:
        print("Error -> File not found!")
    except BaseException as e:
        print("Error ->", e.args[0])
