"""A module for representing and working with D&D 5E spells"""

# Adapted from https://github.com/gwrome/dndtools

import re


class Spell:
    """D&D 5E Spell

    Creates a Spell instance, usually from data provided by a JSON file or database. Can parse the data differently
    depending on its source.

    Attributes:
    name: The spell's name
    level (int): The spell's level
    school: The school of magic the spell belongs to, e.g., "Divination"
    cast_time: The spell's casting time, e.g., "1 Action"
    range: The spell's range, e.g., "Touch" or "150 feet"
    components: The spell's required components and materials, e.g., "V, S, M (a tiny ball of bat guano and sulfur)"
    duration: The spell's duration and whether it requires Concentration, e.g., "Instantaneous" or "8 hours"
    description: The spell's effects
    source: The source material containing the spell, e.g. "PHB p. 236"
    ritual (bool): Whether the spell can be cast as a ritual
    """

    def __init__(self, json_dict=None, from_tools=False):
        """Builds a spell object.

        Args:
            json_dict: a dict containing spell attributes (default: None)
            from_tools: a boolean flag set to True if the json_dict contains data
                        formatted like 5e.tools's files (default: False)
        """
        # When building a Spell from a DB row, we want a plain object we can set manually rather than go through
        # all the parsing logic below because the data is already parsed
        if not json_dict:
            return

        # TODO: All this parsing stuff should be broken up into manageable chunks
        if from_tools:
            # Name of the spell
            self.name = json_dict["name"]

            # Spell level
            self.level = str(json_dict["level"])

            # School of Magic
            schools = {
                "A": "Abjuration",
                "C": "Conjuration",
                "D": "Divination",
                "E": "Enchantment",
                "V": "Evocation",
                "I": "Illusion",
                "N": "Necromancy",
                "P": "Psionic",
                "T": "Transmutation",
            }

            self.school = schools[json_dict["school"]]

            # Source of the spell
            self.source = json_dict["source"]
            if "page" in json_dict.keys():  # add the page number, if available
                self.source += " p. " + str(json_dict["page"])

            # Casting time
            self.cast_time = " ".join(
                [str(json_dict["time"][0]["number"]), json_dict["time"][0]["unit"]]
            )
            if "condition" in json_dict["time"][0].keys():
                self.cast_time += (
                    " " + json_dict["time"][0]["condition"]
                )  # see, e.g., Hellish Rebuke

            # Range is encoded differently depending on whether it's touch/self or ranged
            if json_dict["range"].get("distance", None):
                if "amount" in json_dict["range"]["distance"]:
                    self.range = (
                        str(json_dict["range"]["distance"]["amount"])
                        + " "
                        + json_dict["range"]["distance"]["type"]
                    )
                elif "type" in json_dict["range"]["distance"]:
                    self.range = json_dict["range"]["distance"]["type"].title()
            elif json_dict["range"].get("type", None) == "special":
                self.range = "Special"

            # Spell components - Somatic & Verbal components give boolean values
            # if a material component is required, the value is the component's name
            self.components = []
            if json_dict.get("components", None):
                if "v" in json_dict["components"].keys():
                    self.components.append("V")
                if "s" in json_dict["components"].keys():
                    self.components.append("S")
                if "m" in json_dict["components"].keys():
                    if isinstance(json_dict["components"]["m"], dict):
                        self.components.append(
                            "M ({})".format(
                                json_dict["components"]["m"].get(
                                    "text", json_dict["components"]["m"]
                                )
                            )
                        )
                    else:
                        self.components.append(
                            "M ({})".format(json_dict["components"]["m"])
                        )
                self.components = ", ".join(self.components)
            else:
                self.components = "None"

            # Spell duration
            self.duration = ""
            if json_dict["duration"][0]["type"] == "timed":
                self.duration = str(json_dict["duration"][0]["duration"]["amount"])
                self.duration += " {}".format(
                    json_dict["duration"][0]["duration"]["type"]
                )
                if int(json_dict["duration"][0]["duration"]["amount"]) > 1:
                    self.duration += "s"
                if json_dict["duration"][0].get("concentration", False):
                    self.duration += " (concentration)"
            else:
                self.duration = json_dict["duration"][0]["type"]
            self.duration = self.duration.capitalize()

            # Ritual tag
            self.ritual = False
            if "meta" in json_dict.keys() and json_dict["meta"].get("ritual", False):
                self.ritual = True

            # The meat of the spell description
            self.description = ""
            entry_string = ""
            for e in json_dict["entries"]:
                if isinstance(e, dict):
                    # This handles the entries with headers in the description, e.g., Control Winds's types of winds
                    if "name" in e.keys() and "entries" in e.keys():
                        entry_string += "\n\t_*" + e["name"] + ".*_ "
                        for i in e["entries"]:
                            # This logic is, afaik, only for Guards and Wards's embedded
                            # embedded list
                            if isinstance(i, dict):
                                for j in i["items"]:
                                    entry_string += "\n- " + j
                            else:
                                entry_string += i
                    # This handles entries with embedded lists, e.g., Conjure Woodland Beings
                    if "items" in e.keys():
                        for i in e["items"]:
                            entry_string += "\n- " + i
                else:
                    # This is where the plain paragraph part of spell descriptions are handled
                    entry_string += "\n\t" + e
            self.description += "\t" + entry_string + "\n"

            # Handles pretty common "at higher levels" entries, which is separately encoded
            if "entriesHigherLevel" in json_dict.keys():
                self.description += (
                    "__At Higher Levels.__\n\t"
                    + "".join(json_dict["entriesHigherLevel"][0]["entries"])
                    + "\n"
                )

            # Strip all the {@xyz} formatting language from the 5Etools files and replace with plain text
            clean_description = self.description

            replacements = [
                re.compile("(\{@dice ([+\-\d\w\s]*)\})"),  # {@dice 1d4 +1} => 1d4 + 1
                re.compile(
                    "(\{@damage ([+\-\d\w\s]*)\})"
                ),  # {@damage 1d4 +1} => 1d4 + 1
                re.compile("(\{@condition (\w+)\})"),  # {@condition blinded} => blinded
                re.compile(
                    "(\{@scaledice [+\-\|\d\w\s]*(\d+d\d+)\})"
                ),  # {@scaledice 3d12|3-9|1d12} => 1d12
                re.compile(
                    "(\{@scaledamage [+\-\|\d\w\s]*(\d+d\d+)\})"
                ),  # {@scaledamage 3d12|3-9|1d12} => 1d12
                re.compile(
                    "(\{@creature ([\-\w\s]*)\})"
                ),  # {@creature dire wolf} => dire wolf
                re.compile(
                    "(\{@filter ([/\d\w\s]+)\|.+?\})"
                ),  # {@filter challenge rating 6 or lower...}
                re.compile("(\{@spell ([\w\s]+)\})"),  # {@spell fireball} => fireball
            ]
            for r in replacements:
                m = r.findall(clean_description)
                if m:
                    for replacement in m:
                        clean_description = clean_description.replace(
                            replacement[0], replacement[1]
                        )
            self.description = clean_description.strip()
        else:
            self.cast_time = json_dict["casting_time"]
            self.components = json_dict["components"]["raw"]
            self.description = json_dict["description"]
            if json_dict.get("higher_levels", None):
                self.description += (
                    "\n_*At Higher Levels.*_\n" + json_dict["higher_levels"]
                )
            self.duration = json_dict["duration"]
            self.name = json_dict["name"]
            self.range = json_dict["range"]
            self.ritual = json_dict["ritual"]
            self.school = json_dict["school"].title()
            if json_dict["level"] == "cantrip":
                self.level = 0
            else:
                self.level = int(json_dict["level"])
            self.source = "SRD"

    def format_spell_text(spell):
        """Prepares the spell for sending as a Slack message

        Returns:
            A str containing the spell's attributes formatted for sending as Slack message
        """
        # Block Quote
        output = ">>> "

        # Name
        output += "__**{}**__\n".format(spell.name)

        # Level/School/Ritual
        if int(spell.level) != 0:
            output += "_Level {} {}".format(spell.level, spell.school)
        else:
            output += "_{} cantrip".format(spell.school)
        if spell.ritual:
            output += " (ritual)"
        output += "_\n"

        # Casting time
        output += "**Casting Time:** {}\n".format(spell.cast_time)

        # Range
        output += "**Range:** {}\n".format(spell.range)

        # Components
        output += "**Components:** {}\n".format(spell.components)

        # Duration
        output += "**Duration:** {}\n".format(spell.duration)

        # Description
        output += "\n\t" + spell.description + "\n"

        # Source
        if spell.source:
            output += "_" + spell.source + "_"

        return output

    def export_for_sqlite(self):
        """Prepares a spell for saving in a sqlite database

        Returns:
             A tuple of the spell's attributes in the order required by the SQL schema
        """
        return {
            "name": self.name,
            "level": int(self.level),
            "school": self.school,
            "source": self.source,
            "cast_time": self.cast_time,
            "range": self.range,
            "components": self.components,
            "duration": self.duration,
            "ritual": int(self.ritual),
            "description": self.description,
        }
