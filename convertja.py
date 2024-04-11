import argparse
import copy
import json  # for writing
import os
import pprint
import re
from dataclasses import dataclass, field
from math import ceil, floor
from typing import Optional

import pyjson5  # for reading
from PIL import Image
from classes import BigObject, Buff, Crop, FruitTree, MeleeWeapon, SVObject

CATEGORIES = {"ArtisanGoods": -26,
              "Building Resources": -16,
              "Cooking": -25,
              "Crafting": -8,
              "Flower": -80,
              "Fruit": -79,
              "Gem": -2,
              "Greens": -81,
              "Metal Resource": -15,
              "Metal": -15,
              "Milk": -6,
              "Mineral": -12,
              "Seeds": -74,
              "Trash": -20,
              "Vegetable": -75}

CATINDICES = {"-2": "Gem",
              "-6": "Milk",
              "-7": "Cooking",
              "-12": "Mineral",
              "-15": "Metal Resource",
              "-16": "Building Resources",
              "-18": "Sell at Pierre or Marnie",
              "-20": "Trash",
              "-23": "Sell at Willy",
              "-25": "Cooking",
              "-26": "Artisan Goods",
              "-28": "Monster Loot",
              "-74": "Seeds",
              "-75": "Vegetable",
              "-79": "Fruit",
              "-80": "Flower",
              "-81": "Forage"}

VANILLANPCS = ["Abigail", "Alex", "Caroline", "Clint", "Demetrius", "Dwarf",
               "Elliott", "Emily", "Evelyn", "George", "Gus", "Haley", "Harvey",
               "Jas", "Jodi", "Kent", "Krobus", "Leah", "Leo", "Lewis", "Linus",
               "Marnie", "Maru", "Pam", "Penny", "Pierre", "Robin", "Sam",
               "Sandy", "Sebastian", "Shane", "Vincent", "Willy", "Wizard"]

MODNPCS = {
    "Amanra": "Raffadax.NPCs",
    "Astrid": "Raffadax.NPCs",
    "Coyote": "Raffadax.NPCs",
    "Mephisto": "Raffadax.NPCs",
    "Puck": "Raffadax.NPCs",
    "Shuck": "Raffadax.NPCs",
    "Xolotl": "Raffadax.NPCs",
    "Beatrice": "attonbomb.Beatrice",
    "Marlon": "FlashShifter.SVECode",
    "Olivia": "FlashShifter.SVECode",
    "Susan": "FlashShifter.SVECode",
    "Andy": "FlashShifter.SVECode",
    "Apples": "FlashShifter.SVECode",
    "Claire": "FlashShifter.SVECode",
    "Martin": "FlashShifter.SVECode",
    "Morris": "FlashShifter.SVECode",
    "Sophia": "FlashShifter.SVECode",
    "Victor": "FlashShifter.SVECode",
    "Morgan": "FlashShifter.SVECode",
    "Gunther": "FlashShifter.SVECode",
    "Gregory": "CPBoardingHouse",
    "Sheila": "CPBoardingHouse",
    "Hekate": "Tarniyar.NPC.GV.mod",
    "Hephaestus": "Tarniyar.NPC.GV.mod",
    "Jacob": "Lemurkat.JacobEloise.CP",
    "Eloise": "Lemurkat.JacobEloise.CP",
    "Madam": "FishingIslandNPC",
    "Jade": "malic.cp.jadeNPC",
    "Alecto": "ZoeDoll.NPCAlecto",
    "Wednesday": "RaddBlaster.Wednesday",
    "Sorren": "annachibi.SorrenNPC",
    "Ayeisha": "TheLimeyDragon.Ayeisha",
    "Denver": "MISSINGID",
    "Kim": "KimJyeulNPC.ExnoticTest",
    "Mike": "SYS.mike",
    "Mona": "Zilsara.Mona",
    "Muadhnait": "Asari.Muadhnait",
    "Nikolai": "Fellowclown.PC",
    "Paul": "Ginnyclaire.Paul",
    "Shiko": "Papaya.ShikoTakahashi",
    "Zoro": "EmpressKimi.Zoro"
}

NAMERE = r"[^a-zA-Z0-9_\.]"  # strips invalid chars from item IDs


