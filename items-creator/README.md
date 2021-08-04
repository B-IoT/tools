# items-creator

Given an Excel file, it creates items (should NOT violate any constraints of the DB) in the client's company database. The Excel file needs to have the following columns as header: beacon, category, service, itemID,
brand, model, supplier, purchaseDate, purchasePrice, originLocation, currentLocation, room, contact, currentOwner, previousOwner, orderedNumber, color, serialNumber, maintenanceDate, comments. All other columns are
ignored. 
The header should start at the first row of the Excel. 
Empty fields are not allowed. 

purchaseDate and maintenanceDate need to have the following format: aaaa-mm-dd. 
Whitespaces are not allowed in itemID.

WARNING: When option `--delete` is passed, all items are permanently deleted without any confirmation!!!!

## Installation

First, install the required modules:

```bash
pip install -r requirements.txt
```

Then, create a file `.env` in `src/` with the following content:

```
PASSWORD=<biot_company_user_password>
```

## Usage

Before usage, you need to make sure that the company's database has been created.

```
usage: creator.py [-h] [--delete] file company

Given an Excel file, it creates items (should NOT violate any constraints of the DB) in the client's company database. The Excel file needs to have the following columns as header: beacon, category, service, itemID,
brand, model, supplier, purchaseDate, purchasePrice, originLocation, currentLocation, room, contact, currentOwner, previousOwner, orderedNumber, color, serialNumber, maintenanceDate, comments. All other columns are
ignored. The header should start at the first row of the Excel. Empty fields are not allowed. purchaseDate and maintenanceDate need to have the following format: aaaa-mm-dd. Whitespaces are not allowed in itemID.

positional arguments:
  file        the Excel file
  company     the client's company

optional arguments:
  -h, --help  show this help message and exit
  --delete    Delete all items from the DB before adding the new items (default: False)
```

An example of Excel file is available [here](examples/excel.xlsx).
