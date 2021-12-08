#-*- coding: utf-8 -*-
# common.py  (c)2021  Henrique Moreira

"""
Commonalities on money, etc.
"""

# pylint: disable=missing-function-docstring


def money_string(value) -> str:
    return f"{value:10.2f}"


def known_str(an_obj) -> str:
    if not an_obj:
        return ""
    assert isinstance(an_obj, str)
    return an_obj


# Main script
if __name__ == "__main__":
    print("Please import me.")
