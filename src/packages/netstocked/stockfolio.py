#-*- coding: utf-8 -*-
# stockfolio.py  (c)2021, 2022  Henrique Moreira

"""
Portfolio of stocks, from xlsx.
"""

# pylint: disable=missing-function-docstring

import sys
import os.path
from os import environ
import datetime
import openpyxl
from netstocked.common import money_string

DEBUG = 0
DEFAULT_ENV_VAR_DIR = "PINT"
DEFAULT_BASENAME = "Transactions_accoes.xlsx"

VALID_IDS = ("m", "H", "p",)
WHO_ID = "p"

LOW_IDX = 5000
TAX_COIN = "EUR"


def main():
    """ Main script """
    code = run(sys.stdout, sys.stderr, sys.argv[1:])
    if code is None:
        print(f"""Usage:

{__file__} [excel-input-file]
""")
    sys.exit(code if code else 0)


def run(out, err, args):
    """ Run script """
    who = WHO_ID
    assert err, "stderr"
    if args:
        if len(args) > 1:
            return None
        fname = args[0]
    else:
        dirname = environ[DEFAULT_ENV_VAR_DIR]
        fname = os.path.join(dirname, DEFAULT_BASENAME)
        who = ""	# show all
    msg = reader(out, fname, who, int(DEBUG))
    if msg and err:
        err.write(f"{msg}\n")
    return 0


class Transactions():
    """ Transactions class """
    def __init__(self, fname:str="", sheet_name:str=""):
        self._wbk = openpyxl.load_workbook(fname) if fname else None
        self._sheet, self._content = None, {}
        sheet = sheet_name if sheet_name else "stock_transactions"
        self._msg, self._content = "", {}
        if self._wbk:
            self._sheet = self._init_sheet(fname, sheet)
            self.heads = self._from_heading()
        else:
            self.heads = []

    def content(self) -> dict:
        """ Returns the raw content (dictionary) """
        assert self._content
        return self._content

    def by_account(self, account_name:str) -> list:
        """ Returns the list of transactions per account """
        assert account_name
        return self._content["data"]["by-id"][account_name]

    def _init_sheet(self, fname, sheet_name:str):
        assert sheet_name
        sheet = self._wbk[sheet_name]
        msg, content = read_sheet(sheet, fname)
        self._msg, self._content = msg, content
        return sheet

    def _from_heading(self) -> list:
        """ Returns pairs of (index, header-name), 1..n """
        def better_name(astr:str) -> str:
            return astr.replace(" ", "")

        hdr = self._content["header"]
        res = [
            (idx, better_name(name)) for idx, name in enumerate(hdr, start=1)
        ]
        return res


def reader(out, fname:str, who:str, debug:int=0) -> str:
    """ Read stocks xls """
    wbk = openpyxl.load_workbook(fname)
    sheet = wbk["stock_transactions"]
    msg, content = read_sheet(sheet, fname, debug)
    if debug > 0:
        print("." * 40 + "\n" + str(content))
        print("." * 40, end="\n\n")
    #print("Keys:", sorted(content))
    data = content["data"]
    if who:
        for elem in data["by-id"][who]:
            print(who + ":", elem)
        return msg
    for elem in data["from-to"]:
        print("#", elem)
    return msg


def read_sheet(sheet, fname:str="", debug:int=0) -> tuple:
    msg = ""
    rows = [row for row in sheet]
    header = [ala.value for ala in rows[0]]
    hdr = columns()
    if debug > 0:
        print(f"Debug: read '{fname}', header:\n",
              header, "<<<\n",
              ">>> expected header:\n",
              hdr["header"],
              end="\n\n")
    data_dict = parse_input(header, hdr, rows[1:])
    content = {
        "header": header,
        "data": data_dict,
    }
    return msg, content


def columns() -> dict:
    # for col in header: idx += 1; print(" " * 8 + '"' + f'{col}' + f'": {idx}' + ',')
    cols = {
        "ID": 1,
        "Data": 2,
        "Hora": 3,
        "Produto": 4,
        "ISIN": 5,
        "Bolsa": 6,
        "Quantidade": 7,
        "VM0": 8,
        "Per": 9,
        "TRM": 10,
        "Valor_local": 11,
        "VM": 12,
        "Valor": 13,
        "Cambio": 14,
        "VM2": 15,
        "Taxa": 16,
        "VM3": 17,
        "Total": 18,
    }
    dct, names, letters = {}, {}, {}
    for col_name, col_idx in cols.items():
        assert col_idx >= 1, f"Bogus col_idx: {col_idx}"
        assert col_idx not in dct
        dct[col_idx] = col_name
        assert col_name not in names
        names[col_name] = col_idx
        letter = chr(ord('A') + col_idx - 1)
        letters[letter] = col_name
    hdr = {
        "header": [cols],
        "head-indexes": dct,
        "head-letters": letters,
    }
    return hdr


