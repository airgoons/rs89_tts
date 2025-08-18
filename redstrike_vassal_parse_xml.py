import os, shutil
from zipfile import ZipFile
import json
import xmltodict
import bson

class Unit:
    def __init__(self, parent, xml_data, bson_data=None):
        self.parent = parent
        self.xml_data = xml_data

        self.front_png = None
        self.front_png_url = None
        self.back_png = None
        self.back_png_url = None

        self.parse_unit_xml()
        
        if bson_data is None:
            # bson contained in a Unit's parent Faction
            faction = None
            if type(self.parent.parent.parent) is Faction:
                # Unit has ONE command layer
                faction = self.parent.parent.parent
            elif type(self.parent.parent.parent) is Nation:
                # Unit has TWO command layers
                faction = self.parent.parent.parent.parent
            elif type(self.parent.parent.parent) is Command:
                # Unit has THREE command layers
                faction = self.parent.parent.parent.parent.parent
            else:
                # Unit has more than two command layers
                raise NotImplementedError("ERROR: Unit's parent Faction not in expected hierarchical location [{0}]".format(self.name))
            
            self.set_image_urls(faction._bson_data)

        else:
            self.set_image_urls(bson_data)

    def parse_unit_xml(self):
        # remove weird escape characters
        self.name = self.xml_data.get("@entryName").replace("\\", " ")
        self._parse_unit_data()

    def _parse_unit_data(self):
        text = self.xml_data.get("#text", "").split(";")

        for item in text:
            if ".png" in item:
                if "," in item:
                    self.front_png, self.back_png = item.split(",")
                    break
                else:
                    self.front_png = item
                    self.back_png = None
                    break

    def set_image_urls(self, bson_data):
        for _, file_details in bson_data.items():
            if file_details["Name"] == self.front_png:
                self.front_png_url = file_details["URL"]
            if file_details["Name"] == self.back_png:
                self.back_png_url = file_details["URL"]

            if (self.front_png_url != None):
                if (self.back_png != None):
                    if (self.back_png_url != None):
                        
                        return  # both urls are set
                else:
                    return      # tile has no back image
                

class Command:
    def __init__(self, parent, xml_data):
        self.parent = parent
        self.xml_data = xml_data
        self.subordinate_commands = []
        self.units = []
        self.parse_command_xml()

    def parse_command_xml(self):
        # remove weird escape characters
        self.name = self.xml_data.get("@entryName", "").replace("\\", "")
        
        # handle case where there is another command layer:
        subordinate_commands_raw = self.xml_data.get("VASSAL.build.widget.ListWidget", [])
        subordinate_commands_raw += self.xml_data.get("VASSAL.build.widget.TabWidget", [])
        
        if type(subordinate_commands_raw) is list:
            for subordinate_command_raw in subordinate_commands_raw:
                self.subordinate_commands.append(Command(self, subordinate_command_raw))
        elif type(subordinate_commands_raw) is dict:
            self.subordinate_commands.append(Command(self, subordinate_commands_raw))
        else:
            print("ERROR:  bruh")
        
        units_raw = self.xml_data.get("VASSAL.build.widget.PieceSlot", [])
        if type(units_raw) is list:
            for unit_raw in units_raw:
                self.units.append(Unit(self, unit_raw))
        elif type(units_raw) is dict:
            self.units.append(Unit(self, units_raw))
        else:
            print("ERROR:  Command with no units??  {0}".format(self.name))


class Nation:
    def __init__(self, parent, xml_data):
        self.xml_data = xml_data
        self.parent = parent
        self.commands = []
        self.parse_nation_xml()

    def parse_nation_xml(self):
        # remove weird escape characters
        self.name = self.xml_data.get("@entryName").replace("\\", " ")

        commands_raw = self.xml_data.get("VASSAL.build.widget.ListWidget", [])
        if type(commands_raw) is list:
            for command_raw in commands_raw:
                self.commands.append(Command(self, command_raw))
        elif type(commands_raw) is dict:
            self.commands.append(Command(self, commands_raw))
        else:
            print("WARN:  Nation with no commands (list widget)??  {0}".format(self.name))

        commands_raw_tabwidget = self.xml_data.get("VASSAL.build.widget.TabWidget", [])
        if type(commands_raw_tabwidget) is list:
            for command_raw in commands_raw_tabwidget:
                self.commands.append(Command(self, command_raw))
        elif type(commands_raw_tabwidget) is dict:
            self.commands.append(Command(self, commands_raw_tabwidget))
        else:
            print("WARN:  Nation with no commands (tab widget)??  {0}".format(self.name))


