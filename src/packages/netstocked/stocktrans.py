#-*- coding: utf-8 -*-
# stocktrans.py  (c)2021  Henrique Moreira

"""
Stock transaction(s)
"""

# pylint: disable=missing-function-docstring, line-too-long

from netstocked.common import money_string
from netstocked.isin import isin_cache


class AsTransaction():
    """ Transaction (see class Transactions)
    """
    def __init__(self, tup, isin=""):
        assert isinstance(tup, (list, tuple))
        t_id, star, date, s_val, s_name, buy, quant, t_val = tup
        if isinstance(t_val, int):
            t_val = float(t_val)
        else:
            assert isinstance(t_val, float), f"Value is: {t_val} ({type(t_val)}"
            t_val = round(t_val, 2)
        assert s_val
        assert isinstance(s_val, str)
        assert s_name
        assert buy in ("buy", "sell",), f"Wrong 'buy': '{buy}'"
        assert isinstance(quant, int)
        if quant < 0:
            t_val = -1.0 * t_val
        self.t_id, self.date = t_id, date
        self.buy, self.quant, self.t_val = buy, quant, t_val
        assert star == "*"
        self._name, self._isin = isin_cache.update_cache(s_name, isin)

    def stock_name(self) -> str:
        name = isin_cache.easier_name(self._isin)
        if name:
            return name
        return self._name

    def string(self) -> str:
        aval = money_string(self.t_val)
        shown = stock_string(self._name)
        astr = f"{self.t_id:<6} {self.date} {self.buy:<4} {shown} {self.quant:7}x {aval}"
        return astr

    def json_elem(self) -> dict:
        """ Returns a dictionary json element """
        res = {
            "Id": self.t_id,
            "StockName": self.stock_name(),
            "Op": self.buy,
            "Date": self.date,
            "Quant": float(self.quant),
            "Total": self.t_val,
        }
        return res


def stock_string(astr:str) -> str:
    shown = f"{astr:_<16.14}"
    if len(astr) > 14:
        shown = shown[:-1] + "."
    return shown


# Main script
if __name__ == "__main__":
    print("Please import me.")
