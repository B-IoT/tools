# Copyright (c) 2021 BioT. All rights reserved.

import pandas as pd
import requests
import argparse
from decouple import config
import re

SERVER_URL = "https://api.b-iot.ch:8080"
PASSWORD = config("PASSWORD")


def is_valid(row):
    # if any(row.isna()):
    #     return False

    beacon = row["beacon"]
    category = row["category"]
    service = row["service"]
    itemID = row["itemID"]
    brand = row["brand"]
    model = row["model"]
    supplier = row["supplier"]
    purchaseDate = row["purchaseDate"]
    purchasePrice = row["purchasePrice"]
    originLocation = row["originLocation"]
    currentLocation = row["currentLocation"]
    room = row["room"]
    contact = row["contact"]
    currentOwner = row["currentOwner"]
    previousOwner = row["previousOwner"]
    orderNumber = row["orderNumber"]
    color = row["color"]
    serialNumber = row["serialNumber"]
    maintenanceDate = row["maintenanceDate"]
    comments = row["comments"]

    if pd.isna(itemID) or re.search(r"\s", str(itemID)):
        print(f'itemID does not match the required format. Found: {itemID}')
        return False
    if pd.isna(category):
        print(f'category does not match the required format. Found: {category}')
        return False
    if not re.match("[a-z][a-z]:[a-z][a-z]:[a-z][a-z]:[a-z][a-z]:[a-z][a-z]:[a-z][a-z]", beacon):
        print(f'beacon does not match the required format. Found: {beacon}')
        return False
    if not pd.isna(purchaseDate) and not re.match("[0-9]{4}-[0-9]{2}-[0-9]{2}", purchaseDate):
        print(f'purchaseDate does not match the required format. Found: {purchaseDate}')
        return False
    if not pd.isna(maintenanceDate) and not re.match("[0-9]{4}-[0-9]{2}-[0-9]{2}", maintenanceDate):
        print(f'purchaseDate does not match the required format. Found: {maintenanceDate}')
        return False
    
    try:
        float(purchasePrice)
    except:
        print(f'purchasePrice does not match the required format. Found: {purchasePrice}, required: a float number.')
        return False

    return True

def create_item(session, row, item_id_created, company):
    if is_valid(row):
        item_id = row["itemID"].strip()
        print("Adding item with itemID = " + item_id + " ...")

        beacon = row["beacon"]
        category = row["category"]
        service = "" if pd.isna(row["service"]) else row["service"]
        itemID = row["itemID"]
        brand = "" if pd.isna(row["brand"]) else row["brand"]
        model = "" if pd.isna(row["model"]) else row["model"]
        supplier = "" if pd.isna(row["supplier"]) else row["supplier"]
        purchaseDate = "1900-01-01" if pd.isna(row["purchaseDate"]) else row["purchaseDate"]
        purchasePrice = 0.0 if pd.isna(row["purchasePrice"]) else row["purchasePrice"]
        originLocation = "" if pd.isna(row["originLocation"]) else row["originLocation"]
        currentLocation = "" if pd.isna(row["currentLocation"]) else row["currentLocation"]
        room = "" if pd.isna(row["room"]) else row["room"]
        contact = "" if pd.isna(row["contact"]) else row["contact"]
        currentOwner = "" if pd.isna(row["currentOwner"]) else row["currentOwner"]
        previousOwner = "" if pd.isna(row["previousOwner"]) else row["previousOwner"]
        orderNumber = "" if pd.isna(row["orderNumber"]) else row["orderNumber"]
        color = "" if pd.isna(row["color"]) else row["color"]
        serialNumber = "" if pd.isna(row["serialNumber"]) else row["serialNumber"]
        maintenanceDate = "2999-01-01" if pd.isna(row["maintenanceDate"]) else row["maintenanceDate"]
        comments = "" if pd.isna(row["comments"]) else row["comments"]


        item = {
            "beacon" : beacon,
            "category" : category,
            "service" : service,
            "itemID" : itemID,
            "brand" : brand,
            "model" : model,
            "supplier" : supplier,
            "purchaseDate" : purchaseDate,
            "purchasePrice" : purchasePrice,
            "originLocation" : originLocation,
            "currentLocation" : currentLocation,
            "room" : room,
            "contact" : contact,
            "currentOwner" : currentOwner,
            "previousOwner" : previousOwner,
            "orderNumber" : orderNumber,
            "color" : color,
            "serialNumber" : serialNumber,
            "maintenanceDate" : maintenanceDate,
            "comments" : comments
        }
        

        try:
            # Create
            create_req = session.post(f"{SERVER_URL}/api/items", json=item)
            create_req.raise_for_status()
            item_id_created.append(itemID)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)
    else:
        print(
            f"Error -> Skipping invalid row:\n{row}\nEmpty (or NaN) fields are not allowed, whitespaces are not allowed in the itemID.\n"
        )