def buildBigObjects(srcDir, modId, spritesheet, mode, i18n=None):
    """Converts big craftables to content patcher."""
    newObjects = {"LogName": "Raffadax New Big Objects - {}".format(mode),
                  "Action": "EditData",
                  "Target": "Data/BigCraftables",
                  "Entries": {}
                  }
    objTexture = {"LogName": "Raffadax Big Object Textures - {}".format(mode),
                  "Action": "Load",
                  "Target": "Mods/{}/BigObjects/{}".format(modId, mode),
                  "FromFile": "assets/textures/{}.png".format(spritesheet)}
    if not i18n:
        i18n = {"en": {}}
    i = 0
    spriteFiles = {}
    jsonFiles = []
    objDir = "{}BigCraftables".format(srcDir)
    for entry in objectscan(objDir):
        jsonFiles.append(entry.path.replace("\\", "/"))
    for jf in jsonFiles:
        try:
            objData = pyjson5.load(open(jf, encoding="utf-8"))
        except Exception:
            print(jf)
            quit()
        bo = BigObject()
        nameStr = re.sub(NAMERE, "", objData["Name"])
        bo.Name = "{}_{}".format(modId, nameStr)
        bo.DisplayName = "{{{{i18n:{}.DisplayName}}}}".format(nameStr)
        i18n["en"]["{}.DisplayName".format(nameStr)] = objData["Name"]
        bo.Description = "{{{{i18n:{}.Description}}}}".format(nameStr)
        i18n["en"]["{}.Description".format(nameStr)] = objData["Description"]
        if "Price" in objData:
            bo.Price = objData["Price"]
        if "ProvidesLight" in objData and objData["ProvidesLight"]:
            bo.IsLamp = True
        bo.Texture = "Mods/{}/BigObjects/{}".format(modId, mode)
        bo.SpriteIndex = i
        spritename = jf[0:-5] + ".png"
        spriteFiles[spritename] = bo.SpriteIndex
        newObjects["Entries"][bo.Name] = bo.to_dict()
        if "NameLocalization" in objData:
            for langKey, langStr in objData["NameLocalization"]:
                if langKey not in i18n:
                    i18n[langKey] = {}
                i18n[langKey]["{}.Displayname".format(nameStr)] = langStr
        if "DescriptionLocalization" in objData:
            for langKey, langStr in objData["DescriptionLocalization"]:
                if langKey not in i18n:
                    i18n[langKey] = {}
                i18n[langKey]["{}.Description".format(nameStr)] = langStr
        i += 1

    return [newObjects, spriteFiles, i18n, objTexture]


def buildCooking(srcDir, modId, vanillaObjects):
    """Converts Recipe fields from JA objects to cooking recipes."""
    objDir = "{}Objects".format(srcDir)
    newRecipes = {"LogName": "Raffadax New Cooking Recipes",
                  "Action": "EditData",
                  "Target": "Data/CookingRecipes",
                  "Entries": {}}
    jsonFiles = []
    for entry in objectscan(objDir):
        jsonFiles.append(entry.path.replace("\\", "/"))
    for jf in jsonFiles:
        try:
            objData = pyjson5.load(open(jf, encoding="utf-8"))
        except Exception:
            print(jf)
            quit()
        if "Recipe" in objData and objData["Recipe"] and (objData["Category"] == "Cooking" or objData["Category"] == -7):
            output = "{}_{} {}".format(modId, objData["Name"].replace(" ", ""), objData["Recipe"]["ResultCount"])
            ingredients = []
            for iNode in objData["Recipe"]["Ingredients"]:
                if isinstance(iNode["Object"], int) or iNode['Object'].isnumeric():
                    iStr = "{} {}".format(iNode['Object'], iNode["Count"])
                elif iNode["Object"] in vanillaObjects:
                    iStr = "{} {}".format(vanillaObjects[iNode["Object"]], iNode["Count"])
                else:
                    nameStr = re.sub(NAMERE, "", iNode["Object"])
                    iStr = "{}_{} {}".format(modId, nameStr, iNode["Count"])
                ingredients.append(iStr)
            newRecipes["Entries"][objData["Name"]] = "{}//{}/none/{}".format(" ".join(ingredients), output, objData["Name"])
    return newRecipes


def buildCrafting(srcDir, modId, vanillaObjects):
    """Converts Recipe fields from JA objects & big craftables to crafting recipes."""
    objDir = "{}Objects".format(srcDir)
    bigObjDir = "{}BigCraftables".format(srcDir)
    newRecipes = {"LogName": "Raffadax New Crafting Recipes",
                  "Action": "EditData",
                  "Target": "Data/CraftingRecipes",
                  "Entries": {}}
    jsonFiles = []
    for entry in objectscan(objDir):
        jsonFiles.append(entry.path.replace("\\", "/"))
    for entry in objectscan(bigObjDir):
        jsonFiles.append(entry.path.replace("\\", "/"))
    for jf in jsonFiles:
        try:
            objData = pyjson5.load(open(jf, encoding="utf-8"))
        except Exception:
            print(jf)
            quit()
        if "Recipe" in objData and objData["Recipe"] and (("Category" in objData and objData["Category"] == "Crafting") or jf.endswith("big-craftable.json")):
            output = "{}_{} {}".format(modId, objData["Name"].replace(" ", ""), objData["Recipe"]["ResultCount"])
            ingredients = []
            isBC = "false"
            if jf.endswith("big-craftable.json"):
                isBC = "true"
            for iNode in objData["Recipe"]["Ingredients"]:
                if isinstance(iNode["Object"], int) or iNode['Object'].isnumeric():
                    iStr = "{} {}".format(iNode['Object'], iNode["Count"])
                elif iNode["Object"] in vanillaObjects:
                    iStr = "{} {}".format(vanillaObjects[iNode["Object"]], iNode["Count"])
                else:
                    nameStr = re.sub(NAMERE, "", iNode["Object"])
                    iStr = "{}_{} {}".format(modId, nameStr, iNode["Count"])
                ingredients.append(iStr)
            newRecipes["Entries"][objData["Name"]] = "{}//{}/{}/none/{}".format(" ".join(ingredients), output, isBC, objData["Name"])
    return newRecipes