class Faction:
    def __init__(self, xml_data, bson_data):
        self._xml_data = xml_data
        self._bson_data = bson_data
        self.nations = []
        self.parse_faction_xml()

    def parse_faction_xml(self):
        # remove weird escape characters
        self.name = self._xml_data.get("@entryName").replace("\\", " ")

        # A VASSAL.build.module.TabWidget or VASSAL.build.module.PanelWidget may represent a Nation
        tab_nations = self._xml_data.get("VASSAL.build.widget.TabWidget", [])
        panel_nations = self._xml_data.get("VASSAL.build.widget.PanelWidget", [])

        if type(tab_nations) is list:
            for tab_nation in tab_nations:
                self.nations.append(Nation(self, tab_nation))
        elif type(tab_nations) is dict:
            self.nations.append(Nation(self, tab_nations))
        else:
            print("WARN:  Faction with no tab nations?? {0}".format(self.name))

        if type(panel_nations) is list:
            for panel_nation in panel_nations:
                self.nations.append(Nation(self, panel_nation))
        elif type(panel_nations) is dict:
            self.nations.append(Nation(self, panel_nations))
        else:
            print("WARN:  Faction with no panel nations?? {0}".format(self.name))


class Card:
    def __init__(self, parent, xml_data, bson_data, back_png):
        self.parent = parent
        self._xml_data = xml_data
        
        self.front_png = None
        self.front_png_url = None

        self.back_png = back_png
        self.back_png_url = None
        self.parse_card_xml(bson_data)

    def parse_card_xml(self, bson_data):
        # as of RS89 v1.2, card data is like unit data
        _unit = Unit(None, self._xml_data, bson_data)

        # hack:  set back png then set image urls again
        _unit.back_png = self.back_png
        _unit.back_png_url = None
        _unit.set_image_urls(bson_data)

        self.name = _unit.name
        self.front_png = _unit.front_png
        self.front_png_url = _unit.front_png_url
        self.back_png_url = _unit.back_png_url


class Deck:
    nato_back_png = "NATO_Card_Back.png"
    wp_back_png = "WP_Card_Back.png"

    def __init__(self, xml_data, bson_data):
        self._xml_data = xml_data
        self.cards = []
        self.parse_deck_xml(bson_data)

    def parse_deck_xml(self, bson_data):
        # remove weird escape characters
        self.name = self._xml_data.get("@entryName").replace("\\", " ")
        cards_raw = self._xml_data["VASSAL.build.widget.ListWidget"]["VASSAL.build.widget.PieceSlot"]

        for card_raw in cards_raw:
            if "NATO" in self.name:
                self.cards.append(Card(self, card_raw, bson_data, Deck.nato_back_png))
            elif "WP" in self.name:
                self.cards.append(Card(self, card_raw, bson_data, Deck.wp_back_png))
            else:
                print("[WARN] bad deck??")


class MarkerCategory:
    def __init__(self, xml_data, bson_data):
        self._xml_data = xml_data
        self.markers = []
        self.parse_category_xml(bson_data)

    def parse_category_xml(self, bson_data):
        # as of RS89 v1.2 markers are like units
        self.name = self._xml_data.get("@entryName").replace("\\", " ")
        markers_raw = self._xml_data["VASSAL.build.widget.PieceSlot"]

        for marker_raw in markers_raw:
            try:
                _unit = Unit(self, marker_raw, bson_data)
                if _unit.back_png is None:
                    _unit.back_png = _unit.front_png
                    _unit.back_png_url = _unit.front_png_url

                self.markers.append(_unit)
            except ValueError as e:
                print("Weird Marker:  {0}".format(marker_raw.get("@entryName")))


def extract_vassal_file(vmod_path, vmod_temp):
    # create temp directory
    if not os.path.exists(vmod_temp):
        os.mkdir(vmod_temp)

    with ZipFile(vmod_path, 'r') as vmod_zip:
        vmod_zip.extractall(vmod_temp)


