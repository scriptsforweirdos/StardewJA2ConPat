# StardewJA2ConPat
Python Converter for Stardew Valley Json Assets to Content Patcher

## Features

* Creates content.json including new item entries and Gift Prefs
* Converts translation fields into i18n files for each available language
* Merges images into spritesheets that correspond to the generated JSON
* Uses current UniqueID in the manifest as the new ModId in the exported JSON.

This is very preliminary, untested and raw but people have been asking for it since they heard I was involved with the Raffadax Conversion project, so here you go. Any content.json made from this mod should be heavily proofread and tested in-game before release.

## Out of scope

Currently this cannot convert clothing (shirts/pants/boots/hats) because it was made to convert Raffadax and that mod does not have Json Assets apparel.

## Requires:

* Python 3
* pyjson5 For reading human-crafted JSON
* Pillow for making image spritesheets

## Usage

Windows:  
`python convertja.py --m="MODE" --s="path/to/json/assets/mod/folder/" --d="path/to/output/directory/"`

Mac:  
`python3 convertja.py --m="MODE" --s="path/to/json/assets/mod/folder/" --d="path/to/output/directory/"`

Replace "MODE" with any of crops, objects, trees or weapons.

Objects mode handles both BigObjects and Objects.
