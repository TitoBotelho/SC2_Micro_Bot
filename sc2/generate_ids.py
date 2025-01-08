# pylint: disable=W0212
import importlib
import json
import platform
import sys
from pathlib import Path

from loguru import logger

from sc2.game_data import AbilityData, GameData, UnitTypeData, UpgradeData
from sc2.ids.ability_id import AbilityId

try:
    from sc2.ids.id_version import ID_VERSION_STRING
except ImportError:
    ID_VERSION_STRING = "4.11.4.78285"


class IdGenerator:

    def __init__(self, game_data: GameData = None, game_version: str = None, verbose: bool = False):
        self.game_data: GameData = game_data
        self.game_version = game_version
        self.verbose = verbose

        self.HEADER = f'from __future__ import annotations\n# DO NOT EDIT!\n# This file was automatically generated by "{Path(__file__).name}"\n'

        self.PF = platform.system()

        self.HOME_DIR = str(Path.home())
        self.DATA_JSON = {
            "Darwin": self.HOME_DIR
            + "/Library/Application Support/Blizzard/StarCraft II/stableid.json",
            "Windows": self.HOME_DIR + "/Documents/StarCraft II/stableid.json",
            "Linux": self.HOME_DIR + "/Documents/StarCraft II/stableid.json",
        }

        self.ENUM_TRANSLATE = {
            "Units": "UnitTypeId",
            "Abilities": "AbilityId",
            "Upgrades": "UpgradeId",
            "Buffs": "BuffId",
            "Effects": "EffectId",
        }

        self.FILE_TRANSLATE = {
            "Units": "unit_typeid",
            "Abilities": "ability_id",
            "Upgrades": "upgrade_id",
            "Buffs": "buff_id",
            "Effects": "effect_id",
        }

    @staticmethod
    def make_key(key):
        if key[0].isdigit():
            key = "_" + key
        # In patch 5.0, the key has "@" character in it which is not possible with python enums
        return key.upper().replace(" ", "_").replace("@", "")

    def parse_data(self, data):
        # for d in data:  # Units, Abilities, Upgrades, Buffs, Effects

        units = self.parse_simple("Units", data)
        upgrades = self.parse_simple("Upgrades", data)
        effects = self.parse_simple("Effects", data)
        buffs = self.parse_simple("Buffs", data)

        abilities = {}
        for v in data["Abilities"]:
            key = v["buttonname"]
            remapid = v.get("remapid")

            if (not key) and (remapid is None):
                assert v["buttonname"] == ""
                continue

            if not key:
                if v["friendlyname"] != "":
                    key = v["friendlyname"]
                else:
                    sys.exit(f"Not mapped: {v !r}")

            key = key.upper().replace(" ", "_").replace("@", "")

            if "name" in v:
                key = f'{v["name"].upper().replace(" ", "_")}_{key}'

            if "friendlyname" in v:
                key = v["friendlyname"].upper().replace(" ", "_")

            if key[0].isdigit():
                key = "_" + key

            if key in abilities and v["index"] == 0:
                logger.info(f"{key} has value 0 and id {v['id']}, overwriting {key}: {abilities[key]}")
                # Commented out to try to fix: 3670 is not a valid AbilityId
                abilities[key] = v["id"]
            elif key in abilities:
                logger.info(f"{key} has appeared a second time with id={v['id']}")
            else:
                abilities[key] = v["id"]

        abilities["SMART"] = 1

        enums = {}
        enums["Units"] = units
        enums["Abilities"] = abilities
        enums["Upgrades"] = upgrades
        enums["Buffs"] = buffs
        enums["Effects"] = effects

        return enums

    def parse_simple(self, d, data):
        units = {}
        for v in data[d]:
            key = v["name"]

            if not key:
                continue
            key_to_insert = self.make_key(key)
            if key_to_insert in units:
                index = 2
                tmp = f"{key_to_insert}_{index}"
                while tmp in units:
                    index += 1
                    tmp = f"{key_to_insert}_{index}"
                key_to_insert = tmp
            units[key_to_insert] = v["id"]

        return units

    def generate_python_code(self, enums):
        assert {"Units", "Abilities", "Upgrades", "Buffs", "Effects"} <= enums.keys()

        sc2dir = Path(__file__).parent
        idsdir = sc2dir / "ids"
        idsdir.mkdir(exist_ok=True)

        with (idsdir / "__init__.py").open("w") as f:
            initstring = f"__all__ = {[n.lower() for n in self.FILE_TRANSLATE.values()] !r}\n".replace(
                "'", '"'
            )
            f.write("\n".join([self.HEADER, initstring]))

        for name, body in enums.items():
            class_name = self.ENUM_TRANSLATE[name]

            code = [self.HEADER, "import enum", "\n", f"class {class_name}(enum.Enum):"]

            for key, value in sorted(body.items(), key=lambda p: p[1]):
                code.append(f"    {key} = {value}")

            # Add repr function to more easily dump enums to dict
            code += f"""
    def __repr__(self) -> str:
        return f"{class_name}.{{self.name}}"
""".split("\n")

            # Add missing ids function to not make the game crash when unknown BuffId was detected
            if class_name == "BuffId":
                code += f"""
    @classmethod
    def _missing_(cls, value: int) -> {class_name}:
        return cls.NULL
""".split("\n")

            if class_name == "AbilityId":
                code += f"""
    @classmethod
    def _missing_(cls, value: int) -> {class_name}:
        return cls.NULL_NULL
""".split("\n")

            code += f"""
for item in {class_name}:
    globals()[item.name] = item
""".split("\n")

            ids_file_path = (idsdir / self.FILE_TRANSLATE[name]).with_suffix(".py")
            with ids_file_path.open("w") as f:
                f.write("\n".join(code))

        if self.game_version is not None:
            version_path = Path(__file__).parent / "ids" / "id_version.py"
            with open(version_path, "w") as f:
                f.write(f'ID_VERSION_STRING = "{self.game_version}"\n')

    def update_ids_from_stableid_json(self):
        if (
            self.game_version is None
            or ID_VERSION_STRING is None
            or ID_VERSION_STRING != self.game_version
        ):
            if (
                self.verbose
                and self.game_version is not None
                and ID_VERSION_STRING is not None
            ):
                logger.info(
                    f"Game version is different (Old: {self.game_version}, new: {ID_VERSION_STRING}. Updating ids to match game version"
                )
            stable_id_path = Path(self.DATA_JSON[self.PF])
            assert stable_id_path.is_file(), f"stable_id.json was not found at path \"{stable_id_path}\""
            with stable_id_path.open(encoding="utf-8") as data_file:
                data = json.loads(data_file.read())
            self.generate_python_code(self.parse_data(data))

            # Update game_data if this is a live game
            if self.game_data is not None:
                self.reimport_ids()
                self.update_game_data()

    @staticmethod
    def reimport_ids():

        # Reload the newly written "id" files
        # TODO This only re-imports modules, but if they haven't been imported, it will yield an error
        importlib.reload(sys.modules["sc2.ids.ability_id"])

        importlib.reload(sys.modules["sc2.ids.unit_typeid"])

        importlib.reload(sys.modules["sc2.ids.upgrade_id"])

        importlib.reload(sys.modules["sc2.ids.effect_id"])

        importlib.reload(sys.modules["sc2.ids.buff_id"])

        # importlib.reload(sys.modules["sc2.ids.id_version"])

        importlib.reload(sys.modules["sc2.constants"])

    def update_game_data(self):
        """Re-generate the dicts from self.game_data.
        This should be done after the ids have been reimported."""
        ids = set(a.value for a in AbilityId if a.value != 0)
        self.game_data.abilities = {
            a.ability_id: AbilityData(self.game_data, a)
            for a in self.game_data._proto.abilities if a.ability_id in ids
        }
        # self.game_data.abilities = {
        #     a.ability_id: AbilityData(self.game_data, a) for a in self.game_data._proto.abilities
        # }
        self.game_data.units = {
            u.unit_id: UnitTypeData(self.game_data, u)
            for u in self.game_data._proto.units if u.available
        }
        self.game_data.upgrades = {u.upgrade_id: UpgradeData(self.game_data, u) for u in self.game_data._proto.upgrades}


if __name__ == "__main__":
    updater = IdGenerator()
    updater.update_ids_from_stableid_json()