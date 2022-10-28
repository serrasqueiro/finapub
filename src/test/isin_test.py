""" Test for isin.py (part of 'mintracker')

(c) 2022  Henrique Moreira
"""

from mintracker.sindexes.isin import \
     ISIN_checksum_digit, \
     ISIN, StockDB

from mintracker.sindexes import stockspt
from mintracker.sindexes import euronext

def main_test() -> bool:
    """ Runs basic tests """
    tups = stockspt.STK_ISIN_PSI20
    weights = tup_from_stock_weight(stockspt.STK_W_PSI20)
    first_bogus = None
    for official, isin_code in tups:
        abbrev = "?"
        for name, there, _ in weights:
            if name == official:
                abbrev = there
                break
        isin = ISIN(isin_code)
        hint = "" if isin.is_valid() else " (wrong ISIN)"
        print(f"{isin_code}{hint} = {official}, abbrev={abbrev}")
        if abbrev == "?":
            first_bogus = official
    if first_bogus:
        print("Could not find abbreviation for:", first_bogus)
        return False
    stock_db = StockDB()
    for mkt in ("EN.LIS",):
        print(f"Market, abbreviation mkt={mkt}")
        stocks = list(euronext.stock_names_by_market(mkt))
        is_ok = stock_db.add_market(mkt, stocks)
        assert is_ok
        for official, isin_code in tups:
            try:
                what = stock_db.get_from_ISIN(isin_code)
            except KeyError:
                what = None
            if what:
                print(f"ISIN={isin_code}: {what}")
            else:
                msg = f"No ISIN found at mkt='{mkt}'"
                print(f"ISIN={isin_code}, '{official}', {msg}")
    return True


def tup_from_stock_weight(tup) -> tuple:
    """ Returns the tuple of stock names as triples:
    1. Official designation
    2. Designated Abbreviation
    3. Weight
    """

    def triplet(astr) -> tuple:
        """ Returns triplet separated by ';' """
        name, abbrev, weight = astr.split(";")
        assert name
        assert abbrev
        val = float(weight) if weight != "-" else 0.0
        assert val >= 0.0
        return (name, abbrev, val)

    stock_index_name, longstr = tup
    assert stock_index_name
    assert stock_index_name.replace("-", "").isalnum()
    lines = longstr.strip('\n').splitlines()
    header, payload = lines[0], lines[1:]
    assert len(header.split(";")) == 3
    alist = [triplet(entry) for entry in payload]
    return tuple(alist)


#    sample = "US0378331005"
#    tic = sample[:-1] + "$"
#    z = ISIN(tic)
#    print("isin_checksum_digit('{}') = {}".format(tic, z.isin_str))


#
# Test suite
#
if __name__ == "__main__":
    assert main_test()
