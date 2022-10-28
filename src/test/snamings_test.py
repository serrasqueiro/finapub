""" Test for snamings module (part of 'mintracker')

(c)2020, 2022  Henrique Moreira
"""

# pylint: disable=missing-docstring, invalid-name, consider-using-f-string


from sys import argv
import mintracker
from mintracker.sindexes.stockspt import STK_W_PSI20
from mintracker.sindexes.isin import ISIN_checksum
from mintracker.snamings import StockWeight, RefISIN, StockRefs

def main():
    code = run_main(argv[1:])
    assert code == 0

def run_main(args):
    """ Main basic module test.
    """
    nicks = args if args != [] else None
    do_invent = args != []
    return do_test(nicks, do_invent)

def do_test(nicks, do_invent):
    stk_pair = (
        STK_W_PSI20,
    )
    for name, lines in stk_pair:
        sw = StockWeight(name, lines)
        sr = RefISIN()
        invalids = sr.add_ISIN_refs(mintracker.sindexes.stockspt.STK_ISIN_PSI20)
        if invalids != []:
            print("Invalid ISIN (#{} invalid): {}".format(len(invalids), invalids))
            assert False
        if nicks is None or name in nicks:
            s_refs = StockRefs(sw)
            if do_invent:
                s_refs.add_stock("ABC", "Abc Long")
                sr.ref_isin["Abc Long"] = "ABC123XYZ00?"
            idx, f_sum = 0, 0.0
            for abbrev, any_weight in sw.abbreviations():
                idx += 1
                weight = any_weight if any_weight is not None else -1.0
                print("#{}:\t{} {:8.2f} {:.15} {}"
                      "".format(idx, name, weight, abbrev, sw.full_name(abbrev)))
                if weight > 0:
                    f_sum += weight
            print("Total weight (100%) = {:.3f}".format(f_sum))
            for abbrev, _ in sw.abbreviations():
                stock_name = sw.full_name(abbrev)
                isin = sr.ref_isin.get(stock_name)
                is_ok = isin is not None and ISIN_checksum(isin) == isin
                str_ok = "OK" if is_ok else "NotOk; ok would be '{}'".format(ISIN_checksum(isin))
                print("{}, ISIN={}, {} ({})".format(name, isin, stock_name, str_ok))
    return 0

if __name__ == "__main__":
    main()
