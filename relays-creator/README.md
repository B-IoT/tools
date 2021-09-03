# relays-creator

Given an Excel file, it creates (or updates if already present) the relays in the client's company database.
The Excel file need to have the following columns as header: relay_id, longitude, latitude, floor, wifi_ssid, wifi_password. 
All other columns are ignored.
The header should start at the first row of the Excel.
Empty fields are not allowed.
Whitespaces are not allowed in relay_id.
Latitude and longitude need to be different from 0.

## Installation

First, install the required modules:

```bash
pip install -r requirements.txt
```

Then, create a file `.env` in `src/` with the following content:

```
PASSWORD=<biot_user_password_in_company_db>
```

## Usage

Before usage, you need to make sure that the company's database and biot user have been created.

```
usage: creator.py [-h] [--delete] file company

Given an Excel file, it creates (or updates if already present) the relays in the client's company database. The Excel file need to have the following columns as header: relay_id, longitude, latitude, floor, wifi_ssid, wifi_password.
All other columns are ignored. The header should start at the first row of the Excel. Empty fields are not allowed. Whitespaces are not allowed in relay_id. Latitude and longitude need to be different from 0.

positional arguments:
  file        the Excel file
  company     the client's company

optional arguments:
  -h, --help  show this help message and exit
  --delete    Delete all relays (except relay_0 and relay_biot) from the DB before adding the new relays (default: False)
```

An example of Excel file is available [here](examples/excel.xlsx).
