#-*- coding: utf-8 -*-
# isin.py  (c)2021  Henrique Moreira

"""
ISIN and stock cache
"""

from netstocked.common import known_str

# pylint: disable=missing-function-docstring, line-too-long

LOG_CACHE = 1

FAST_ISIN = {
    "NL0000009538": "PHILIPS",	# KON.PHILIPS N.V.
    "DE0005200000": "BEIERSDORF",
}


class IsinCache():
    """ ISIN cache """
    def __init__(self):
        self._msg = ""
        self._stocks = {
            "by-name": {},
            "by-isin": {},
            "log": [],
            "bogus": [],
        }

    def last_error(self) -> str:
        """ Return last error """
        return self._msg

    def stocks(self) -> dict:
        return self._stocks

    def stock_names(self) -> list:
        """ Returns all cached names """
        res = [(name, self._stocks["by-name"][name]) for name in sorted(self._stocks["by-name"])]
        return res

    def update_cache(self, name:str, isin:str) -> tuple:
        if LOG_CACHE:
            self._stocks["log"].append((isin, name))
        res_name, res_isin = self._update_cache(name, isin)
        msg = self._msg
        if msg:
            self._stocks["bogus"].append(msg)
        return res_name, res_isin

    def _update_cache(self, name:str, isin:str) -> tuple:
        self._msg = ""
        if not name:
            return name, ""
        if not isin:
            return name, known_str(self._stocks["by-name"].get(name))
        if isin in self._stocks["by-isin"]:
            there = self._stocks["by-isin"][isin]
            is_ok = there == name
            if not is_ok:
                self._msg = f"ISIN {isin}: is not '{name}', but {there}"
            return name, isin
        isin_there = self._stocks["by-name"].get(name)
        if isin_there:
            is_ok = isin_there == isin
            if not is_ok:
                self._msg = f"ISIN for {name} expected as '{isin_there}'"
            return name, isin_there
        self._stocks["by-name"][name] = isin
        self._stocks["by-isin"][isin] = name
        return name, isin

    def easier_name(self, isin:str) -> str:
        """ Returns empty if ISIN 'isin' does not exist,
        else, returns the easier name stored in the constant!
        """
        if not isin:
            return ""
        name = FAST_ISIN.get(isin)
        if not name:
            return ""
        assert name
        return name


isin_cache = IsinCache()


# Main script
if __name__ == "__main__":
    print("Please import me.")