def buildCrops(srcDir, modId, objectData, objectSprites, i18n, spritesheet, vanillaObjects):
    """Creates Seed objects & builds Data/Crops entries."""
    cropDir = "{}Crops".format(srcDir)
    cropTexture = {"LogName": "Raffadax Crop Textures",
                   "Action": "Load",
                   "Target": "Mods/{}/Crops".format(modId),
                   "FromFile": "assets/textures/crops.png"}
    newCrops = {"LogName": "Raffadax New Crops",
                "Action": "EditData",
                "Target": "Data/Crops",
                "Entries": {}}
    jsonFiles = []
    cropSprites = {}
    i = len(objectSprites)
    j = 0
    for entry in objectscan(cropDir):
        jsonFiles.append(entry.path.replace("\\", "/"))
    for jf in jsonFiles:
        data = pyjson5.load(open(jf, encoding="utf-8"))
        # seed object
        seedObj = SVObject()
        nameStr = re.sub(NAMERE, "", data["SeedName"])
        seedObj.Name = "{}_{}".format(modId, nameStr)
        i18n["en"]["{}.Displayname".format(nameStr)] = data["SeedName"]
        seedObj.DisplayName = "{{{{i18n: {}.Displayname}}}}".format(nameStr)
        # build the description.
        i18n["en"]["{}.Description".format(nameStr)] = data["SeedDescription"]
        seedObj.Description = "{{{{i18n: {}.Description}}}}".format(nameStr)
        seedObj.Type = "Seeds"
        seedObj.Category = -74
        if "SeedPurchasePrice" in data:
            seedObj.Price = data["SeedPurchasePrice"]
        seedObj.Texture = "Mods/{}/Objects/Crops".format(modId)
        seedObj.SpriteIndex = i
        spritename = jf.rsplit("/", 1)[0] + "/seeds.png"
        if "SeedNameLocalization" in data:
            for langKey, langStr in data["NameLocalization"]:
                if langKey not in i18n:
                    i18n[langKey] = {}
                i18n[langKey]["{}.Displayname".format(nameStr)] = langStr
        if "SeedDescriptionLocalization" in data:
            for langKey, langStr in data["DescriptionLocalization"]:
                if langKey not in i18n:
                    i18n[langKey] = {}
                i18n[langKey]["{}.Description".format(nameStr)] = langStr
        objectSprites[spritename] = seedObj.SpriteIndex
        objectData["Entries"][seedObj.Name] = seedObj.to_dict()

        # crop object
        cropObj = Crop()
        cropObj.Seasons = data["Seasons"]
        cropObj.DaysInPhase = data["Phases"]
        cropName = re.sub(NAMERE, "", data["Product"])
        if cropName in vanillaObjects:
            cropObj.HarvestItemID = vanillaObjects[cropName]
        else:
            cropObj.HarvestItemID = "{}_{}".format(modId, cropName)
        cropObj.Texture = "Mods/{}/Crops".format(modId)
        if "RegrowthPhase" in data:
            cropObj.RegrowDays = data["RegrowthPhase"]
        if "TrellisCrop" in data:
            cropObj.IsRaised = data["TrellisCrop"]
        if "HarvestWithScythe" in data and data["HarvestWithScythe"]:
            cropObj.HarvestMethod = "Scythe"
        if "Bonus" in data:
            if "MinimumPerHarvest" in data["Bonus"]:
                cropObj.HarvestMinStack = data["Bonus"]["MinimumPerHarvest"]
            if "MaximumPerHarvest" in data["Bonus"]:
                cropObj.HarvestMaxStack = data["Bonus"]["MinimumPerHarvest"]
            if "MaxIncreasePerFarmLevel" in data["Bonus"]:
                cropObj.HarvestMaxIncreasePerFarmingLevel = data["Bonus"]["MaxIncreasePerFarmLevel"]
            if "ExtraChance" in data["Bonus"]:
                cropObj.ExtraHarvestChance = data["Bonus"]["ExtraChance"]
        if "Colors" in data and data["Colors"]:
            cropObj.TintColors = data["Colors"]
        cropObj.SpriteIndex = j
        cropspritename = jf.rsplit("/", 1)[0] + "/crop.png"
        cropSprites[cropspritename] = cropObj.SpriteIndex
        if "CropType" in data and data["CropType"]:
            if data["CropType"] == "Paddy":
                cropObj.IsPaddyCrop = True
            if data["CropType"] == "IndoorsOnly":
                newRule = {"Id": "{}_Rule".format(seedObj.Name),
                           "Result": "Deny",
                           "Condition": "LOCATION_IS_OUTDOORS Here"}
                cropObj.PlantableLocationRules.append(newRule)
        newCrops["Entries"][seedObj.Name] = cropObj.to_dict()
        i += 1
        j += 1
    return [objectData, newCrops, cropSprites, objectSprites, i18n, cropTexture]


