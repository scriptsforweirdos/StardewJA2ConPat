"""Converts MultiYield Crops to work with 1.6 objects added via Content Patcher.

Edit Lines 14-16 to suit your purposes.
"""
import copy
import json
import os
import pprint

import pyjson5

MODNAME = "Raffadax.RaffadaxCompleteProduction"
MYCFILE = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.5.6 Files/[MYC] Raffadax Multi Yield/HarvestRules.json"
OUTPATH = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/[MYC] Raffadax Multi Yield/HarvestRules.json"

if __name__ == "__main__":
    mycData = pyjson5.load(open(MYCFILE), encoding="utf-8")
    vanillaFile = "vanillaObjects.json"
    vanillaData = json.load(open(vanillaFile))
    outList = []
    for rule in mycData["Harvests"]:
        outRule = copy.deepcopy(rule)
        if outRule["CropName"] not in vanillaData:
            outRule["CropName"] = "{}_{}".format(MODNAME, rule["CropName"].replace(" ", ""))
        for hr in outRule["HarvestRules"]:
            if hr["ItemName"] not in vanillaData:
                hr["ItemName"] = "{}_{}".format(MODNAME, hr["ItemName"].replace(" ", ""))
        outList.append(outRule)
    outDict = {"Harvests": outList}
    outJson = json.dumps(outDict, indent=4)
    with open(OUTPATH, 'w') as f:
        f.write(outJson)