def parse_input(header:list, hdr:dict, payload:list):
    assert isinstance(header, list)
    hdr_dicts = hdr["header"]
    assert len(hdr_dicts) == 1
    starting_row_idx = len(hdr_dicts) + 1
    hdr_dict = hdr_dicts[0]
    assert hdr_dict["ID"] == 1, "ID must be column# 1 (A)"
    hletter = hdr["head-letters"]
    rowlist = []
    for row in payload:
        brute = {
            "@data_types": "",
        }
        for cell in row:
            letra = cell.column_letter
            brute["@data_types"] += cell.data_type
            field = hletter.get(letra)
            if not field:
                assert field is None
                continue
            brute[field] = (cell.data_type, cell.value)
        rowlist.append(brute)
    content = {
        "header": header,
        "tail": rowlist,
        "starting-row-idx": starting_row_idx,
        "from-to": [],
        "by-id": {},
    }
    #	types = [brute["@data_types"] for brute in content["tail"]]
    #	print('\n'.join(types))
    msg = check_all_columns(hdr_dict, starting_row_idx, rowlist)
    assert msg == "", f"check_all_columns(): {msg}"
    dct = process_brute_content(content, starting_row_idx)
    # Sanity check only:
    for acronym in dct:
        # Check listing By acronym 'H', 'm', 'p', ...etc.
        for idx, elem in enumerate(dct[acronym], starting_row_idx):
            #print(":::", acronym, idx, elem)
            assert len(elem) == 10, f"Unexpected length ({len(elem)}: {elem}"
    return content


def process_brute_content(content:dict, idx:int=2) -> dict:
    """ Makes formulas """
    debug = DEBUG
    alist, taxlist = [], []
    from_to = []
    rowlist = content["tail"]
    baselist = ["NADA"] * idx
    for acronym in VALID_IDS:
        assert acronym not in content["by-id"], acronym
        content["by-id"][acronym] = []
    line = idx
    tax_idx = {}
    for brute in rowlist:
        types = brute["@data_types"]
        quant, per, local = brute["Quantidade"][1], brute["Per"][1], brute["Valor_local"][1]
        astr = date_from_cell_tup(brute["Data"])
        adate = astr
        value = round(quant * per, 2)
        shown_total = money_string(value)
        if debug > 0:
            print(f"Debug: #{idx}", types, quant, per, local)
        assert brute["Quantidade"][0] == "n", f"Wrong quantity type: {quant}"
        elem = [
            idx,
            brute["ID"][1],
            adate,
            shown_total,
            brute["Produto"][1],
            "buy" if quant > 0 else "sell",
            quant,
            value,
            brute["ISIN"][1] if brute["ISIN"][1] else "",
            f"line={line}",
        ]
        alist = [elem] + alist
        taxa = brute["Taxa"][1]
        if taxa is None:
            taxa = "-"
            taxval = 0.0
        else:
            taxa = money_string(taxa)
            taxval = float(taxa)
        taxlist = [(taxa, taxval, TAX_COIN)] + taxlist
        baselist.append(elem)
        idx += 1
        line += 1
    row_id = 1000
    for idx, elem in enumerate(alist):
        row_id += 1
        elem[0] = row_id
        acronym = elem[1]
        tup = tuple(elem)
        from_to.append(tup)
        elem[0] = len(content["by-id"][acronym]) + LOW_IDX + 1
        elem[1] = taxlist[idx]
        content["by-id"][acronym].append(elem)
    # Transactions().content()["data"]["from-to"] lists transactions linearly for all accounts
    content["from-to"] = from_to
    return content["by-id"]


def check_all_columns(hdr_dict:dict, idx:int, rowlist:list) -> str:
    for row in rowlist:
        has = "@data_types" in row
        assert has
        n_fields = len(row) - int(has)
        if n_fields != len(hdr_dict):
            #print("# row:", row)
            return f"Row {idx}: has {n_fields} columns, expected {len(hdr_dict)}"
        idx += 1
    return ""


def date_from_cell_tup(tup:tuple) -> str:
    atype, aval = tup
    # f'{brute["Data"][0]}:{brute["Data"][1]}'
    # f'{atype}:{aval}'
    if atype == "s":	# excel string
        obj = datetime.datetime.strptime(aval, "%d-%m-%Y")
    elif atype == "d":
        obj = aval
    new = obj.strftime("%Y-%m-%d")
    assert isinstance(new, str)
    iso_date = new
    return iso_date


# Main script
if __name__ == "__main__":
    main()