def buildObjects(srcDir, modId, spritesheet, mode, i18n):
    """Converts JA objects to Content Patcher models including Gift Tastes."""
    newObjects = {"LogName": "Raffadax New Objects - {}".format(mode),
                  "Action": "EditData",
                  "Target": "Data/Objects",
                  "Entries": {}
                  }
    newGifts = {"LogName": "Raffadax Gift Taste Edit - {}".format(mode),
                "Action": "EditData",
                "Target": "Data/NPCGiftTastes",
                "TextOperations": []}
    conditionalGifts = {}
    objTexture = {"LogName": "Raffadax Object Textures - {}".format(mode),
                  "Action": "Load",
                  "Target": "Mods/{}/Objects/{}".format(modId, mode),
                  "FromFile": "assets/textures/{}.png".format(spritesheet)}
    i = 0
    jsonFiles = []
    spriteFiles = {}
    giftprefs = {}
    objDir = "{}Objects".format(srcDir)
    tasteKeys = {"Love": 1, "Like": 3, "Neutral": 9, "Dislike": 5, "Hate": 7}
    for entry in objectscan(objDir):
        jsonFiles.append(entry.path.replace("\\", "/"))
    for jf in jsonFiles:
        try:
            objData = pyjson5.load(open(jf, encoding="utf-8"))
        except Exception:
            print(jf)
            quit()
        newObj = SVObject()
        nameRe = r"[^a-zA-Z0-9_\.]"
        nameStr = re.sub(nameRe, "", objData["Name"])
        newObj.Name = "{}_{}".format(modId, nameStr)
        newObj.DisplayName = "{{{{i18n:{}.DisplayName}}}}".format(nameStr)
        i18n["en"]["{}.DisplayName".format(nameStr)] = objData["Name"]
        if "Category" in objData:
            if isinstance(objData["Category"], str):
                if objData["Category"].strip("-").isnumeric():
                    newObj.Category = int(objData["Category"])
                    if str(objData["Category"]) in CATINDICES:
                        newObj.Type = CATINDICES[str(objData["Category"])]
                    else:
                        print("No Cat found for {}".format(objData["Category"]))
                else:
                    newObj.Type = objData["Category"]
                    if newObj.Type in CATEGORIES:
                        newObj.Category = CATEGORIES[newObj.Type]
                    else:
                        print("No Cat found for {}".format(newObj.Type))
            else:
                newObj.Category = objData["Category"]
                newObj.Type = CATINDICES[str(objData["Category"])]
                # print("Non string cat for {}".format(newObj.Name))
        else:
            print("No Category data for {}".format(objData["Name"]))
            quit()
        if "Description" in objData:
            newObj.Description = "{{{{i18n:{}.Description}}}}".format(nameStr)
            i18n["en"]["{}.Description".format(nameStr)] = objData["Description"]
        if "Price" in objData:
            newObj.Price = objData["Price"]
        newObj.Texture = "Mods/{}/Objects/{}".format(modId, mode)
        newObj.SpriteIndex = i
        if "Edibility" in objData:
            newObj.Edibility = objData["Edibility"]
        if "EdibleIsDrink" in objData:
            newObj.IsDrink = objData["EdibleIsDrink"]
        if "EdibleBuffs" in objData and objData["EdibleBuffs"]:
            newBuff = Buff()
            newBuff.Id = "{}_buff".format(newObj.Name)
            for bk, bv in objData["EdibleBuffs"].items():
                if bk in ["Farming", "Mining", "Foraging", "Luck", "Fishing"]:
                    setattr(newBuff, "{}Level".format(bk), bv)
                else:
                    setattr(newBuff, bk, bv)
            newObj.Buffs.append(newBuff.to_dict())
        if "ContextTags" in objData:
            newObj.ContextTags = objData["ContextTags"]
        if "CategoryTextOverride" in objData:  # this may have to become a CustomField
            catName = re.sub(NAMERE, "", objData["CategoryTextOverride"])
            newObj.ContextTags.append("category_{}".format(catName.lower()))
        if "NameLocalization" in objData:
            for langKey, langStr in objData["NameLocalization"]:
                if langKey not in i18n:
                    i18n[langKey] = {}
                i18n[langKey]["{}.Displayname".format(nameStr)] = langStr
        if "DescriptionLocalization" in objData:
            for langKey, langStr in objData["DescriptionLocalization"]:
                if langKey not in i18n:
                    i18n[langKey] = {}
                i18n[langKey]["{}.Description".format(nameStr)] = langStr
        if "GiftTastes" in objData:
            for tk, tdata in objData["GiftTastes"].items():
                fieldIndex = tasteKeys[tk]
                for npc in tdata:
                    if npc not in VANILLANPCS and npc not in MODNPCS:
                        print("Nonexistent NPC: {} in {}".format(npc, newObj.Name))
                        quit()
                    if npc not in giftprefs:
                        giftprefs[npc] = {}
                    if fieldIndex not in giftprefs[npc]:
                        giftprefs[npc][fieldIndex] = []
                    giftprefs[npc][fieldIndex].append(newObj.Name)
        newObjects["Entries"][newObj.Name] = newObj.to_dict()
        spritename = jf[0:-5] + ".png"
        spriteFiles[spritename] = newObj.SpriteIndex
        i += 1
    for npc, tierData in giftprefs.items():
        if npc in VANILLANPCS:
            for tier, itemList in tierData.items():
                prefDict = {"Operation": "Append",
                            "Target": ["Fields", npc, int(tier)],
                            "Value": " ".join(itemList),
                            "Delimiter": " "
                            }
                newGifts["TextOperations"].append(prefDict)
        else:
            conditionalGifts[npc] = {"LogName": "Raffadax Gift Taste Edit - {}".format(mode),
                                     "Action": "EditData",
                                     "Target": "Data/NPCGiftTastes",
                                     "TextOperations": []}
            for tier, itemList in tierData.items():
                prefDict = {"Operation": "Append",
                            "Target": ["Fields", npc, int(tier)],
                            "Value": " ".join(itemList),
                            "Delimiter": " "
                            }
                conditionalGifts[npc]["TextOperations"].append(prefDict)
            modName = MODNPCS[npc]
            conditionalGifts[npc]["When"] = {"HasMod": modName}
    # pprint.pprint(conditionalGifts)
    # convert dict to list
    cGiftList = []
    for npc, prefData in conditionalGifts.items():
        cGiftList.append(prefData)
    return [newObjects, spriteFiles, newGifts, i18n, objTexture, cGiftList]


