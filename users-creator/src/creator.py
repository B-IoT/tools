# Copyright (c) 2021 BioT. All rights reserved.

import pandas as pd
import requests
import argparse
from decouple import config

SERVER_URL = "http://localhost:8080"


def is_valid(row):
    if any(row.isna()):
        return False

    username = row["username"].strip()
    if " " in username:
        return False

    return True

def create_user(session, row, user_id_created):
    if is_valid(row):
        user_id = row["user_id"].strip()
        print("Adding user with user_id = " + user_id + " ...")
        user = {
            "userID": user_id,
            "username": row["username"],
            "password": row["password"].strip(),
            "company": row["company"]
        }

        try:
            # Create
            create_req = session.post(f"{SERVER_URL}/oauth/register", json=user)
            create_req.raise_for_status()
            user_id_created.append(user_id)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)
    else:
        print(
            f"Error -> Skipping invalid row:\n{row}\nEmpty (or NaN) fields are not allowed, whitespaces are not allowed in the user_id.\n"
        )




if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""
        Given an Excel file, it creates the users (should NOT already exist) in the client's company database.
        The Excel file needs to have the following columns as header: user_id, username, password and company. All other columns are ignored.
        The header should start at the first row of the Excel.
        Empty fields are not allowed.
        Whitespaces are not allowed in user_id, username, password and company.
        """
    )
    parser.add_argument("file", metavar="file", type=str, help="the Excel file")
    parser.add_argument(
        "company", metavar="company", type=str, help="the client's company"
    )
    args = parser.parse_args()
    print("Welcome to the BioT users creator!\n")
    try:
        filename = args.file
        company = args.company
        columns = [
            "user_id",
            "username",
            "password",
            "company"
        ]
        df = pd.read_excel(filename, usecols=columns)

        with requests.Session() as s:
            print("Authenticating...")
            
            print("Creating users...")
            user_id_created = []
            df.apply(
                lambda row: create_user(s, row, user_id_created),
                axis=1,
            )

            if user_id_created:
                print(
                    f"Created {len(user_id_created)} users for company {company}:\n{user_id_created}\n"
                )

            print("Bye!")
    except FileNotFoundError:
        print("Error -> File not found!")
    except BaseException as e:
        print("Error ->", e.args[0])
