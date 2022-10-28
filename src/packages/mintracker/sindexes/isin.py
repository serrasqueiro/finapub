"""
Module for ISIN, basic class and checks

Follows:
- ISO 6166: International Securities Identification Number (ISIN)

(c)2020, 2022  Henrique Moreira (part of 'mintracker')
"""

# pylint: disable=invalid-name, consider-using-f-string

import string


class ISIN():
    """
    ISIN class -- International Securities Identification Number
    """
    def __init__(self, s_isin=None):
        self.isin_str = s_isin


    def checksum_digit(self, s):
        """
        Calculate ISIN checksum digit (and 12 alpha-digit string)
        :param s: input ISIN
        :return: pair (tuple): checksum digit, and 12 alpha-digit string
        """
        assert isinstance(s, str)
        if len(s) != 12:
            return -1, None
        cs_digit = ISIN_checksum_digit(s)
        s_isin = "{}{}".format(s[:-1], cs_digit)
        return cs_digit, s_isin


    def is_valid(self):
        """
        Checks whether ISIN is valid
        :return: bool, True iff ISIN is valid
        """
        assert self.isin_str
        _, s_isin = self.checksum_digit(self.isin_str)
        if s_isin is None:
            return False
        return s_isin == self.isin_str


    def __str__(self):
        is_ok = self.is_valid()
        if is_ok:
            return self.isin_str
        return "-"


class StockDB():
    """ Stock Database """
    def __init__(self):
        self._isin_ref = {}
        self.markets = {}

    def add_market(self, mkt_name, stocks) -> bool:
        """ Add market sock list (fourplets) """
        assert self._check_stocks(stocks)
        self.markets[mkt_name] = stocks
        return True

    def get_from_ISIN(self, isin) -> tuple:
        """ Get pair abbreviation and full name from ISIN """
        assert isinstance(isin, str)
        return self._isin_ref[isin]

    def _check_stocks(self, stocks) -> bool:
        """ Basic checks on stock list (fourplets) """
        for fourplet in stocks:
            assert len(fourplet) == 4
            myisin = ISIN(fourplet[1])
            if not myisin.is_valid():
                return False
            assert myisin.isin_str not in self._isin_ref
            self._isin_ref[myisin.isin_str] = fourplet[2:]
        return True


def ISIN_checksum(s):
    """
    Calculate checksum of ISIN string
    :param s: string
    :return: string, 12 chars
    """
    if s is None:
        return None
    assert isinstance(s, str)
    if len(s) == 12:
        x = s[:11] + "0"
    elif len(s) == 11:
        x = s + "0"
    else:
        return None
    csum_str = str(ISIN_checksum_digit(x))
    return x[:11] + csum_str


def ISIN_checksum_digit(isin):
    """
    Internal checksum calculation for stock ISIN numbers
    :param isin: string, 12 octets
    :return: int, the checksum digit
    """
    # pylint: disable=line-too-long

    def digit_sum(n):
        return (n // 10) + (n % 10)

    assert len(isin) == 12
    # See: https://stackoverflow.com/questions/46061228/calculating-isin-checksum
    all_uppercase = string.ascii_uppercase
    alphabet = {letter: value for (value, letter) in
                enumerate(''.join(str(n) for n in range(10)) + all_uppercase)}
    val = - sum(digit_sum(2 * int(c))
                if i % 2 == 1
                else int(c) for (i, c) in enumerate(reversed(''.join(str(d) for d in (alphabet[v] for v in isin[:-1]))), 1)) % 10
    checksum_digit = abs(val)
    return checksum_digit