def buildSprites(spriteList, dstDir, fileName, spriteType="objects"):
    """Stitches together sprites."""
    if spriteType == "objects":
        imgHeight = ceil(len(spriteList) / 24) * 16
        imgWidth = 384
        base = Image.new("RGBA", (imgWidth, imgHeight))
        for imgpath, sidx in spriteList.items():
            img = Image.open(imgpath)
            x = (sidx % 24) * 16
            y = floor(sidx / 24) * 16
            base.paste(img, (x, y))
    elif spriteType == "crops":
        imgWidth = 256
        imgHeight = ceil(len(spriteList) / 2) * 32
        base = Image.new("RGBA", (imgWidth, imgHeight))
        # maxsize = (128, 32)
        for imgpath, sidx in spriteList.items():
            img = Image.open(imgpath)
            x = (sidx % 2) * 128
            y = floor(sidx / 2) * 32
            # no resizing needed
            base.paste(img, (x, y))
    elif spriteType == "fruittrees":
        imgWidth = 432
        imgHeight = 80 * len(spriteList)
        base = Image.new("RGBA", (imgWidth, imgHeight))
        for imgpath, sidx in spriteList.items():
            img = Image.open(imgpath)
            x = 0
            y = 80 * sidx
            base.paste(img, (x, y))
    elif spriteType == "weapons":
        imgWidth = 128
        imgHeight = ceil(len(spriteList) / 8) * 16
        base = Image.new("RGBA", (imgWidth, imgHeight))
        for imgpath, sidx in spriteList.items():
            img = Image.open(imgpath)
            x = (sidx % 8) * 16
            y = floor(sidx / 8) * 16
            base.paste(img, (x, y))
    elif spriteType == "bigobjects":
        imgHeight = ceil(len(spriteList) / 8) * 32
        imgWidth = 128
        base = Image.new("RGBA", (imgWidth, imgHeight))
        for imgpath, sidx in spriteList.items():
            img = Image.open(imgpath)
            x = (sidx % 8) * 16
            y = floor(sidx / 8) * 32
            base.paste(img, (x, y))
    # base.show()
    outPath = "{}{}.png".format(dstDir, fileName)
    base.save(outPath)


