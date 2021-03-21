# relays-creator

Given an Excel file, the script creates the relays in the client's company database.
The Excel file need to have the following columns: relay_id, longitude, latitude, floor, username, password, wifi_ssid, wifi_password. All other columns are ignored.

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

```
usage: creator.py [-h] file company

Given an Excel file, it creates the relays in the client's company database. The Excel file need to have the
following columns: relay_id, longitude, latitude, floor, username, password, wifi_ssid, wifi_password. All other columns are ignored.

positional arguments:
  file        the Excel file
  company     the client's company

optional arguments:
  -h, --help  show this help message and exit
```

An example of Excel file is available [here](examples/excel.xlsx).
