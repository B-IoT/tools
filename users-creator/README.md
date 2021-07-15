# users-creator

Given an Excel file, it creates the users in the client's company database.
The Excel file need to have the following columns as header: username, password. All other columns are ignored.

The header should start at the first row of the Excel.
Empty fields are not allowed.
Whitespace are not allowed in username and password.

## Installation

First, install the required modules:

```bash
pip install -r requirements.txt
```

## Usage

Before usage, you need to make sure that the company's database has been created.

```
usage: creator.py [-h] file company

Given an Excel file, it creates (or updates if already present) the relays in the client's company database. The Excel file need to have the following columns as header: relay_id,
longitude, latitude, floor, username, password, wifi_ssid, wifi_password. All other columns are ignored. The header should start at the first row
of the Excel. Empty fields are not allowed. Whitespaces are not allowed in relay_id. Latitude and longitude need to be different from 0.

positional arguments:
  file        the Excel file
  company     the client's company

optional arguments:
  -h, --help  show this help message and exit
```

An example of Excel file is available [here](examples/excel.xlsx).