def delete_all_items(session, company):
    try:
        get_req = session.get(f"{SERVER_URL}/api/items")
        get_req.raise_for_status()

        json = get_req.json()
    except Exception as e:
        print(f"Cannot get items from the DB: {e}")

    ids_to_delete = []
    for e in json:
        ids_to_delete.append(e["id"])
    print(f"IDs of items that will be deleted: {ids_to_delete}")

    try:
        for id in ids_to_delete:
            create_req = session.delete(f"{SERVER_URL}/api/items/{id}")
            create_req.raise_for_status()
    except Exception as e:
        print(f"Cannot delete at least one item from the DB: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""
        Given an Excel file, it creates items (should NOT violate any constraints of the DB) in the client's company database.
        The Excel file needs to have the following columns as header: beacon, category, service, itemID, brand, model, supplier, 
        purchaseDate, purchasePrice, originLocation, currentLocation, room, contact, currentOwner, previousOwner, orderNumber, 
        color, serialNumber, maintenanceDate, comments. All other columns are ignored.\n
        The header should start at the first row of the Excel.\n
        Empty fields are not allowed for beacon, itemID and category. All other fields left blank will get a default value.\n
        The beacon should be a MAC address and have the format aa:aa:aa:aa:aa:aa.
        
        purchaseDate and maintenanceDate need to have the following format: aaaa-mm-dd.\n
        Whitespaces are not allowed in itemID.
        """
    )
    parser.add_argument("file", metavar="file", type=str, help="the Excel file")
    parser.add_argument(
        "company", metavar="company", type=str, help="the client's company"
    )
    parser.add_argument('--delete', dest='delete', action='store_const',
                    const=True, default=False,
                    help='Delete all items from the DB before adding the new items (default: False)')
    args = parser.parse_args()
    print("Welcome to the BioT users creator!\n")
    try:
        filename = args.file
        company = args.company
        delete = args.delete
        columns = [
                "beacon",
                "category",
                "service",
                "itemID",
                "brand",
                "model",
                "supplier",
                "purchaseDate",
                "purchasePrice",
                "originLocation",
                "currentLocation",
                "room",
                "contact",
                "currentOwner",
                "previousOwner",
                "orderNumber",
                "color",
                "serialNumber",
                "maintenanceDate",
                "comments"
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
            
            itemID_created = []

            if delete:
                confirmation = input(f"WARNING: this operation will delete all items from the DB for the company '{company}'! Are you sure you want to continue? [y/N]: ")
                if confirmation == "y" or confirmation == "Y":
                    print(f"Deleting all items from DB of company = {company}")
                    delete_all_items(s, company)
                    print(f"Done! Deleted all items from DB of company = {company}")
                else:
                    print("Okay, exiting...")
                    exit()

            print("Creating items...")
            df.apply(
                lambda row: create_item(s, row, itemID_created, company),
                axis=1,
            )

            if itemID_created:
                print(
                    f"Created {len(itemID_created)} items for company {company}:\n{itemID_created}\n"
                )

            print("Bye!")
    except FileNotFoundError:
        print("Error -> File not found!")
    except BaseException as e:
        print("Error ->", e.args[0])
