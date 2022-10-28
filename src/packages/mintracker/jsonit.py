#-*- coding: utf-8 -*-
# jsonit.py  (c)2021  Henrique Moreira

"""
To JSON, and from JSON
"""

# pylint: disable=missing-function-docstring

import json

def to_json(alist:list) -> str:
    """ Returns the JSON string for a list """
    astr = json.dumps(alist, indent=2, sort_keys=True) + "\n"
    return astr


# Main script
if __name__ == "__main__":
    print("Please import me.")