def parse_redstrike_hierarchy(buildfile_path, bson_data):
    # actual processing
    data_raw = None
    with open(buildfile_path, 'r') as f:
        data_raw = xmltodict.parse(f.read())

    # A VASSAL.build.module.PieceWindow (there are more than one) contains a set of
    ## VASSAL.build.widget.TabWidget, each of which might be a nation
    # In v1.2, the GameModule -> 0th PieceWindow -> TabWidget -> TabWidget is the set of Factions
    entries_raw = data_raw["VASSAL.build.GameModule"]["VASSAL.build.module.PieceWindow"][0]["VASSAL.build.widget.TabWidget"]["VASSAL.build.widget.TabWidget"]
    
    factions = []
    decks = []
    markers = []

    for entry_raw in entries_raw:
        entryName = entry_raw.get("@entryName")

        if not ((entryName == "Markers") or (entryName == "Cards")):
            factions.append(Faction(entry_raw, bson_data))
        
        if (entryName == "Cards"):
            decks_raw = entry_raw["VASSAL.build.widget.TabWidget"]
            for deck_raw in decks_raw:
                decks.append(Deck(deck_raw, bson_data))

        if (entryName == "Markers"):
            # All markers are in separated into categories by a ListWidget
            marker_categories_raw = entry_raw["VASSAL.build.widget.ListWidget"]
            for category_raw in marker_categories_raw:
                markers.append(MarkerCategory(category_raw, bson_data))

    return factions, decks, markers


def parse_bson(bson_path):
    data = {}
    with open(bson_path, 'rb') as bson_file:
        data = bson.loads(bson_file.read())
    return data
            

def publish_faction_json(factions, json_path):
    # build dictionary representation
    data = {}
    for faction in factions:
        faction_dict = {}
        for nation in faction.nations:
            nation_dict = {}
            for command in nation.commands:
                command_dict = {}
                for subordinate_command in command.subordinate_commands:
                    subordinate_command_dict = {}
                    for subordinate_command2 in subordinate_command.subordinate_commands:
                        subordinate_command2_dict = {}  # :/ this is getting ugly
                        for unit in subordinate_command2.units:
                            unit_dict = {
                                "front_png":        unit.front_png,
                                "front_png_url":    unit.front_png_url,
                                "back_png":         unit.back_png,
                                "back_png_url":     unit.back_png_url
                            }
                            subordinate_command2_dict[unit.name] = unit_dict
                        subordinate_command_dict[subordinate_command2.name] = subordinate_command2_dict
                    for unit in subordinate_command.units:
                        unit_dict = {
                            "front_png":        unit.front_png,
                            "front_png_url":    unit.front_png_url,
                            "back_png":         unit.back_png,
                            "back_png_url":     unit.back_png_url
                        }
                        subordinate_command_dict[unit.name] = unit_dict
                    command_dict[subordinate_command.name] = subordinate_command_dict
                for unit in command.units:
                    unit_dict = {
                        "front_png":        unit.front_png,
                        "front_png_url":    unit.front_png_url,
                        "back_png":         unit.back_png,
                        "back_png_url":     unit.back_png_url
                    }
                    command_dict[unit.name] = unit_dict
                nation_dict[command.name] = command_dict
            faction_dict[nation.name] = nation_dict
        data[faction.name] = faction_dict
    
    with open(json_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)


def publish_decks_json(decks, json_path):
    data = {}

    for deck in decks:
        deck_dict = {}
        for card in deck.cards:
            card_dict = {
                "front_png":        card.front_png,
                "front_png_url":    card.front_png_url,
                "back_png":         card.back_png,
                "back_png_url":     card.back_png_url
            }
            deck_dict[card.name] = card_dict
        data[deck.name] = deck_dict

    with open(json_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)


def publish_markers_json(markers, json_path):
    data = {}

    for category in markers:
        category_dict = {}
        for marker in category.markers:
            marker_dict = {
                "front_png":        marker.front_png,
                "front_png_url":    marker.front_png_url,
                "back_png":         marker.back_png,
                "back_png_url":     marker.back_png_url
            }
            category_dict[marker.name] = marker_dict
        data[category.name] = category_dict

    with open(json_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)


def cleanup(vmod_temp):
    shutil.rmtree(vmod_temp)


if __name__ == "__main__":
    vmod_temp = "./temp"
    vmod_path = "./Red_Strike_V1_2.vmod"
    bson_path = "./CloudInfo.bson"
    buildfile_path = os.path.abspath("{0}//{1}".format(vmod_temp, "buildFile.xml"))
    factions_json_path = "{0}_factions.json".format(vmod_path)
    cards_json_path = "{0}_cards.json".format(vmod_path)
    markers_json_path = "{0}_markers.json".format(vmod_path)

    extract_vassal_file(vmod_path, vmod_temp)
    bson_data = parse_bson(bson_path)
    factions, decks, markers = parse_redstrike_hierarchy(buildfile_path, bson_data)
    cleanup(vmod_temp)

    # jsons for debugging
    publish_faction_json(factions, factions_json_path)
    publish_decks_json(decks, cards_json_path)
    publish_markers_json(markers, markers_json_path)
    print("DONE!")
