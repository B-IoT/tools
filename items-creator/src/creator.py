# Copyright (c) 2021 BioT. All rights reserved.

import pandas as pd
import requests
import argparse
from decouple import config
import re

SERVER_URL = "https://api.b-iot.ch:443"
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
    if not re.match("[a-z0-9][a-z0-9]:[a-z0-9][a-z0-9]:[a-z0-9][a-z0-9]:[a-z0-9][a-z0-9]:[a-z0-9][a-z0-9]:[a-z0-9][a-z0-9]", beacon):
        print(f'beacon does not match the required format. Found: {beacon}')
        return False
    if not pd.isna(purchaseDate) and not re.match("[0-9]{4}-[0-9]{2}-[0-9]{2}", purchaseDate):
        print(f'purchaseDate does not match the required format. Found: {purchaseDate}')
        return False
    if not pd.isna(maintenanceDate) and not re.match("[0-9]{4}-[0-9]{2}-[0-9]{2}", maintenanceDate):
        print(f'purchaseDate does not match the required format. Found: {maintenanceDate}')
        return False
    
    if not pd.isna(purchasePrice):
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
        itemID = row["itemID"]

        service = row["service"]
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

        item = {
            "beacon" : beacon,
            "category" : category,
            "itemID" : itemID
        }

        if not pd.isna(service):
            item["service"] = service
        if not pd.isna(brand):
            item["brand"] = brand
        if not pd.isna(model):
            item["model"] = model
        if not pd.isna(supplier):
            item["supplier"] = supplier
        if not pd.isna(purchaseDate):
            item["purchaseDate"] = purchaseDate
        if not pd.isna(purchasePrice):
            item["purchasePrice"] = purchasePrice
        if not pd.isna(originLocation):
            item["originLocation"] = originLocation
        if not pd.isna(currentLocation):
            item["currentLocation"] = currentLocation
        if not pd.isna(room):
            item["room"] = room
        if not pd.isna(contact):
            item["contact"] = contact
        if not pd.isna(currentOwner):
            item["currentOwner"] = currentOwner
        if not pd.isna(previousOwner):
            item["previousOwner"] = previousOwner
        if not pd.isna(orderNumber):
            item["orderNumber"] = orderNumber
        if not pd.isna(color):
            item["color"] = color
        if not pd.isna(serialNumber):
            item["serialNumber"] = serialNumber
        if not pd.isna(maintenanceDate):
            item["maintenanceDate"] = maintenanceDate
        if not pd.isna(comments):
            item["comments"] = comments

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
        Empty fields are not allowed for beacon, itemID and category.\n
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
