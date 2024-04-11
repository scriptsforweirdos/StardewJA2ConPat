from dataclasses import dataclass, field
from typing import Optional


@dataclass
class BigObject():
    Name: str = ""
    DisplayName: str = ""
    Description: str = ""
    Price: Optional[int] = 0
    Fragility: Optional[int] = 0
    CanBePlacedIndoors: Optional[bool] = True
    CanBePlacedOutdoors: Optional[bool] = False
    IsLamp: Optional[bool] = False
    Texture: Optional[str] = ""
    SpriteIndex: Optional[int] = 0
    ContextTags: Optional[list] = field(default_factory=lambda: [])

    def to_dict(self):
        outDict = {}
        mandatoryKeys = ["Name", "DisplayName", "Description", "SpriteIndex"]
        for k, v in self.__dict__.items():
            if k in mandatoryKeys or v:
                outDict[k] = v
            elif k == "CanBePlacedIndoors" and not v:
                outDict[k] == v
        return outDict


@dataclass
class Buff():
    Duration: int = 0
    Id: str = ""
    FarmingLevel: Optional[int] = 0
    FishingLevel: Optional[int] = 0
    ForagingLevel: Optional[int] = 0
    LuckLevel: Optional[int] = 0
    MiningLevel: Optional[int] = 0
    Attack: Optional[int] = 0
    Defense: Optional[int] = 0
    MagnetRadius: Optional[int] = 0
    MaxStamina: Optional[int] = 0

    def to_dict(self):
        outDict = {"Id": "",
                   "Duration": 0,
                   "IsDebuff": False,
                   "CustomAttributes": {}}
        for k, v in self.__dict__.items():
            if k in ["Id", "Duration"]:
                outDict[k] == v
            else:
                if v:
                    outDict["CustomAttributes"][k] = v
                if v < 0:
                    outDict["IsDebuff"] = True
        return outDict


@dataclass
class Crop():
    Seasons: list = field(default_factory=lambda: [])
    DaysInPhase: list = field(default_factory=lambda: [])
    HarvestItemID: str = ""
    Texture: str = ""
    SpriteIndex: int = 0
    RegrowDays: Optional[int] = -1
    IsRaised: Optional[bool] = False
    IsPaddyCrop: Optional[bool] = False
    NeedsWatering: Optional[bool] = True
    HarvestMethod: Optional[str] = "Grab"
    HarvestMinStack: Optional[int] = 1
    HarvestMaxStack: Optional[int] = 1
    HarvestMinQuality: Optional[int] = 0
    HarvestMaxQuality: Optional[int] = 0
    HarvestMaxIncreasePerFarmingLevel: Optional[int] = 0
    ExtraHarvestChance: Optional[int] = 0
    TintColors: Optional[list] = field(default_factory=lambda: [])
    CountForMonoculture: Optional[bool] = False
    CountForPolyculture: Optional[bool] = False
    PlantableLocationRules: Optional[dict] = field(default_factory=lambda: [])

    def to_dict(self):
        outDict = {}
        mandatoryKeys = ["Seasons", "DaysInPhase", "HarvestItemID", "Texture", "SpriteIndex"]
        for k, v in self.__dict__.items():
            if k in mandatoryKeys or v:
                outDict[k] = v
        return outDict


@dataclass
class FruitTree():
    DisplayName: str = ""
    Seasons: list = field(default_factory=lambda: [])
    Fruit: list = field(default_factory=lambda: [])
    Texture: str = ""
    TextureSpriteRow: int = 0
    PlantableLocationRule: Optional[list] = field(default_factory=lambda: [])

    def to_dict(self):
        outDict = {}
        mandatoryKeys = ["DisplayName", "Seasons", "Fruit", "Texture",
                         "TextureSpriteRow"]
        for k, v in self.__dict__.items():
            if k in mandatoryKeys or v:
                outDict[k] = v
        return outDict


@dataclass
class MeleeWeapon():
    Name: str = ""
    DisplayName: str = ""
    Description: str = ""
    Type: int = 0
    Texture: str = ""
    SpriteIndex: int = 0
    MinDamage: int = 0
    MaxDamage: int = 0
    CanBeLostOnDeath: bool = True
    Knockback: Optional[float] = 0.0
    Speed: Optional[int] = 0
    Precision: Optional[int] = 0
    Defense: Optional[int] = 0
    AreaOfEffect: Optional[int] = 0
    CritChance: Optional[float] = 0.0
    CritMultiplier: Optional[float] = 0.0
    MineBaseLevel: Optional[int] = -1
    MineMinLevel: Optional[int] = -1
    Projectiles: Optional[list] = field(default_factory=lambda: [])

    def to_dict(self):
        outDict = {}
        mandatoryKeys = ["Name", "DisplayName", "Description", "Type", "Texture",
                         "SpriteIndex", "MinDamage", "MaxDamage", "CanBeLostOnDeath"]
        for k, v in self.__dict__.items():
            if k in mandatoryKeys or v:
                outDict[k] = v
        return outDict


@dataclass
class SVObject():
    Name: str = ""
    DisplayName: str = ""
    Description: str = ""
    Type: str = ""
    Category: int = 0
    Price: int = 0
    Texture: str = ""
    SpriteIndex: int = 0
    Edibility: Optional[int] = -1
    IsDrink: Optional[bool] = False
    GeodeDrops: Optional[list] = field(default_factory=lambda: [])
    Buffs: Optional[list] = field(default_factory=lambda: [])
    ArtifactSpotChances: Optional[dict] = field(default_factory=lambda: {})
    ContextTags: Optional[list] = field(default_factory=lambda: [])
    ExcludeFromRandomSale: Optional[bool] = False
    ExcludeFromFishingCollection: Optional[bool] = False
    ExcludeFromShippingCollection: Optional[bool] = False

    def to_dict(self):
        outDict = {}
        mandatoryKeys = ["Name", "DisplayName", "Description", "Type",
                         "Category", "Price", "Texture", "SpriteIndex"]
        for k, v in self.__dict__.items():
            if k in mandatoryKeys or v:
                outDict[k] = v
        return outDict