def buildTrees(srcDir, modId, objectData, objectSprites, i18n, spritesheet):
    """Creates Data/fruitTrees entries from JA Trees."""
    treeDir = "{}FruitTrees".format(srcDir)
    newTrees = {"LogName": "Raffadax New Trees",
                "Action": "EditData",
                "Target": "Data/fruitTrees",
                "Entries": {}}
    treeTexture = {"LogName": "Raffadax Tree Textures",
                   "Action": "Load",
                   "Target": "Mods/{}/Trees".format(modId),
                   "FromFile": "assets/textures/fruittrees.png"}
    jsonFiles = []
    treeSprites = {}
    i = len(objectSprites)
    j = 0
    for entry in objectscan(treeDir):
        jsonFiles.append(entry.path.replace("\\", "/"))
    for jf in jsonFiles:
        data = pyjson5.load(open(jf, encoding="utf-8"))
        # sapling object
        saplingObj = SVObject()
        nameStr = re.sub(NAMERE, "", data["SaplingName"])
        saplingObj.Name = "{}_{}".format(modId, nameStr)
        i18n["en"]["{}.Displayname".format(nameStr)] = data["SaplingName"]
        saplingObj.Displayname = "{{{{i18n:{}.Displayname}}}}".format(nameStr)
        # build the description.
        i18n["en"]["{}.Description".format(nameStr)] = data["SaplingDescription"]
        saplingObj.Description = "{{{{i18n:{}.Description}}}}".format(nameStr)
        saplingObj.Type = "Seeds"
        saplingObj.Category = -74
        if "SaplingPurchasePrice" in data:
            saplingObj.Price = data["SaplingPurchasePrice"]
        saplingObj.Texture = "Mods/{}/Objects/FruitTrees".format(modId)
        saplingObj.SpriteIndex = i
        spritename = jf.rsplit("/", 1)[0] + "/sapling.png"
        if "SaplingNameLocalization" in data:
            for langKey, langStr in data["NameLocalization"]:
                if langKey not in i18n:
                    i18n[langKey] = {}
                i18n[langKey]["{}.Displayname".format(nameStr)] = langStr
        if "SaplingDescriptionLocalization" in data:
            for langKey, langStr in data["DescriptionLocalization"]:
                if langKey not in i18n:
                    i18n[langKey] = {}
                i18n[langKey]["{}.Description".format(nameStr)] = langStr
        objectSprites[spritename] = saplingObj.SpriteIndex
        objectData["Entries"][saplingObj.Name] = saplingObj.to_dict()

        # tree object
        newTree = FruitTree()
        newTree.DisplayName = "{{{{i18n: {}.TreeName}}}}".format(nameStr)
        i18n["en"]["{}.TreeName"] = data["Name"]
        newTree.Seasons = [data["Season"]]
        fruitName = re.sub(NAMERE, "", data["Product"])
        fruit = {"ItemId": "{}_{}".format(modId, fruitName)}
        newTree.Fruit.append(fruit)
        newTree.Texture = "Mods/{}/Trees".format(modId)
        newTree.TextureSpriteRow = j
        treespritename = jf.rsplit("/", 1)[0] + "/tree.png"
        treeSprites[treespritename] = newTree.TextureSpriteRow
        newTrees["Entries"][saplingObj.Name] = newTree.to_dict()
        i += 1
        j += 1

    return [objectData, newTrees, treeSprites, objectSprites, i18n, treeTexture]


def buildWeapons(srcDir, modId, spritesheet, i18n):
    """Creates Data/Weapons entries from JA Weapons."""
    weaponDir = "{}Weapons".format(srcDir)
    newWeapons = {"LogName": "Raffadax New Weapons",
                  "Action": "EditData",
                  "Target": "Data/Weapons",
                  "Entries": {}}
    weaponTexture = {"LogName": "Raffadax Tree Textures",
                     "Action": "Load",
                     "Target": "Mods/{}/Weapons".format(modId),
                     "FromFile": "assets/textures/weaponobjects.png"}
    jsonFiles = []
    weaponSprites = {}
    weaponTypes = {"Sword": 0, "Dagger": 1, "Club": 2}
    i = 0
    for entry in objectscan(weaponDir):
        jsonFiles.append(entry.path.replace("\\", "/"))
    for jf in jsonFiles:
        data = pyjson5.load(open(jf, encoding="utf-8"))
        # sapling object
        nameNoDiacritics = jf.rsplit("/", 2)[1]  # not sure if the game will be happy with UTF-8 items, let's take it to ascii
        newMW = MeleeWeapon()
        nameStr = re.sub(NAMERE, "", nameNoDiacritics)
        newMW.Name = "{}_{}".format(modId, nameStr)
        i18n["en"]["{}.Displayname".format(nameStr)] = data["Name"]
        newMW.DisplayName = "{{{{i18n:{}.Displayname}}}}".format(nameStr)
        i18n["en"]["{}.Description".format(nameStr)] = data["Description"]
        newMW.Description = "{{{{i18n:{}.Description}}}}".format(nameStr)
        newMW.Type = weaponTypes[data["Type"]]
        newMW.Texture = "Mods/{}/Weapons".format(modId)
        newMW.SpriteIndex = i
        if "MinimumDamage" in data:
            newMW.MinDamage = data["MinimumDamage"]
        if "MaximumDamage" in data:
            newMW.MaxDamage = data["MaximumDamage"]
        if "Knockback" in data:
            newMW.Knockback = float(data["Knockback"])
        if "Speed" in data:
            newMW.Speed = int(data["Speed"])
        if "Accuracy" in data:
            newMW.Precision = int(data["Accuracy"])
        if "Defense" in data:
            newMW.Defense = int(data["Defense"])
        if "ExtraSwingArea" in data:
            newMW.AreaOfEffect = int(data["ExtraSwingArea"])
        if "CritChance" in data:
            newMW.CritChance = float(data["CritChance"])
        if "CritMultiplier" in data:
            newMW.CritMultiplier = float(data["CritMultiplier"])
        if "MineDropVar" in data:
            newMW.MineBaseLevel = int(data["MineDropVar"])
        if "MineDropMinimumLevel" in data:
            newMW.MineMinLevel = int(data["MineDropMinimumLevel"])
        spritename = jf.rsplit("/", 1)[0] + "/weapon.png"
        weaponSprites[spritename] = newMW.SpriteIndex
        newWeapons["Entries"][newMW.Name] = newMW.to_dict()
        i += 1

    return [newWeapons, weaponSprites, i18n, weaponTexture]


