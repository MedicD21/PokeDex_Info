#!/usr/bin/env python3
"""
Pokemon Moves Scraper
Scrapes comprehensive move data from Serebii.net including move details and Pokemon that learn them.
"""

import sys
import os
import json
import time
import re
from typing import Dict, List, Any, Optional

# Add project paths
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "utils"))

from config import PokeDataUtils, DATA_FILES, BASE_URLS


class MovesDataScraper:
    """Scrapes Pokemon moves data from Serebii"""

    def __init__(self, generation: int = 9):
        self.utils = PokeDataUtils()
        self.moves_data = []
        self.generation = generation

        # Generation-specific configuration
        self.gen_config = self._get_generation_config(generation)
        self.base_url = self.gen_config["url"]

        # Move categories mapping
        self.move_categories = {
            "Physical": "Physical",
            "Special": "Special",
            "Status": "Status",
            "Other": "Status",  # Fallback
        }

    def _get_generation_config(self, generation: int) -> Dict[str, Any]:
        """Get generation-specific configuration with data structure info"""
        configs = {
            1: {
                "url": "https://www.serebii.net/attackdex-rby/",
                "games": ["Red", "Blue", "Yellow"],
                "filename": "moves_data_gen1.json",
                "has_critical_hit_rate": False,
                "has_z_move_data": False,
                "has_max_move_data": False,
                "has_arceus_data": False,
                "has_za_data": False,
                "has_contests": False,
                "has_physical_special_split": False,
            },
            2: {
                "url": "https://www.serebii.net/attackdex-gs/",
                "games": ["Gold", "Silver", "Crystal"],
                "filename": "moves_data_gen2.json",
                "has_critical_hit_rate": False,
                "has_z_move_data": False,
                "has_max_move_data": False,
                "has_arceus_data": False,
                "has_za_data": False,
                "has_contests": False,
                "has_physical_special_split": False,
            },
            3: {
                "url": "https://www.serebii.net/attackdex/",
                "games": ["Ruby", "Sapphire", "Emerald"],
                "filename": "moves_data_gen3.json",
                "has_critical_hit_rate": False,
                "has_z_move_data": False,
                "has_max_move_data": False,
                "has_arceus_data": False,
                "has_za_data": False,
                "has_contests": True,
                "has_physical_special_split": False,
            },
            4: {
                "url": "https://www.serebii.net/attackdex-dp/",
                "games": ["Diamond", "Pearl", "Platinum"],
                "filename": "moves_data_gen4.json",
                "has_critical_hit_rate": True,
                "has_z_move_data": False,
                "has_max_move_data": False,
                "has_arceus_data": False,
                "has_za_data": False,
                "has_contests": True,
                "has_physical_special_split": True,
            },
            5: {
                "url": "https://www.serebii.net/attackdex-bw/",
                "games": ["Black", "White", "Black 2", "White 2"],
                "filename": "moves_data_gen5.json",
                "has_critical_hit_rate": False,
                "has_z_move_data": False,
                "has_max_move_data": False,
                "has_arceus_data": False,
                "has_za_data": False,
                "has_contests": False,
                "has_physical_special_split": True,
            },
            6: {
                "url": "https://www.serebii.net/attackdex-xy/",
                "games": ["X", "Y", "Omega Ruby", "Alpha Sapphire"],
                "filename": "moves_data_gen6.json",
                "has_critical_hit_rate": True,
                "has_z_move_data": False,
                "has_max_move_data": False,
                "has_arceus_data": False,
                "has_za_data": False,
                "has_contests": True,
                "has_physical_special_split": True,
            },
            7: {
                "url": "https://www.serebii.net/attackdex-sm/",
                "games": ["Sun", "Moon", "Ultra Sun", "Ultra Moon"],
                "filename": "moves_data_gen7.json",
                "has_critical_hit_rate": True,
                "has_z_move_data": True,
                "has_max_move_data": False,
                "has_arceus_data": False,
                "has_za_data": False,
                "has_contests": False,
                "has_physical_special_split": True,
            },
            8: {
                "url": "https://www.serebii.net/attackdex-swsh/",
                "games": ["Sword", "Shield", "Legends: Arceus"],
                "filename": "moves_data_gen8.json",
                "has_critical_hit_rate": True,
                "has_z_move_data": False,
                "has_max_move_data": True,
                "has_arceus_data": True,
                "has_za_data": False,
                "has_contests": False,
                "has_physical_special_split": True,
            },
            9: {
                "url": "https://www.serebii.net/attackdex-sv/",
                "games": ["Scarlet", "Violet", "Legends: Z-A"],
                "filename": "moves_data_gen9.json",
                "has_critical_hit_rate": True,
                "has_z_move_data": False,
                "has_max_move_data": False,
                "has_arceus_data": False,
                "has_za_data": True,
                "has_contests": False,
                "has_physical_special_split": True,
            },
        }

        if generation not in configs:
            raise ValueError(
                f"Generation {generation} not supported. Supported generations: {list(configs.keys())}"
            )

        return configs[generation]

    def scrape_moves_list(self) -> List[str]:
        """Get list of all moves from the main attack dex page"""
        print("Fetching moves list from Serebii...")

        try:
            soup = self.utils.safe_request(self.base_url)
            if not soup:
                return []

            move_links = []

            # Find all select dropdowns that contain move options
            select_elements = soup.find_all("select")
            for select in select_elements:
                options = select.find_all("option")
                for option in options:
                    value = option.get("value", "")
                    # Look for options with attackdex URLs for this generation
                    # Extract the generation-specific path from base_url
                    # e.g., "https://www.serebii.net/attackdex-sv/" -> "attackdex-sv"
                    gen_path = self.base_url.split("/")[-2]  # Get "attackdex-sv" part

                    if value and f"/{gen_path}/" in value and value.endswith(".shtml"):
                        # Extract move filename from the full path
                        # e.g., "/attackdex-sv/thunderbolt.shtml" -> "thunderbolt"
                        move_filename = value.split(f"/{gen_path}/")[-1].replace(
                            ".shtml", ""
                        )
                        if move_filename and move_filename not in move_links:
                            move_links.append(move_filename)

            # Filter out any remaining non-move entries
            filtered_moves = []
            skip_patterns = [
                "index",
                "nav",
                "menu",
                "generation",
                "pokemon",
                "games",
                "archive",
                "privacy",
                "discord",
                "home",
            ]

            for move in move_links:
                # Skip if it contains navigation patterns or is too short/long
                if (
                    not any(pattern in move.lower() for pattern in skip_patterns)
                    and 2 <= len(move) <= 50
                    and move.replace("-", "").replace("_", "").isalnum()
                ):
                    filtered_moves.append(move)

            print(f"Found {len(filtered_moves)} moves to scrape")
            return filtered_moves

        except Exception as e:
            print(f"Error fetching moves list: {e}")
            return []

    def scrape_move_data(self, move_filename: str) -> Optional[Dict[str, Any]]:
        """Scrape detailed data for a specific move"""
        move_url = f"{self.base_url}{move_filename}.shtml"

        try:
            soup = self.utils.safe_request(move_url)
            if not soup:
                return None

            # Base move data structure (all generations)
            move_data = {
                "name": "",
                "battle_type": "",
                "category": "",
                "power_points": None,
                "base_power": None,
                "accuracy": None,
                "battle_effect": "",
                "secondary_effect": "",
                "effect_rate": "",
                "speed_priority": 0,
                "pokemon_hit_in_battle": "",
                "physical_contact": False,
                "sound_type": False,
                "punch_move": False,
                "biting_move": False,
                "snatchable": False,
                "slicing_move": False,
                "bullet_type": False,
                "wind_move": False,
                "powder_move": False,
                "metronome": False,
                "affected_by_gravity": False,
                "defrosts_when_used": False,
                "reflected_by_magic_coat": False,
                "blocked_by_protect": False,
                "copyable_by_mirror_move": False,
                "learned_by": [],  # Pokemon that can learn this move
            }

            # Add generation-specific fields
            if self.gen_config["has_critical_hit_rate"]:
                move_data["base_critical_hit_rate"] = ""

            if self.gen_config["has_z_move_data"]:
                move_data["z_move_power"] = ""
                move_data["z_move_effect"] = ""

            if self.gen_config["has_max_move_data"]:
                move_data["max_move_power"] = ""
                move_data["max_move_effect"] = ""

            if self.gen_config["has_arceus_data"]:
                move_data["arceus_data"] = {
                    "power_points": None,
                    "base_power_standard": None,
                    "base_power_agile": None,
                    "base_power_strong": None,
                    "accuracy": None,
                    "battle_effect": "",
                    "effect_rate_standard": "",
                    "effect_rate_strong": "",
                    "speed_priority_standard": 0,
                    "speed_priority_strong": 0,
                }

            if self.gen_config["has_za_data"]:
                move_data["pokemon_legends_za_data"] = {
                    "cooldown": "",
                    "base_power_za": "",
                    "distance": "",
                    "effect_rate_za": "",
                    "effect_duration": "",
                    "frame_data": "",
                    "base_critical_hit_rate_za": "",
                }

            if self.gen_config["has_contests"]:
                move_data["contest"] = {
                    "contest_type": "",
                    "appeal": "",
                    "jam": "",
                    "effect": "",
                }

            # Extract move name from page title
            title = soup.find("title")
            if title:
                title_text = title.get_text()
                if " - " in title_text:
                    # Split on last " - " to get move name (format: "Serebii.net Generation X AttackDex - Move Name")
                    move_data["name"] = title_text.split(" - ")[-1].strip()
                else:
                    # Fallback: use the filename as the move name (convert underscores to spaces, title case)
                    move_data["name"] = move_filename.replace("_", " ").title()
            else:
                # Last resort fallback: use filename
                move_data["name"] = move_filename.replace("_", " ").title()

            # Find the main move details table
            tables = soup.find_all("table", class_="dextable")

            for table in tables:
                rows = table.find_all("tr")

                # Parse structured table data
                for i, row in enumerate(rows):
                    cells = row.find_all(["td", "th"])

                    # Look for header patterns and extract data
                    for j, cell in enumerate(cells):
                        cell_text = cell.get_text().strip()

                        # Battle Type (from image src)
                        if "Battle Type" in cell_text and j + 1 < len(rows):
                            next_row = rows[i + 1]
                            type_cells = next_row.find_all("td")
                            if len(type_cells) > 1:
                                type_img = type_cells[1].find("img")
                                if type_img and type_img.get("src"):
                                    src = type_img.get("src")
                                    # Extract type from path like "/pokedx-bw/type/grass.gif"
                                    if "/type/" in src:
                                        move_data["battle_type"] = (
                                            src.split("/type/")[1]
                                            .replace(".gif", "")
                                            .replace(".png", "")
                                            .title()
                                        )

                        # Category (from image src)
                        elif "Category" in cell_text and i + 1 < len(rows):
                            next_row = rows[i + 1]
                            cat_cells = next_row.find_all("td")
                            # Look through all cells to find the category image
                            for cat_cell in cat_cells:
                                cat_img = cat_cell.find("img")
                                if cat_img and cat_img.get("src"):
                                    src = cat_img.get("src")
                                    # Category image can be from physical/special/status paths
                                    if any(
                                        path in src
                                        for path in [
                                            "/physical/",
                                            "/special/",
                                            "/status/",
                                        ]
                                    ):
                                        category_name = None
                                        if "/physical/" in src:
                                            category_name = "Physical"
                                        elif "/special/" in src:
                                            category_name = "Special"
                                        elif "/status/" in src:
                                            category_name = "Status"
                                        if category_name:
                                            move_data["category"] = category_name
                                            break
                                    # Fallback: try type path
                                    elif "/type/" in src:
                                        move_data["category"] = (
                                            src.split("/type/")[1]
                                            .replace(".gif", "")
                                            .replace(".png", "")
                                            .title()
                                        )
                                        break

                        # Power Points, Base Power, Accuracy (numeric values)
                        elif "Power Points" in cell_text and i + 1 < len(rows):
                            next_row = rows[i + 1]
                            value_cells = next_row.find_all("td")
                            if len(value_cells) >= 3:
                                # Power Points
                                pp_text = value_cells[0].get_text().strip()
                                if pp_text.isdigit():
                                    move_data["power_points"] = int(pp_text)
                                # Base Power
                                power_text = value_cells[1].get_text().strip()
                                if power_text.isdigit():
                                    move_data["base_power"] = int(power_text)
                                # Accuracy
                                acc_text = value_cells[2].get_text().strip()
                                if acc_text.isdigit():
                                    move_data["accuracy"] = int(acc_text)

                        # Battle Effect
                        elif "Battle Effect:" in cell_text:
                            if i + 1 < len(rows):
                                effect_row = rows[i + 1]
                                effect_cell = effect_row.find("td", class_="fooinfo")
                                if effect_cell:
                                    move_data["battle_effect"] = (
                                        effect_cell.get_text().strip()
                                    )

                        # Secondary Effect and Effect Rate
                        elif "Secondary Effect:" in cell_text:
                            if i + 1 < len(rows):
                                effect_row = rows[i + 1]
                                effect_cells = effect_row.find_all("td")
                                if len(effect_cells) >= 2:
                                    # Secondary Effect
                                    sec_effect = (
                                        effect_cells[0].get_text().strip()
                                        if effect_cells[0].get("class")
                                        and "fooinfo" in effect_cells[0].get("class")
                                        else effect_cells[1].get_text().strip()
                                    )
                                    move_data["secondary_effect"] = sec_effect
                                    # Effect Rate
                                    if len(effect_cells) >= 3:
                                        rate_text = effect_cells[-1].get_text().strip()
                                        move_data["effect_rate"] = rate_text

                        # Critical Hit Rate, Speed Priority, Pokemon Hit in Battle
                        elif "Base Critical Hit Rate" in cell_text and i + 1 < len(
                            rows
                        ):
                            next_row = rows[i + 1]
                            crit_cells = next_row.find_all("td")
                            if len(crit_cells) >= 3:
                                # Only store critical hit rate for generations that have it
                                if self.gen_config["has_critical_hit_rate"]:
                                    move_data["base_critical_hit_rate"] = (
                                        crit_cells[0].get_text().strip()
                                    )
                                priority_text = crit_cells[1].get_text().strip()
                                if priority_text.lstrip("-").isdigit():
                                    move_data["speed_priority"] = int(priority_text)
                                move_data["pokemon_hit_in_battle"] = (
                                    crit_cells[2].get_text().strip()
                                )

                        # Move attribute flags (Physical Contact, Sound-Type, etc.)
                        elif "Physical Contact" in cell_text:
                            # Find the corresponding values row
                            if i + 1 < len(rows):
                                values_row = rows[i + 1]
                                attr_cells = values_row.find_all("td")
                                if len(attr_cells) >= 5:
                                    move_data["physical_contact"] = (
                                        attr_cells[0].get_text().strip().lower()
                                        == "yes"
                                    )
                                    move_data["sound_type"] = (
                                        attr_cells[1].get_text().strip().lower()
                                        == "yes"
                                    )
                                    move_data["punch_move"] = (
                                        attr_cells[2].get_text().strip().lower()
                                        == "yes"
                                    )
                                    move_data["biting_move"] = (
                                        attr_cells[3].get_text().strip().lower()
                                        == "yes"
                                    )
                                    move_data["snatchable"] = (
                                        attr_cells[4].get_text().strip().lower()
                                        == "yes"
                                    )

                        # Second row of attributes
                        elif "Slicing Move" in cell_text:
                            if i + 1 < len(rows):
                                values_row = rows[i + 1]
                                attr_cells = values_row.find_all("td")
                                if len(attr_cells) >= 5:
                                    move_data["slicing_move"] = (
                                        attr_cells[0].get_text().strip().lower()
                                        == "yes"
                                    )
                                    move_data["bullet_type"] = (
                                        attr_cells[1].get_text().strip().lower()
                                        == "yes"
                                    )
                                    move_data["wind_move"] = (
                                        attr_cells[2].get_text().strip().lower()
                                        == "yes"
                                    )
                                    move_data["powder_move"] = (
                                        attr_cells[3].get_text().strip().lower()
                                        == "yes"
                                    )
                                    move_data["metronome"] = (
                                        attr_cells[4].get_text().strip().lower()
                                        == "yes"
                                    )

                        # Third row of attributes
                        elif "Affected by Gravity" in cell_text:
                            if i + 1 < len(rows):
                                values_row = rows[i + 1]
                                attr_cells = values_row.find_all("td")
                                if len(attr_cells) >= 5:
                                    move_data["affected_by_gravity"] = (
                                        attr_cells[0].get_text().strip().lower()
                                        == "yes"
                                    )
                                    move_data["defrosts_when_used"] = (
                                        attr_cells[1].get_text().strip().lower()
                                        == "yes"
                                    )
                                    move_data["reflected_by_magic_coat"] = (
                                        attr_cells[2].get_text().strip().lower()
                                        == "yes"
                                    )
                                    move_data["blocked_by_protect"] = (
                                        attr_cells[3].get_text().strip().lower()
                                        == "yes"
                                    )
                                    move_data["copyable_by_mirror_move"] = (
                                        attr_cells[4].get_text().strip().lower()
                                        == "yes"
                                    )

                        # Z-Move data (Gen 7 only)
                        elif self.gen_config["has_z_move_data"] and (
                            "Corresponding Z-Move" in cell_text
                            or "Z-Move Power" in cell_text
                        ):
                            if i + 1 < len(rows):
                                values_row = rows[i + 1]
                                zmove_cells = values_row.find_all("td")
                                if len(zmove_cells) >= 2:
                                    # Corresponding Z-Move name
                                    move_data["z_move_effect"] = (
                                        zmove_cells[0].get_text().strip()
                                    )
                                    # Z-Move Power
                                    if len(zmove_cells) > 1:
                                        power_text = zmove_cells[1].get_text().strip()
                                        if power_text.isdigit():
                                            move_data["z_move_power"] = int(power_text)

                        # Max Move data (Gen 8 only)
                        elif self.gen_config["has_max_move_data"] and (
                            "Corresponding Max Move" in cell_text
                            or "MaxMove Power" in cell_text
                        ):
                            if i + 1 < len(rows):
                                values_row = rows[i + 1]
                                maxmove_cells = values_row.find_all("td")
                                if len(maxmove_cells) >= 2:
                                    # Corresponding Max Move name
                                    move_data["max_move_effect"] = (
                                        maxmove_cells[0].get_text().strip()
                                    )
                                    # Max Move Power
                                    if len(maxmove_cells) > 1:
                                        power_text = maxmove_cells[1].get_text().strip()
                                        if power_text.isdigit():
                                            move_data["max_move_power"] = int(
                                                power_text
                                            )

                        # Pokémon Legends: Z-A Data section (only for supported generations)
                        elif self.gen_config["has_za_data"] and (
                            "Pokémon Legends: Z-A Data" in cell_text
                            or "Pokemon Legends: Z-A Data" in cell_text
                        ):
                            # Look for the Z-A data table that follows
                            za_table_found = False
                            for remaining_row in rows[i:]:
                                za_cells = remaining_row.find_all("td")
                                if len(za_cells) >= 3:
                                    # Check for Cooldown | Base Power | Distance headers
                                    if any(
                                        "Cooldown" in cell.get_text()
                                        for cell in za_cells
                                    ):
                                        # Next row should have the values
                                        next_idx = rows.index(remaining_row) + 1
                                        if next_idx < len(rows):
                                            value_row = rows[next_idx]
                                            value_cells = value_row.find_all("td")
                                            if len(value_cells) >= 3:
                                                move_data["pokemon_legends_za_data"][
                                                    "cooldown"
                                                ] = (value_cells[0].get_text().strip())
                                                move_data["pokemon_legends_za_data"][
                                                    "base_power_za"
                                                ] = (value_cells[1].get_text().strip())
                                                move_data["pokemon_legends_za_data"][
                                                    "distance"
                                                ] = (value_cells[2].get_text().strip())

                                    # Check for Effect Rate | Effect Duration | Frame Data headers
                                    elif any(
                                        "Effect Rate" in cell.get_text()
                                        for cell in za_cells
                                    ):
                                        next_idx = rows.index(remaining_row) + 1
                                        if next_idx < len(rows):
                                            value_row = rows[next_idx]
                                            value_cells = value_row.find_all("td")
                                            if len(value_cells) >= 3:
                                                move_data["pokemon_legends_za_data"][
                                                    "effect_rate_za"
                                                ] = (value_cells[0].get_text().strip())
                                                move_data["pokemon_legends_za_data"][
                                                    "effect_duration"
                                                ] = (value_cells[1].get_text().strip())
                                                frame_text = (
                                                    value_cells[2]
                                                    .get_text()
                                                    .strip()
                                                    .replace("\r", "")
                                                    .replace("\t", " ")
                                                )
                                                move_data["pokemon_legends_za_data"][
                                                    "frame_data"
                                                ] = " ".join(frame_text.split())

                                    # Check for Base Critical Hit Rate (single column in Z-A section)
                                    elif (
                                        any(
                                            "Base Critical Hit Rate" in cell.get_text()
                                            for cell in za_cells
                                        )
                                        and len(za_cells) == 1
                                    ):
                                        next_idx = rows.index(remaining_row) + 1
                                        if next_idx < len(rows):
                                            value_row = rows[next_idx]
                                            value_cells = value_row.find_all("td")
                                            if len(value_cells) >= 1:
                                                move_data["pokemon_legends_za_data"][
                                                    "base_critical_hit_rate_za"
                                                ] = (value_cells[0].get_text().strip())

                        # Legends: Arceus Data section (only for Gen 8)
                        elif self.gen_config["has_arceus_data"] and (
                            "Legends: Arceus Data" in cell_text
                            or "Legends: Arceus" in cell_text
                        ):
                            # Look for Arceus-specific data in following rows
                            for arceus_row in rows[i:]:
                                arceus_cells = arceus_row.find_all("td")
                                if not arceus_cells:
                                    continue

                                # Check for Base Power with Standard/Agile/Strong variants
                                if any(
                                    "Base Power" in cell.get_text()
                                    for cell in arceus_cells
                                ):
                                    if len(arceus_cells) >= 1:
                                        power_text = arceus_cells[0].get_text().strip()
                                        # Parse "Standard: 80 Agile: 60 Strong: 100"
                                        if "Standard:" in power_text:
                                            parts = power_text.split()
                                            for idx, part in enumerate(parts):
                                                if (
                                                    part == "Standard:"
                                                    and idx + 1 < len(parts)
                                                ):
                                                    val = parts[idx + 1]
                                                    if val.isdigit():
                                                        move_data["arceus_data"][
                                                            "base_power_standard"
                                                        ] = int(val)
                                                elif part == "Agile:" and idx + 1 < len(
                                                    parts
                                                ):
                                                    val = parts[idx + 1]
                                                    if val.isdigit():
                                                        move_data["arceus_data"][
                                                            "base_power_agile"
                                                        ] = int(val)
                                                elif (
                                                    part == "Strong:"
                                                    and idx + 1 < len(parts)
                                                ):
                                                    val = parts[idx + 1]
                                                    if val.isdigit():
                                                        move_data["arceus_data"][
                                                            "base_power_strong"
                                                        ] = int(val)

                                # Check for Speed Priority with Standard/Strong variants
                                elif any(
                                    "Speed" in cell.get_text()
                                    and "Priority" in cell.get_text()
                                    for cell in arceus_cells
                                ):
                                    if len(arceus_cells) >= 1:
                                        speed_text = arceus_cells[0].get_text().strip()
                                        if "Standard:" in speed_text:
                                            parts = speed_text.split()
                                            for idx, part in enumerate(parts):
                                                if (
                                                    part == "Standard:"
                                                    and idx + 1 < len(parts)
                                                ):
                                                    val = parts[idx + 1]
                                                    if val.lstrip("-").isdigit():
                                                        move_data["arceus_data"][
                                                            "speed_priority_standard"
                                                        ] = int(val)
                                                elif (
                                                    part == "Strong:"
                                                    and idx + 1 < len(parts)
                                                ):
                                                    val = parts[idx + 1]
                                                    if val.lstrip("-").isdigit():
                                                        move_data["arceus_data"][
                                                            "speed_priority_strong"
                                                        ] = int(val)

            # Extract Pokemon that learn this move
            move_data["learned_by"] = self.extract_pokemon_learners(soup)

            # Set fallback name if not found
            if not move_data["name"]:
                move_data["name"] = move_filename.replace("-", " ").title()

            return move_data

        except Exception as e:
            print(f"Error scraping move {move_filename}: {e}")
            return None

    def extract_pokemon_learners(self, soup) -> List[Dict[str, Any]]:
        """Extract which Pokemon can learn this move and how"""
        learners = []

        try:
            # Find all tables with Pokemon learning data
            # Gen 1-2, 4-9: use "dextable" class
            # Gen 3: uses "dextab" class instead
            tables = soup.find_all(
                "table", class_=lambda x: x and ("dextable" in x or "dextab" in x)
            )

            # Skip first table (it's the move data), process learner tables
            for table_idx, table in enumerate(tables[1:], start=1):
                # Determine learning method from nearby headers
                current_method = "Level Up"  # default

                # Look for method headers before this table
                prev_elements = []
                current_elem = table
                for _ in range(10):  # Look back at previous 10 elements
                    current_elem = current_elem.find_previous_sibling()
                    if current_elem:
                        prev_elements.append(
                            current_elem.get_text().strip()
                            if current_elem.get_text
                            else ""
                        )
                    else:
                        break

                # Check for learning method indicators
                prev_text = " ".join(prev_elements).lower()
                if "move reminder" in prev_text or "move tutor" in prev_text:
                    current_method = "Move Tutor"
                elif "breeding" in prev_text or "egg move" in prev_text:
                    current_method = "Breeding"
                elif "z-a" in prev_text:
                    current_method = "Z-A Level Up"
                elif "machine" in prev_text or "tm" in prev_text:
                    current_method = "TM"
                else:
                    current_method = "Level Up"

                # Parse table rows - skip header rows (first 2 rows)
                rows = table.find_all("tr")

                for row_idx, row in enumerate(rows):
                    # Skip header rows (first 2 rows typically contain headers)
                    if row_idx < 2:
                        continue

                    cells = row.find_all("td")

                    # Need minimum cells for data extraction (at least dex#, pic, name, type)
                    if len(cells) < 4:
                        continue

                    try:
                        # Extract dex number (usually first cell with #0XXX format)
                        dex_cell = cells[0]
                        dex_text = dex_cell.get_text().strip()

                        # Check for dex number format: #001, #0001, etc.
                        if dex_text.startswith("#") and len(dex_text) >= 4:
                            # Extract dex number after #
                            dex_num_str = dex_text[1:].strip()
                            # Check if it's numeric
                            if dex_num_str.isdigit():
                                # Pad to 4 digits
                                dex_number = dex_num_str.zfill(4)

                                # Extract Pokemon name
                                pokemon_name = ""
                                pokemon_form = "Normal"

                                # Look for a cell with a link to Pokemon page
                                for i in range(len(cells)):
                                    name_cell = cells[i]
                                    name_link = name_cell.find("a")
                                    if name_link:
                                        link_text = name_link.get_text().strip()
                                        # Make sure it's a valid Pokemon name
                                        if link_text and not link_text.isdigit():
                                            pokemon_name = link_text
                                            break

                                # If no link found, try to get text directly
                                if not pokemon_name:
                                    for i in range(2, min(5, len(cells))):
                                        text = cells[i].get_text(strip=True)
                                        if (
                                            text
                                            and not text.isdigit()
                                            and not text.startswith("Lv")
                                        ):
                                            pokemon_name = text
                                            break

                                # Check for form variants by looking at images
                                for cell in cells[:5]:
                                    img_tag = cell.find("img")
                                    if img_tag and img_tag.get("src"):
                                        img_src = img_tag.get("src")
                                        # Check for form indicators in image filename
                                        if "-h.png" in img_src or "-h/" in img_src:
                                            pokemon_form = "Hisuian"
                                            break
                                        elif "-a.png" in img_src or "-a/" in img_src:
                                            pokemon_form = "Alolan"
                                            break
                                        elif "-g.png" in img_src or "-g/" in img_src:
                                            pokemon_form = "Galarian"
                                            break
                                        elif "-p.png" in img_src or "-p/" in img_src:
                                            pokemon_form = "Paldean"
                                            break
                                        elif "-mega" in img_src.lower():
                                            pokemon_form = "Mega"
                                            break
                                        elif "-gmax" in img_src.lower():
                                            pokemon_form = "Gigantamax"
                                            break

                                # Extract level - look for "Lv. X" in the last few cells
                                learn_level = None

                                for cell in reversed(cells[-3:]):
                                    level_text = cell.get_text().strip()
                                    if level_text.startswith("Lv. "):
                                        try:
                                            learn_level = int(
                                                level_text.replace("Lv. ", "")
                                            )
                                            break
                                        except ValueError:
                                            pass

                                # Create learner entry
                                learner_data = {
                                    "dex_number": dex_number,
                                    "name": pokemon_name,
                                    "form": pokemon_form,
                                    "method": current_method,
                                }

                                if learn_level is not None:
                                    learner_data["level"] = learn_level

                                # Only add if we have valid dex number and name
                                if dex_number and pokemon_name:
                                    learners.append(learner_data)

                    except (ValueError, IndexError, AttributeError) as e:
                        continue

        except Exception as e:
            print(f"Error extracting Pokemon learners: {e}")

        # Remove duplicates while preserving order (include form in deduplication)
        seen = set()
        unique_learners = []
        for learner in learners:
            key = (
                learner["dex_number"],
                learner["form"],
                learner["method"],
                learner.get("level"),
            )
            if key not in seen:
                seen.add(key)
                unique_learners.append(learner)

        return unique_learners

    def scrape_all_moves(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Scrape all moves data"""
        print("=== Pokemon Moves Scraper ===")
        print("Fetching comprehensive moves data from Serebii.net")
        print()

        # Get list of moves
        move_files = self.scrape_moves_list()
        if not move_files:
            print("No moves found to scrape!")
            return []

        if limit:
            move_files = move_files[:limit]
            print(f"Limiting to first {limit} moves for testing")

        print(f"Scraping {len(move_files)} moves...")
        print()

        moves_data = []

        for i, move_file in enumerate(move_files, 1):
            print(f"[{i:3d}/{len(move_files)}] Scraping {move_file}...")

            move_data = self.scrape_move_data(move_file)
            if move_data:
                # Skip moves that no Pokemon can learn (not usable in this generation)
                learners_count = len(move_data["learned_by"])
                if learners_count == 0:
                    print(
                        f"  ⚠ {move_data['name']} - {move_data['battle_type']} type, no Pokemon can learn it (skipping - not usable in Gen {self.generation})"
                    )
                else:
                    moves_data.append(move_data)
                    print(
                        f"  ✓ {move_data['name']} - {move_data['battle_type']} type, {learners_count} Pokemon can learn it"
                    )
            else:
                print(f"  ✗ Failed to scrape {move_file}")

            # Rate limiting
            time.sleep(0.5)

            # Progress update every 25 moves
            if i % 25 == 0:
                print(f"\n--- Progress: {i}/{len(move_files)} moves completed ---\n")

        total_scraped = len(move_files)
        usable_moves = len(moves_data)
        skipped_moves = total_scraped - usable_moves

        print(
            f"\n✅ Scraping complete! Collected {usable_moves} usable Gen {self.generation} moves"
        )
        if skipped_moves > 0:
            print(
                f"   ⚠ Skipped {skipped_moves} moves (no Pokemon can learn them in Gen {self.generation})"
            )
        return moves_data

    def save_moves_data(self, moves_data: List[Dict[str, Any]]):
        """Save moves data to JSON file with smart merging"""
        # Use generation-specific filename with absolute path to project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_file = os.path.join(project_root, "data", self.gen_config["filename"])

        # Ensure data directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        # Smart merge: If file exists, merge new moves without duplicating
        existing_moves = {}
        if os.path.exists(output_file):
            try:
                existing_data = self.utils.load_json_data(output_file)
                if isinstance(existing_data, dict) and "moves" in existing_data:
                    # Index existing moves by name for quick lookup
                    for move in existing_data["moves"]:
                        existing_moves[move.get("name", "").lower()] = move
                    print(f"Found {len(existing_moves)} existing moves")
            except Exception as e:
                print(f"Warning: Could not read existing file: {e}")

        # Merge new moves, avoiding duplicates
        merged_moves = list(existing_moves.values())
        new_move_count = 0
        updated_move_count = 0

        for move in moves_data:
            move_name = move.get("name", "").lower()
            if move_name in existing_moves:
                # Update existing move
                idx = next(
                    i
                    for i, m in enumerate(merged_moves)
                    if m.get("name", "").lower() == move_name
                )
                merged_moves[idx] = move
                updated_move_count += 1
            else:
                # Add new move
                merged_moves.append(move)
                new_move_count += 1

        # Create backup before saving if file exists
        if os.path.exists(output_file):
            backup_file = output_file.replace(".json", "_backup.json")
            try:
                os.rename(output_file, backup_file)
                print(f"Created backup: {backup_file}")
            except Exception as e:
                print(f"Warning: Could not create backup: {e}")

        # Create structured data with metadata
        structured_data = {
            "metadata": {
                "generation": self.generation,
                "games": self.gen_config["games"],
                "source": f"Serebii.net AttackDex-Gen{self.generation}",
                "scraped_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_moves": len(merged_moves),
                "merge_info": {
                    "new_moves": new_move_count,
                    "updated_moves": updated_move_count,
                    "total_after_merge": len(merged_moves),
                },
            },
            "moves": merged_moves,
        }

        # Save merged data
        self.utils.save_json_data(structured_data, output_file)
        print(f"\n✅ Saved {len(merged_moves)} moves to {output_file}")
        if new_move_count > 0 or updated_move_count > 0:
            print(f"   - {new_move_count} new moves added")
            if updated_move_count > 0:
                print(f"   - {updated_move_count} existing moves updated")

        # Print summary stats
        types_count = {}
        categories_count = {}
        total_learners = 0

        for move in merged_moves:
            # Count by type
            move_type = move.get("battle_type", "Unknown")
            types_count[move_type] = types_count.get(move_type, 0) + 1

            # Count by category
            category = move.get("category", "Unknown")
            categories_count[category] = categories_count.get(category, 0) + 1

            # Count total Pokemon-move relationships
            total_learners += len(move.get("learned_by", []))

        print(f"\n📊 Moves Data Summary:")
        print(f"   Total Moves: {len(merged_moves)}")
        print(f"   Total Pokémon-Move Relationships: {total_learners}")
        print(f"   Move Types: {len(types_count)}")
        print(f"   Move Categories: {len(categories_count)}")


def main():
    """Main execution function"""
    print("=== Pokémon Moves Data Scraper ===")
    print("Available generations:")
    print("1 - Generation 1 (Red/Blue/Yellow)")
    print("2 - Generation 2 (Gold/Silver/Crystal)")
    print("3 - Generation 3 (Ruby/Sapphire/Emerald)")
    print("4 - Generation 4 (Diamond/Pearl/Platinum)")
    print("5 - Generation 5 (Black/White/Black 2/White 2)")
    print("6 - Generation 6 (X/Y/Omega Ruby/Alpha Sapphire)")
    print("7 - Generation 7 (Sun/Moon/Ultra Sun/Ultra Moon)")
    print("8 - Generation 8 (Sword/Shield/Legends: Arceus)")
    print("9 - Generation 9 (Scarlet/Violet/Legends: Z-A)")

    while True:
        try:
            generation = int(
                input("\nWhich generation would you like to scrape? (1-9): ")
            )
            if 1 <= generation <= 9:
                break
            else:
                print("Please enter a number between 1 and 9.")
        except ValueError:
            print("Please enter a valid number.")

    scraper = MovesDataScraper(generation)

    # Ask user for scraping options
    print(f"\nPokemon Moves Scraper - Generation {generation}")
    print("1. Scrape all moves (full dataset)")
    print("2. Scrape first 50 moves (testing)")
    print("3. Scrape first 10 moves (quick test)")

    choice = input("Choose option (1-3): ").strip()

    limit = None
    if choice == "2":
        limit = 50
    elif choice == "3":
        limit = 10
    elif choice != "1":
        print("Invalid choice, defaulting to full scrape")

    # Scrape moves data
    moves_data = scraper.scrape_all_moves(limit=limit)

    if moves_data:
        # Save data
        scraper.save_moves_data(moves_data)
        print(f"\n🎉 Generation {generation} moves scraping completed successfully!")
        print(f"Data saved to: data/{scraper.gen_config['filename']}")
    else:
        print("❌ No moves data collected")


if __name__ == "__main__":
    main()
