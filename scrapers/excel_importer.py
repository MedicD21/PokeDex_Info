#!/usr/bin/env python3
"""
Excel Data Importer
Reads Master_Pokedex_Database.xlsx and merges data with existing pokemon_data.json
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "utils"))

import json
import pandas as pd
from typing import Dict, List, Any, Optional
from config import PokeDataUtils, DATA_FILES


class ExcelDataImporter:
    """Imports Pokemon data from Excel file and merges with existing JSON data"""

    def __init__(self):
        self.utils = PokeDataUtils()
        self.excel_file = "Master_Pokedex_Database.xlsx"

        # Define comprehensive column mappings for all data categories
        self.column_mappings = {
            # Basic Info
            "name": "Name",
            "pokedex_number": "National Dex #",
            "form": "Form",
            "species": "Species",
            "gender": "Gender",
            # Types & Abilities
            "type_1": "Type 1",
            "type_2": "Type 2",
            "ability_1": "Ability 1",
            "ability_2": "Ability 2",
            "hidden_ability": "Hidden Ability",
            # Base Stats
            "hp": "HP",
            "attack": "Attack",
            "defense": "Defense",
            "sp_attack": "Sp. Attack",
            "sp_defense": "Sp. Defense",
            "speed": "Speed",
            "bst": "BST",
            # Physical Info
            "height": "Height",
            "weight": "Weight",
            "color": "Color",
            "shape": "Shape",
            "footprint": "Footprint",
            "catch_rate": "Catch Rate",
            "base_exp": "Base EXP",
            # Breeding Info
            "egg_group_1": "Egg Group 1",
            "egg_group_2": "Egg Group 2",
            "gender_ratio": "Gender Ratio",
            "egg_cycles": "Egg Cycles",
            "base_friendship": "Base Friendship",
            "growth_rate": "Growth Rate",
            # Game Mechanics
            "ev_yield": "EV Yield",
        }

    def _process_breeding_info(self, row: pd.Series) -> Dict[str, Any]:
        """Process breeding information from Excel row"""
        breeding_info = {}

        # Egg Groups
        egg_groups = []
        if pd.notna(row.get("Egg Group 1")):
            egg_groups.append(row["Egg Group 1"])
        if pd.notna(row.get("Egg Group 2")):
            egg_groups.append(row["Egg Group 2"])
        if egg_groups:
            breeding_info["egg_groups"] = egg_groups

        # Gender Ratio
        if pd.notna(row.get("Gender Ratio")):
            breeding_info["gender_ratio"] = self._clean_gender_ratio(
                row["Gender Ratio"]
            )

        # Egg Cycles
        if pd.notna(row.get("Egg Cycles")):
            breeding_info["egg_cycles"] = row["Egg Cycles"]

        # Base Friendship
        if pd.notna(row.get("Base Friendship")):
            breeding_info["base_friendship"] = row["Base Friendship"]

        # Growth Rate
        if pd.notna(row.get("Growth Rate")):
            breeding_info["growth_rate"] = row["Growth Rate"]

        return breeding_info

    def _clean_gender_ratio(self, value: Any) -> Any:
        """Clean up gender ratio values coming from the spreadsheet.

        The spreadsheet sometimes stores genderless as comma-separated characters
        (eg. "G,e,n,d,e,r,l,e,s,s"). We want to join those into a single word
        "Genderless" while leaving numeric ratios ("87.5% male, 12.5% female")
        and other complex strings intact.
        """
        if not isinstance(value, str):
            return value

        val = value.strip()

        # If the value contains a percentage or digits, assume it's already a numeric ratio
        if any(ch.isdigit() for ch in val) or "%" in val:
            return val

        # If it looks like comma-separated letters (or letters+spaces), join them
        if "," in val:
            # Remove commas and spaces
            joined = val.replace(",", "").replace(" ", "").strip()
            if joined.isalpha():
                # Normalize capitalization (e.g., genderless)
                return joined.capitalize()
            # If the joined result isn't a simple word, fall back to original trimmed value
            return val.replace(", ", "")

        return val

    def _process_game_mechanics(self, row: pd.Series) -> Dict[str, Any]:
        """Process game mechanics data from Excel row"""
        mechanics = {}

        # EV Yield
        if pd.notna(row.get("EV Yield")):
            mechanics["ev_yield"] = row["EV Yield"]

        # Catch Rate
        if pd.notna(row.get("Catch Rate")):
            mechanics["catch_rate"] = row["Catch Rate"]

        # Base EXP
        if pd.notna(row.get("Base EXP")):
            mechanics["base_exp"] = row["Base EXP"]

        return mechanics

    def _process_physical_info(self, row: pd.Series) -> Dict[str, Any]:
        """Process physical information from Excel row"""
        physical = {}

        # Height
        if pd.notna(row.get("Height")):
            physical["height"] = row["Height"]

        # Weight
        if pd.notna(row.get("Weight")):
            physical["weight"] = row["Weight"]

        # Color
        if pd.notna(row.get("Color")):
            physical["color"] = row["Color"]

        # Shape
        if pd.notna(row.get("Shape")):
            physical["shape"] = row["Shape"]

        # Footprint
        if pd.notna(row.get("Footprint")):
            physical["footprint"] = row["Footprint"]

        return physical

    def _process_dex_entries(self, row: pd.Series) -> Dict[str, str]:
        """Process Pokedex entries from Excel row"""
        dex_entries = {}

        # Map of Excel columns to game names
        dex_mapping = {
            "Red Dex Text": "red",
            "Blue Dex Text": "blue",
            "Yellow Dex Text": "yellow",
            "Gold Dex Text": "gold",
            "Silver Dex Text": "silver",
            "Crystal Dex Text": "crystal",
            "Ruby Dex Text": "ruby",
            "Sapphire Dex Text": "sapphire",
            "Emerald Dex Text": "emerald",
            "FireRed Dex Text": "firered",
            "LeafGreen Dex Text": "leafgreen",
            "Diamond Dex Text": "diamond",
            "Pearl Dex Text": "pearl",
            "Platinum Dex Text": "platinum",
            "HeartGold Dex Text": "heartgold",
            "SoulSilver Dex Text": "soulsilver",
            "Black Dex Text": "black",
            "White Dex Text": "white",
            "Black 2 Dex Text": "black2",
            "White 2 Dex Text": "white2",
            "X Dex Text": "x",
            "Y Dex Text": "y",
            "Omega Ruby Dex Text": "omegaruby",
            "Alpha Sapphire Dex Text": "alphasapphire",
            "Sun Dex Text": "sun",
            "Moon Dex Text": "moon",
            "Ultra Sun Dex Text": "ultrasun",
            "Ultra Moon Dex Text": "ultramoon",
            "Sword Dex Text": "sword",
            "Shield Dex Text": "shield",
        }

        for excel_col, game_key in dex_mapping.items():
            if excel_col in row.index and pd.notna(row[excel_col]):
                dex_text = str(row[excel_col]).strip()
                if dex_text:
                    dex_entries[game_key] = dex_text

        return dex_entries

    def _process_abilities(self, row: pd.Series) -> Dict[str, Any]:
        """Process ability information from Excel row"""
        abilities = {}

        # Regular abilities
        regular_abilities = []
        if pd.notna(row.get("Ability 1")):
            regular_abilities.append(row["Ability 1"])
        if pd.notna(row.get("Ability 2")):
            regular_abilities.append(row["Ability 2"])
        if regular_abilities:
            abilities["regular"] = regular_abilities

        # Hidden ability
        if pd.notna(row.get("Hidden Ability")):
            abilities["hidden"] = row["Hidden Ability"]

        return abilities

    def _process_types(self, row: pd.Series) -> List[str]:
        """Process type information from Excel row"""
        types = []

        # Use Type Helper columns if available, otherwise fall back to Type columns
        type1 = row.get("Type 1 Helper", row.get("Type 1"))
        type2 = row.get("Type 2 Helper", row.get("Type 2"))

        if pd.notna(type1):
            types.append(type1)
        if pd.notna(type2):
            types.append(type2)

        return types

    def read_excel_data(self) -> Dict[str, pd.DataFrame]:
        """Read the MasterDex sheet from the Excel file"""
        print(f"Reading Excel file: {self.excel_file}")

        try:
            # Read only the MasterDex sheet with row 2 as headers (0-indexed, so header=1)
            excel_data = pd.read_excel(
                self.excel_file, sheet_name="MasterDex", header=1
            )

            print(f"Successfully loaded 'MasterDex' sheet:")
            print(f"  - {len(excel_data)} rows, {len(excel_data.columns)} columns")
            print(
                f"    Columns: {list(excel_data.columns)[:5]}{'...' if len(excel_data.columns) > 5 else ''}"
            )

            # Return as dict format to maintain compatibility with rest of code
            return {"MasterDex": excel_data}

        except Exception as e:
            print(f"Error reading Excel file: {e}")
            return {}

    def analyze_excel_structure(self, excel_data: Dict[str, pd.DataFrame]):
        """Analyze the structure of Excel data to understand what we have"""
        print("\n=== Excel Data Analysis ===")

        for sheet_name, df in excel_data.items():
            print(f"\nSheet: {sheet_name}")
            print("-" * 40)
            print(f"Shape: {df.shape}")
            print(f"Columns: {list(df.columns)}")

            # Show first few rows
            print(f"Sample data:")
            print(df.head(3).to_string(index=False))

            # Check for Pokemon names or numbers
            if any(
                isinstance(col, str)
                and col.lower() in ["name", "pokemon", "number", "id", "#"]
                for col in df.columns
            ):
                print(f"✓ Looks like Pokemon data!")

            print()

    def map_excel_to_json_structure(
        self, excel_data: Dict[str, pd.DataFrame]
    ) -> List[Dict]:
        """Convert Excel data to our JSON structure"""
        print("Converting Excel data to JSON structure...")

        pokemon_list = []

        # Try to find the main Pokemon sheet
        main_sheet = None
        sheet_name_used = None
        for sheet_name, df in excel_data.items():
            # Look for sheets that likely contain main Pokemon data
            if any(
                keyword in sheet_name.lower()
                for keyword in ["pokemon", "pokedex", "main", "data", "master"]
            ):
                main_sheet = df
                sheet_name_used = sheet_name
                print(f"Using '{sheet_name}' as main Pokemon data sheet")
                break

        if main_sheet is None:
            # Use the first sheet if no obvious main sheet
            main_sheet = list(excel_data.values())[0]
            sheet_name_used = list(excel_data.keys())[0]
            print(f"Using first sheet '{sheet_name_used}' as main Pokemon data")

        # Debug: Check how many -00 entries we have
        total_rows = len(main_sheet)
        base_form_rows = main_sheet[
            main_sheet["ref_id"].astype(str).str.endswith("-00", na=False)
        ]
        print(f"Total rows in Excel: {total_rows}")
        print(f"Base forms (-00) found: {len(base_form_rows)}")

        # Convert each row to Pokemon entry
        pokemon_list = []
        for index, row in main_sheet.iterrows():
            # Process Pokemon that have names
            has_name = pd.notna(row.get("Name", ""))
            ref_id = row.get("ref_id", "")

            # Process if:
            # 1. Has ref_id ending with -00 (base forms with ref_id), OR
            # 2. Has name but no ref_id (most Pokemon in the sheet)
            should_process = False
            if isinstance(ref_id, str) and ref_id.endswith("-00"):
                should_process = True  # Base form with ref_id
            elif has_name and (pd.isna(ref_id) or ref_id == ""):
                should_process = True  # Pokemon with name but no ref_id

            if should_process:
                pokemon = self._convert_row_to_pokemon(row)
                if pokemon:
                    pokemon_list.append(pokemon)

        print(f"Converted {len(pokemon_list)} Pokemon from Excel data")
        return pokemon_list

    def _convert_row_to_pokemon(self, row: pd.Series) -> Optional[Dict]:
        """Convert a single Excel row to comprehensive Pokemon JSON structure"""
        pokemon = {}

        # Basic Information
        if pd.notna(row.get("Name")):
            pokemon["name"] = row["Name"]

        # Try multiple column names for pokedex number
        dex_num = row.get("National Dex #") or row.get("National Dex Number")
        if pd.notna(dex_num):
            pokemon["pokedex_number"] = int(dex_num)

        if pd.notna(row.get("Species")):
            pokemon["species"] = row["Species"]
        if pd.notna(row.get("Form")):
            pokemon["form"] = row["Form"]

        # Types
        types = self._process_types(row)
        if types:
            pokemon["types"] = types

        # Abilities
        abilities = self._process_abilities(row)
        if abilities:
            pokemon["abilities"] = abilities

        # Base Stats (force override existing)
        base_stats = {}
        stat_mappings = {
            "hp": "HP",
            "attack": "Attack",
            "defense": "Defense",
            "sp_attack": "Sp. Atk",
            "sp_defense": "Sp. Def",
            "speed": "Speed",
        }

        for json_key, excel_key in stat_mappings.items():
            if pd.notna(row.get(excel_key)):
                base_stats[json_key] = int(row[excel_key])

        if pd.notna(row.get("BST")):
            base_stats["total"] = int(row["BST"])

        if base_stats:
            pokemon["base_stats"] = base_stats

        # Physical Information
        physical_info = self._process_physical_info(row)
        if physical_info:
            pokemon["physical_info"] = physical_info

        # Breeding Information
        breeding_info = self._process_breeding_info(row)
        if breeding_info:
            pokemon["breeding_info"] = breeding_info

        # Game Mechanics
        game_mechanics = self._process_game_mechanics(row)
        if game_mechanics:
            pokemon["game_mechanics"] = game_mechanics

        # Pokedex Entries
        dex_entries = self._process_dex_entries(row)
        if dex_entries:
            pokemon["dex_entries"] = dex_entries

        # Game Appearances (process location data)
        game_appearances = self._process_game_data(row.to_dict())
        if game_appearances:
            pokemon["game_appearances"] = game_appearances

        return pokemon if pokemon.get("name") else None

    def _process_game_data(self, row_dict: Dict) -> Dict:
        """Process game appearances and locations from Excel row"""
        game_appearances = {}

        # Define game mappings from Excel column names to our game names
        game_mappings = {
            "Red": "Red",
            "Blue": "Blue",
            "Yellow": "Yellow",
            "Gold": "Gold",
            "Silver": "Silver",
            "Crystal": "Crystal",
            "Ruby": "Ruby",
            "Sapphire": "Sapphire",
            "Emerald": "Emerald",
            "FireRed": "FireRed",
            "LeafGreen": "LeafGreen",
            "Diamond": "Diamond",
            "Pearl": "Pearl",
            "Platinum": "Platinum",
            "HeartGold": "HeartGold",
            "SoulSilver": "SoulSilver",
            "Black": "Black",
            "White": "White",
            "Black-2": "Black 2",
            "White-2": "White 2",
            "X": "X",
            "Y": "Y",
            "Omega-Ruby": "Omega Ruby",
            "Alpha-Sapphire": "Alpha Sapphire",
            "Sun": "Sun",
            "Moon": "Moon",
            "Ultra-Sun": "Ultra Sun",
            "Ultra-Moon": "Ultra Moon",
            "Lets-Go-Pikachu": "Let's Go Pikachu",
            "Lets-Go-Eevee": "Let's Go Eevee",
            "Sword": "Sword",
            "Shield": "Shield",
            "The-Isle-Of-Armor": "The Isle of Armor",
            "The Crown Tundra": "The Crown Tundra",
            "Brilliant-Diamond": "Brilliant Diamond",
            "Shining-Pearl": "Shining Pearl",
            "Legends-Arceus": "Legends: Arceus",
            "Scarlet": "Scarlet",
            "Violet": "Violet",
            "The-Teal-Mask": "The Teal Mask",
            "The-Indigo-Disk": "The Indigo Disk",
            "Legends-Z-A": "Legends Z-A",
        }

        # Location column mappings (Excel column to game name)
        location_mappings = {
            "Red Location": "Red",
            "Blue Location": "Blue",
            "Yellow Location": "Yellow",
            "Gold Location": "Gold",
            "Silver Location": "Silver",
            "Crystal Location": "Crystal",
            "Ruby Location": "Ruby",
            "Sapphire Location": "Sapphire",
            "Emerald Location": "Emerald",
            "FireRed Location": "FireRed",
            "LeafGreen Location": "LeafGreen",
            "Diamond Location": "Diamond",
            "Pearl Location": "Pearl",
            "Platinum Location": "Platinum",
            "HeartGold Location": "HeartGold",
            "SoulSilver Location": "SoulSilver",
            "Black Location": "Black",
            "White Location": "White",
            "Black 2 Location": "Black 2",
            "White 2 Location": "White 2",
            "X Location": "X",
            "Y Location": "Y",
            "Omega Ruby Location": "Omega Ruby",
            "Alpha Sapphire Location": "Alpha Sapphire",
            "Sun Location": "Sun",
            "Moon Location": "Moon",
            "Ultra Sun Location": "Ultra Sun",
            "Ultra Moon Location": "Ultra Moon",
            "Let's Go Pikachu Location": "Let's Go Pikachu",
            "Let's Go Eevee Location": "Let's Go Eevee",
            "Sword Location": "Sword",
            "Shield Location": "Shield",
            "The Isle of Armor Location": "The Isle of Armor",
            "The Crown Tundra Location": "The Crown Tundra",
            "Brilliant Diamond Location": "Brilliant Diamond",
            "Shining Pearl Location": "Shining Pearl",
            "Legends: Arceus Location": "Legends: Arceus",
            "Scarlet Location": "Scarlet",
            "Violet Location": "Violet",
            "The Teal Mask Location": "The Teal Mask",
            "The Indigo Disk Location": "The Indigo Disk",
            "Legends: Z-A Location": "Legends Z-A",
        }

        # Process each game
        for excel_game, our_game in game_mappings.items():
            # Check if dex number exists for this game (keys are case-sensitive)
            dex_number = row_dict.get(excel_game)

            # Find corresponding location column
            location = None
            for location_col, location_game in location_mappings.items():
                if location_game == our_game:
                    location = row_dict.get(location_col)
                    break

            if pd.notna(dex_number) and dex_number != "":
                game_entry = {
                    "dex_number": (
                        int(float(dex_number)) if pd.notna(dex_number) else None
                    ),
                    "available": True,
                }

                # Add location if available
                if pd.notna(location) and str(location).strip() != "":
                    location_str = str(location).strip()
                    if location_str.lower() not in ["nan", "none", ""]:
                        game_entry["location"] = location_str

                game_appearances[our_game] = game_entry

        return game_appearances

    def merge_with_existing_data(self, excel_pokemon: List[Dict]) -> List[Dict]:
        """Merge Excel data with existing JSON data"""
        print("Merging Excel data with existing pokemon_data.json...")

        # Load existing data
        existing_data = self.utils.load_json_data(DATA_FILES["pokemon"])
        if not isinstance(existing_data, list):
            existing_data = []

        print(f"Existing data: {len(existing_data)} Pokemon")
        print(f"Excel data: {len(excel_pokemon)} Pokemon")

        # Create lookup for existing Pokemon by name
        existing_lookup = {
            p.get("name", "").lower(): i for i, p in enumerate(existing_data)
        }

        merged_count = 0
        new_count = 0

        for excel_pokemon_entry in excel_pokemon:
            name = excel_pokemon_entry.get("name", "").lower()

            if name in existing_lookup:
                # Merge with existing entry
                existing_index = existing_lookup[name]
                existing_entry = existing_data[existing_index]

                # Merge data (Excel data takes precedence for missing fields)
                merged_entry = self._merge_pokemon_entries(
                    existing_entry, excel_pokemon_entry
                )
                existing_data[existing_index] = merged_entry
                merged_count += 1
            else:
                # Add new Pokemon
                existing_data.append(excel_pokemon_entry)
                new_count += 1

        print(f"Merged {merged_count} existing Pokemon with Excel data")
        print(f"Added {new_count} new Pokemon from Excel")
        print(f"Total Pokemon: {len(existing_data)}")

        return existing_data

    def _merge_pokemon_entries(self, existing: Dict, excel: Dict) -> Dict:
        """Merge two Pokemon entries, preferring existing data but filling gaps with Excel data"""
        merged = existing.copy()

        for key, value in excel.items():
            # Special case: Always overwrite evolution_info from Excel (more accurate)
            if key == "evolution_info":
                merged[key] = value
            # Special case: Merge base_stats intelligently (preserve existing + add from Excel)
            elif key == "base_stats" and isinstance(value, dict):
                if "base_stats" not in merged:
                    merged["base_stats"] = {}

                # Keep existing base_stats
                existing_stats = merged.get("base_stats", {}).copy()

                # Update/add stats from Excel
                for stat_key, stat_value in value.items():
                    existing_stats[stat_key] = stat_value

                merged["base_stats"] = existing_stats
            # Special case: Merge game_appearances intelligently
            elif key == "game_appearances" and isinstance(value, dict):
                if "game_appearances" not in merged:
                    merged["game_appearances"] = {}

                # Merge each game's data
                for game_name, game_data in value.items():
                    if game_name in merged["game_appearances"]:
                        # Merge with existing game entry, adding location data
                        existing_game = merged["game_appearances"][game_name]
                        merged_game = existing_game.copy()

                        # Add location if it exists in Excel data
                        if "location" in game_data:
                            merged_game["location"] = game_data["location"]

                        # Update other fields if missing
                        for field, field_value in game_data.items():
                            if field not in merged_game or not merged_game[field]:
                                merged_game[field] = field_value

                        merged["game_appearances"][game_name] = merged_game
                    else:
                        # Add new game entry
                        merged["game_appearances"][game_name] = game_data

            # Special case: Merge breeding_info but prefer Excel gender_ratio
            elif key == "breeding_info" and isinstance(value, dict):
                if "breeding_info" not in merged:
                    merged["breeding_info"] = {}

                for sub_key, sub_value in value.items():
                    if sub_key == "gender_ratio":
                        # Always take Excel's gender_ratio (cleaned)
                        merged["breeding_info"][sub_key] = self._clean_gender_ratio(
                            sub_value
                        )
                    elif (
                        sub_key not in merged["breeding_info"]
                        or not merged["breeding_info"][sub_key]
                    ):
                        merged["breeding_info"][sub_key] = sub_value
            elif key not in merged or not merged[key]:
                # Add missing field from Excel
                merged[key] = value
            elif isinstance(value, dict) and isinstance(merged[key], dict):
                # Merge nested dictionaries
                for sub_key, sub_value in value.items():
                    if sub_key not in merged[key] or not merged[key][sub_key]:
                        merged[key][sub_key] = sub_value
            elif isinstance(value, list) and isinstance(merged[key], list):
                # Merge lists (avoid duplicates)
                for item in value:
                    if item not in merged[key]:
                        merged[key].append(item)

        return merged

    def save_merged_data(self, merged_data: List[Dict]):
        """Save the merged data to pokemon_data.json"""
        print("Saving merged data to pokemon_data.json...")

        # Create backup first
        backup_path = f"data/pokemon_data_backup_before_excel.json"
        existing_data = self.utils.load_json_data(DATA_FILES["pokemon"])
        if existing_data:
            self.utils.save_json_data(existing_data, backup_path)
            print(f"Created backup: {backup_path}")

        # Save merged data
        self.utils.save_json_data(merged_data, DATA_FILES["pokemon"])
        print(f"Saved {len(merged_data)} Pokemon to {DATA_FILES['pokemon']}")

    def run_import(self):
        """Main import process"""
        print("=== Excel Data Import Process ===")

        # Check if Excel file exists
        if not os.path.exists(self.excel_file):
            print(f"Excel file not found: {self.excel_file}")
            return

        # Read Excel data
        excel_data = self.read_excel_data()
        if not excel_data:
            print("No data read from Excel file")
            return

        # Analyze structure
        self.analyze_excel_structure(excel_data)

        # Ask user to proceed
        print("\n" + "=" * 50)
        proceed = input("Proceed with import? (y/n): ").strip().lower()
        if proceed != "y":
            print("Import cancelled")
            return

        # Convert to JSON structure
        excel_pokemon = self.map_excel_to_json_structure(excel_data)
        if not excel_pokemon:
            print("No Pokemon data found in Excel file")
            return

        # Show sample of converted data
        print(f"\nSample converted Pokemon:")
        for i, pokemon in enumerate(excel_pokemon[:2]):
            print(f"  {i+1}. {pokemon.get('name', 'Unknown')}")
            print(f"     Number: {pokemon.get('number', 'N/A')}")
            print(f"     Types: {pokemon.get('types', 'N/A')}")
            if "base_stats" in pokemon:
                print(f"     Base Stats: {pokemon['base_stats']}")

        # Confirm merge
        merge_confirm = (
            input(f"\nMerge {len(excel_pokemon)} Pokemon with existing data? (y/n): ")
            .strip()
            .lower()
        )
        if merge_confirm != "y":
            print("Merge cancelled")
            return

        # Merge and save
        merged_data = self.merge_with_existing_data(excel_pokemon)
        self.save_merged_data(merged_data)

        print("\n✅ Excel import completed successfully!")
        print(f"📁 Data saved to: {DATA_FILES['pokemon']}")
        print(f"💾 Backup created: data/pokemon_data_backup_before_excel.json")


def main():
    """Main function"""
    importer = ExcelDataImporter()
    importer.run_import()


if __name__ == "__main__":
    main()