def objectscan(path):
    """Recursive Scans of a JA modpack, returns json filepaths."""
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from objectscan(entry.path)
        elif entry.name.endswith((".json")):
            yield entry


def writeData(textures: list, data: list, dstDir: str, dstName: str, cGifts=[]):
    """Generates the json files and writes to drive."""
    jsonOut = {"Changes": []}
    jsonOut["Changes"] += textures
    jsonOut["Changes"] += data
    if cGifts:
        jsonOut["Changes"] += cGifts
    outPath = "{}data/{}.json".format(dstDir, dstName)
    outData = json.dumps(jsonOut, indent=4)
    if not os.path.exists("{}data".format(dstDir)):
        os.mkdir("{}data".format(dstDir))
    with open(outPath, 'w') as f:
        f.write(outData)
    print("Content Patcher data written to {}".format(outPath))


def writeLanguageData(i18n, dstDir):
    """Generates i18n files and writes to drive."""
    if not os.path.exists("{}i18n".format(dstDir)):
        os.mkdir("{}i18n".format(dstDir))
    for langKey, langData in i18n.items():
        outPath = "{}i18n/default.json".format(dstDir)
        outData = pyjson5.dumps(langData)
        with open(outPath, 'w') as f:
            f.write(outData)
    print("i18n data written to {}".format("{}i18n".format(dstDir)))


