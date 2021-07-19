# users-creator

Given an Excel file, it creates the users in the client's company database.
The Excel file needs to have the following columns as header: user_id, username, password and company. All other columns are ignored.

The header should start at the first row of the Excel.
Empty fields are not allowed.
Whitespace are not allowed in user_id, username and password.

## Installation

First, install the required modules:

```bash
pip install -r requirements.txt
```

## Usage

Before usage, you need to make sure that the company's database has been created.

```
usage: creator.py [-h] file company

Given an Excel file, it creates (or updates if already present) the relays in the client's company database. The Excel file needs to have the following columns as header: user_id, username, password and company. All other columns are ignored. The header should start at the first row of the Excel. Empty fields are not allowed. Whitespace are not allowed in user_id, username and password.

positional arguments:
  file        the Excel file
  company     the client's company

optional arguments:
  -h, --help  show this help message and exit
```

An example of Excel file is available [here](examples/excel.xlsx).
