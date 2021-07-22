# users-creator

Given an Excel file, it creates the users in the client's company database.
The Excel file needs to have the following columns as header: user_id, username, password. All other columns are ignored.

The company of the users is set automatically to the company name passed as arguments to the script.

The header should start at the first row of the Excel.
Empty fields are not allowed.
Whitespace are not allowed in user_id, username and password.
It adds automatically the BioT admin user with username “biot_<company_name>” and  password “biot”.

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

Before usage, you need to make sure that the company's database has been created.

```
usage: creator.py [-h] file company

Given an Excel file, it creates the users (should NOT already exist) in the client's company database.
The Excel file needs to have the following columns as header: user_id, username, password. All other columns are ignored.
The header should start at the first row of the Excel.
Empty fields are not allowed.
Whitespaces are not allowed in user_id, username, password.
It adds automatically the BioT admin user with username “biot_<company_name>” and  password “biot”.

positional arguments:
  file        the Excel file
  company     the client's company

optional arguments:
  -h, --help  show this help message and exit
```

An example of Excel file is available [here](examples/excel.xlsx).