if __name__ == "__main__":
    # TODO: ExcludeWithMod
    # TODO: Add gift prefs hasmod conditions for non-Vanilla NPCs
    # TODO: Look into JA forge recipes, currently not implemented
    # QUESTION: Do we want parsers for the JA clothing items? Raffadax has none but other mods may have them.
    # get the path to the current file
    parser = argparse.ArgumentParser()
    parser.add_argument("--m", dest="convertMethod", type=str, help="Selects Method, options: artisan, crops, trees, weapons, aio")
    parser.add_argument("--s", dest="sourceDirectory", type=str, help="Source Directory, e.g. [JA] Your Json Assets Mod")
    parser.add_argument("--d", dest="destDirectory", type=str, help="Destination Directory")
    args = parser.parse_args()
    outData = {"Format": "1.30.0",
               "Changes": []}
    dir_path = os.path.dirname(os.path.realpath(__file__))
    rootDir = dir_path.rsplit("\\", 1)[0].replace("\\", "/")
    oldFiles = "{}/1.5.6 Files/".format(rootDir)
    srcDir = "{}[JA] Raffadax Crops/".format(oldFiles)
    dstDir = "{}/1.6 Files/".format(rootDir)
    spriteDir = "{}assets/textures/".format(dstDir)
    i18n = {"en": {}}
    modId = "{{ModId}}"
    if not os.path.exists(spriteDir):
        os.mkdir(spriteDir)
    if args.sourceDirectory:
        srcDir = args.sourceDirectory
    if args.destDirectory:
        dstDir = args.destDirectory
    if args.convertMethod.lower() == "crops":
        srcDir = "{}[JA] Raffadax Crops/".format(oldFiles)
        # crop objects
        objectData, objectSprites, giftData, i18n, objTexture, conditionalGifts = buildObjects(srcDir, modId, "cropobjects", "Crops", i18n)
        # seed objects and cropdata
        objectData, cropData, cropSprites, objectSprites, i18n, cropTexture = buildCrops(srcDir, modId, objectData, objectSprites, i18n, "cropobjects")
        # write data to file
        writeData([objTexture, cropTexture], [objectData, cropData, giftData], dstDir, "Crops", conditionalGifts)
        # # write i18n data
        writeLanguageData(i18n, dstDir, "Crops")
        # # make sprites
        buildSprites(objectSprites, spriteDir, "cropobjects", "objects")
        buildSprites(cropSprites, spriteDir, "crops", "crops")
        print("Sprites saved to {}".format(spriteDir))
    if args.convertMethod.lower() == "trees":
        srcDir = "{}[JA] Raffadax Trees/".format(oldFiles)
        # fruit objects
        objectData, objectSprites, giftData, i18n, objTexture, conditionalGifts = buildObjects(srcDir, modId, "treeobjects", "FruitTrees", i18n)
        objectData, treeData, treeSprites, objectSprites, i18n, treeTexture = buildTrees(srcDir, modId, objectData, objectSprites, i18n, "treeobjects")
        # pprint.pprint(giftData)
        writeData([objTexture, treeTexture], [objectData, treeData, giftData], dstDir, "Trees", conditionalGifts)
        writeLanguageData(i18n, dstDir, "Trees")
        buildSprites(objectSprites, spriteDir, "treeobjects", "objects")
        buildSprites(treeSprites, spriteDir, "fruittrees", "fruittrees")
        print("Sprites saved to {}".format(spriteDir))
    if args.convertMethod.lower() == "weapons":
        srcDir = "{}[JA] Raffadax Weapons/".format(oldFiles)
        weaponData, weaponSprites, i18n, weaponTexture = buildWeapons(srcDir, modId, "weaponobjects", i18n)
        writeData([weaponTexture], [weaponData], dstDir, "Weapons")
        writeLanguageData(i18n, dstDir, "Weapons")
        buildSprites(weaponSprites, spriteDir, "weaponobjects", "weapons")
        print("Sprites saved to {}".format(spriteDir))
    if args.convertMethod.lower() == "artisan":
        srcDir = "{}Raffadax Artisan Assets/[JA] Raffadax Production/".format(oldFiles)
        objectData, objectSprites, giftData, i18n, objTexture, conditionalGifts = buildObjects(srcDir, modId, "artisanobjects", "Artisan")
        bigObjectData, bigObjectSprites, i18n, bigObjTexture = buildBigObjects(srcDir, modId, "artisanmachines", "Artisan", i18n)
        # recipes
        vanillaObjects = pyjson5.load(open("vanillaObjects.json"), encoding="utf-8")
        cookingData = buildCooking(srcDir, modId, vanillaObjects)
        craftingData = buildCrafting(srcDir, modId, vanillaObjects)
        writeData([objTexture, bigObjTexture], [objectData, bigObjectData, cookingData, craftingData], dstDir, "Artisan", conditionalGifts)
        writeLanguageData(i18n, dstDir, "Artisan")
        print("Building sprites...")
        buildSprites(objectSprites, spriteDir, "artisanobjects", "objects")
        buildSprites(bigObjectSprites, spriteDir, "artisanmachines", "bigobjects")
        print("Sprites saved to {}".format(spriteDir))
    if args.convertMethod.lower() == "aio":
        cropDir = "{}[JA] Raffadax Crops/".format(oldFiles)
        treeDir = "{}[JA] Raffadax Trees/".format(oldFiles)
        wepDir = "{}[JA] Raffadax Weapons/".format(oldFiles)
        artiDir = "{}Raffadax Artisan Assets/[JA] Raffadax Production/".format(oldFiles)
        dstDir = "{}/1.6 Files/[CP] Raffadax Test/assets/".format(rootDir)
        spriteDir = "{}textures/".format(dstDir)
        i18n = {"en": {}}
        vanillaObjects = pyjson5.load(open("vanillaObjects.json"), encoding="utf-8")
        # Crops
        print("Generating Crop Data")
        objectData, objectSprites, giftData, i18n, objTexture, conditionalGifts = buildObjects(cropDir, modId, "cropobjects", "Crops", i18n)
        # seed objects and cropdata
        objectData, cropData, cropSprites, objectSprites, i18n, cropTexture = buildCrops(cropDir, modId, objectData, objectSprites, i18n, "cropobjects", vanillaObjects)
        # write data to file
        writeData([objTexture, cropTexture], [objectData, cropData, giftData], dstDir, "crops", conditionalGifts)
        # # make sprites
        buildSprites(objectSprites, spriteDir, "cropobjects", "objects")
        buildSprites(cropSprites, spriteDir, "crops", "crops")
        # Trees
        print("Generating Fruit Tree Data")
        objectData, objectSprites, giftData, i18n, objTexture, conditionalGifts = buildObjects(treeDir, modId, "treeobjects", "FruitTrees", i18n)
        objectData, treeData, treeSprites, objectSprites, i18n, treeTexture = buildTrees(treeDir, modId, objectData, objectSprites, i18n, "treeobjects")
        writeData([objTexture, treeTexture], [objectData, treeData, giftData], dstDir, "trees", conditionalGifts)
        buildSprites(objectSprites, spriteDir, "treeobjects", "objects")
        buildSprites(treeSprites, spriteDir, "fruittrees", "fruittrees")
        # weapons
        print("Generating Weapon Data")
        weaponData, weaponSprites, i18n, weaponTexture = buildWeapons(wepDir, modId, "weaponobjects", i18n)
        writeData([weaponTexture], [weaponData], dstDir, "weapons")
        buildSprites(weaponSprites, spriteDir, "weaponobjects", "weapons")
        # artisan
        print("Generating Artisan Data")
        objectData, objectSprites, giftData, i18n, objTexture, conditionalGifts = buildObjects(artiDir, modId, "artisanobjects", "Artisan", i18n)
        bigObjectData, bigObjectSprites, i18n, bigObjTexture = buildBigObjects(artiDir, modId, "artisanmachines", "Artisan", i18n)
        # recipes
        cookingData = buildCooking(artiDir, modId, vanillaObjects)
        craftingData = buildCrafting(artiDir, modId, vanillaObjects)
        writeData([objTexture, bigObjTexture], [objectData, bigObjectData, cookingData, craftingData], dstDir, "artisan", conditionalGifts)
        buildSprites(objectSprites, spriteDir, "artisanobjects", "objects")
        buildSprites(bigObjectSprites, spriteDir, "artisanmachines", "bigobjects")
        # # write i18n data
        writeLanguageData(i18n, dstDir)
