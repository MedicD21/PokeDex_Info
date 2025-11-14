#!/usr/bin/env python3
"""
Comprehensive Pokemon Data Scraper
Collects all available Pokemon information from Serebii.net including:
- Basic info (name, number, type, abilities)
- Physical stats (height, weight, species)
- Base stats (HP, Attack, Defense, etc.)
- Game appearances and regional dex numbers
- Locations, evolution data, moves, and more

This is the master scraper that calls specialized sub-scrapers.
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import json
import time
import re
from typing import Dict, List, Any, Optional
from utils.config import PokeDataUtils, BASE_URLS, DATA_FILES, REGION_TO_GAMES


class ComprehensivePokemonScraper:
    """Main scraper class for comprehensive Pokemon data collection"""

    def __init__(self):
        self.utils = PokeDataUtils()
        self.pokemon_data = self.utils.load_json_data(DATA_FILES["pokemon"])
        self.updated_count = 0

    def scrape_pokemon_details(self, pokemon_name: str, pokemon_entry: Dict) -> Dict:
        """Scrape comprehensive details for a single Pokemon"""
        print(f"  Scraping comprehensive data for {pokemon_name}...")

        # Format URL
        formatted_name = self.utils.format_pokemon_name_for_url(pokemon_name)
        url = f"{BASE_URLS['serebii_pokemon']}{formatted_name}/"

        soup = self.utils.safe_request(url)
        if not soup:
            return pokemon_entry

        # Initialize new data fields if they don't exist
        if "physical_info" not in pokemon_entry:
            pokemon_entry["physical_info"] = {}
        if "game_appearances" not in pokemon_entry:
            pokemon_entry["game_appearances"] = {}
        if "evolution_info" not in pokemon_entry:
            pokemon_entry["evolution_info"] = {}

        # Extract all fooinfo cells (contains most data)
        fooinfo_cells = soup.find_all("td", class_="fooinfo")

        for cell in fooinfo_cells:
            text = cell.get_text(strip=True)

            # Parse regional dex numbers
            if "#" in text and any(region in text for region in REGION_TO_GAMES.keys()):
                self._parse_regional_dex_info(text, pokemon_entry)

            # Parse physical information
            elif any(
                keyword in text.lower()
                for keyword in ["pokemon", "seed", "flame", "water", "electric"]
            ):
                # This might be the species/category
                if "Pokémon" in text:
                    pokemon_entry["physical_info"]["species"] = self.utils.clean_text(
                        text
                    )

            # Parse height and weight
            elif re.search(r"\d+'\d+\"|\d+\.?\d*m", text) and re.search(
                r"\d+\.?\d*lbs|\d+\.?\d*kg", text
            ):
                height_weight_info = self.utils.parse_height_weight(text)
                if height_weight_info:
                    pokemon_entry["physical_info"].update(height_weight_info)

        # Look for additional tables with structured data
        tables = soup.find_all("table")
        for table in tables:
            self._parse_table_data(table, pokemon_entry)

        # Look for evolution information
        self._parse_evolution_info(soup, pokemon_entry)

        # Look for location information
        self._parse_location_info(soup, pokemon_entry)

        return pokemon_entry

    def _parse_regional_dex_info(self, text: str, pokemon_entry: Dict):
        """Parse regional dex information from concatenated text"""
        # Use regex to find all patterns like "Region (details):#number"
        pattern = r"([^#:]+?):#(\d+)"
        matches = re.findall(pattern, text)

        for region_info, dex_number in matches:
            region_info = region_info.strip()

            if "National" in region_info:
                continue  # Skip national dex

            try:
                dex_num = int(dex_number.lstrip("0")) if dex_number != "0" else 0
            except ValueError:
                continue

            # Map region to games
            games_to_update = []
            for region_key, games in REGION_TO_GAMES.items():
                if region_key.lower() in region_info.lower() or any(
                    part in region_info for part in region_key.split()
                ):
                    games_to_update = games
                    break

            # Update game appearances with simplified region names
            simplified_region = self._simplify_region_name(region_info)
            for game in games_to_update:
                pokemon_entry["game_appearances"][game] = {
                    "dex_number": dex_num,
                    "available": True,
                    "region": simplified_region,
                }

    def _parse_table_data(self, table, pokemon_entry: Dict):
        """Parse structured data from HTML tables"""
        rows = table.find_all("tr")

        for row in rows:
            cells = row.find_all(["td", "th"])
            if len(cells) >= 2:
                header = self.utils.clean_text(cells[0].get_text())
                value = self.utils.clean_text(cells[1].get_text())

                # Parse various data types
                if "ability" in header.lower():
                    if "abilities_detailed" not in pokemon_entry:
                        pokemon_entry["abilities_detailed"] = {}
                    pokemon_entry["abilities_detailed"][header] = value

                elif "egg group" in header.lower():
                    if "breeding_info" not in pokemon_entry:
                        pokemon_entry["breeding_info"] = {}
                    pokemon_entry["breeding_info"]["egg_groups"] = value.split(", ")

                elif "gender ratio" in header.lower():
                    if "breeding_info" not in pokemon_entry:
                        pokemon_entry["breeding_info"] = {}
                    pokemon_entry["breeding_info"]["gender_ratio"] = value

                elif "catch rate" in header.lower():
                    pokemon_entry["catch_rate"] = self.utils.extract_number_from_text(
                        value
                    )

                elif "base happiness" in header.lower():
                    pokemon_entry["base_happiness"] = (
                        self.utils.extract_number_from_text(value)
                    )

                elif "growth rate" in header.lower():
                    pokemon_entry["growth_rate"] = value

    def _parse_evolution_info(self, soup, pokemon_entry: Dict):
        """Parse evolution information"""
        # Look for evolution-related content
        evolution_sections = soup.find_all(
            text=re.compile(r"evolve|evolution", re.IGNORECASE)
        )

        if evolution_sections:
            # This is a simplified parser - could be expanded
            pokemon_entry["evolution_info"]["has_evolution_data"] = True
            pokemon_entry["evolution_info"]["evolution_text"] = []

            for section in evolution_sections[:3]:  # Limit to first 3 matches
                parent = section.parent
                if parent:
                    text = self.utils.clean_text(parent.get_text())
                    if len(text) > 10 and len(text) < 200:  # Reasonable length
                        pokemon_entry["evolution_info"]["evolution_text"].append(text)

    def _parse_location_info(self, soup, pokemon_entry: Dict):
        """Parse location/encounter information"""
        # Look for location tables or text
        location_keywords = ["location", "route", "area", "wild", "encounter"]

        # Initialize locations
        if "locations" not in pokemon_entry:
            pokemon_entry["locations"] = {}

        # This is a placeholder - full implementation would parse specific location tables
        location_tables = soup.find_all(
            "table", class_=re.compile(r"location|encounter", re.IGNORECASE)
        )

        if location_tables:
            pokemon_entry["locations"]["has_location_data"] = True
            pokemon_entry["locations"]["location_count"] = len(location_tables)

    def _simplify_region_name(self, region_info: str) -> str:
        """Simplify region names to be cleaner and more consistent"""
        region_lower = region_info.lower()

        if "kanto" in region_lower:
            return "Kanto"
        elif "johto" in region_lower:
            return "Johto"
        elif "hoenn" in region_lower:
            return "Hoenn"
        elif "sinnoh" in region_lower:
            return "Sinnoh"
        elif "unova" in region_lower:
            return "Unova"
        elif "kalos" in region_lower:
            return "Kalos"
        elif "alola" in region_lower:
            return "Alola"
        elif "galar" in region_lower:
            return "Galar"
        elif "paldea" in region_lower:
            return "Paldea"
        elif "hisui" in region_lower:
            return "Hisui"
        elif "lumiose" in region_lower:
            return "Lumiose"
        elif "isle of armor" in region_lower:
            return "Isle of Armor"
        elif "crown tundra" in region_lower:
            return "Crown Tundra"
        elif "blueberry" in region_lower:
            return "Blueberry Academy"
        elif "kitakami" in region_lower:
            return "Kitakami"
        else:
            # Return original if no match found
            return region_info

    def scrape_all_pokemon(self, limit: Optional[int] = None, start_index: int = 0):
        """Scrape comprehensive data for all Pokemon"""
        print("Starting comprehensive Pokemon data scraping...")

        if not self.pokemon_data:
            print("No Pokemon data found. Please run the basic scraper first.")
            return

        total_pokemon = len(self.pokemon_data)
        if limit:
            end_index = min(start_index + limit, total_pokemon)
            pokemon_to_process = self.pokemon_data[start_index:end_index]
        else:
            pokemon_to_process = self.pokemon_data[start_index:]

        print(
            f"Processing {len(pokemon_to_process)} Pokemon (starting from index {start_index})..."
        )

        for i, pokemon in enumerate(pokemon_to_process, start_index + 1):
            pokemon_name = pokemon.get("name", "Unknown")

            try:
                print(f"[{i}/{total_pokemon}] Processing {pokemon_name}...")

                # Scrape comprehensive data
                updated_pokemon = self.scrape_pokemon_details(pokemon_name, pokemon)

                # Update the pokemon in our main data
                pokemon_index = next(
                    (
                        idx
                        for idx, p in enumerate(self.pokemon_data)
                        if p.get("name") == pokemon_name
                    ),
                    None,
                )
                if pokemon_index is not None:
                    self.pokemon_data[pokemon_index] = updated_pokemon
                    self.updated_count += 1

                # Save progress periodically
                if i % 50 == 0:
                    self._save_progress()
                    print(
                        f"  Progress saved. Updated {self.updated_count} Pokemon so far."
                    )

                # Respectful delay
                time.sleep(0.5)

            except Exception as e:
                print(f"  Error processing {pokemon_name}: {e}")
                continue

        # Final save
        self._save_progress()
        print(
            f"Comprehensive scraping completed! Updated {self.updated_count} Pokemon."
        )

    def _save_progress(self):
        """Save current progress to file"""
        self.utils.save_json_data(self.pokemon_data, DATA_FILES["pokemon"])

    def get_stats_summary(self) -> Dict[str, Any]:
        """Get summary statistics of collected data"""
        if not self.pokemon_data:
            return {}

        total = len(self.pokemon_data)
        with_physical_info = sum(1 for p in self.pokemon_data if "physical_info" in p)
        with_game_appearances = sum(
            1
            for p in self.pokemon_data
            if "game_appearances" in p and p["game_appearances"]
        )
        with_evolution_info = sum(1 for p in self.pokemon_data if "evolution_info" in p)
        with_locations = sum(1 for p in self.pokemon_data if "locations" in p)

        return {
            "total_pokemon": total,
            "with_physical_info": with_physical_info,
            "with_game_appearances": with_game_appearances,
            "with_evolution_info": with_evolution_info,
            "with_locations": with_locations,
            "completion_rates": {
                "physical_info": (
                    f"{(with_physical_info/total*100):.1f}%" if total > 0 else "0%"
                ),
                "game_appearances": (
                    f"{(with_game_appearances/total*100):.1f}%" if total > 0 else "0%"
                ),
                "evolution_info": (
                    f"{(with_evolution_info/total*100):.1f}%" if total > 0 else "0%"
                ),
                "locations": (
                    f"{(with_locations/total*100):.1f}%" if total > 0 else "0%"
                ),
            },
        }


def main():
    """Main function with interactive menu"""
    scraper = ComprehensivePokemonScraper()

    print("=== Comprehensive Pokemon Data Scraper ===")
    print("This scraper collects detailed information including:")
    print("- Physical info (height, weight, species)")
    print("- Regional Pokedex numbers")
    print("- Game appearances")
    print("- Evolution information")
    print("- Location data")
    print("- And more!")
    print()

    # Show current stats
    stats = scraper.get_stats_summary()
    if stats:
        print("Current data status:")
        for key, value in stats["completion_rates"].items():
            print(f"  {key.replace('_', ' ').title()}: {value}")
        print()

    # Interactive menu
    while True:
        print("Options:")
        print("1. Test on single Pokemon (Bulbasaur) - [PREVIEW ONLY - NO SAVE]")
        print("2. Scrape limited batch (specify number) - [SAVES TO FILE]")
        print("3. Scrape all Pokemon (full run) - [SAVES TO FILE]")
        print("4. Continue from specific index - [SAVES TO FILE]")
        print("5. Show current statistics - [READ ONLY]")
        print("6. Exit")

        choice = input("Choose an option (1-6): ").strip()

        if choice == "1":
            # Test on Bulbasaur
            test_pokemon = next(
                (p for p in scraper.pokemon_data if p.get("name") == "Bulbasaur"), None
            )
            if test_pokemon:
                updated = scraper.scrape_pokemon_details(
                    "Bulbasaur", test_pokemon.copy()
                )
                print("Test results for Bulbasaur:")
                print(json.dumps(updated, indent=2))
            else:
                print("Bulbasaur not found in data.")

        elif choice == "2":
            limit = input("How many Pokemon to scrape? ").strip()
            try:
                limit = int(limit)
                scraper.scrape_all_pokemon(limit=limit)
            except ValueError:
                print("Invalid number.")

        elif choice == "3":
            confirm = (
                input("This will scrape ALL Pokemon. Continue? (y/n): ").strip().lower()
            )
            if confirm == "y":
                scraper.scrape_all_pokemon()

        elif choice == "4":
            start_idx = input("Start from which index? ").strip()
            limit = input("How many to process (or 'all')? ").strip()
            try:
                start_idx = int(start_idx)
                if limit.lower() == "all":
                    scraper.scrape_all_pokemon(start_index=start_idx)
                else:
                    limit = int(limit)
                    scraper.scrape_all_pokemon(limit=limit, start_index=start_idx)
            except ValueError:
                print("Invalid input.")

        elif choice == "5":
            stats = scraper.get_stats_summary()
            print("Current Statistics:")
            print(json.dumps(stats, indent=2))

        elif choice == "6":
            break

        else:
            print("Invalid choice.")

        print()


if __name__ == "__main__":
    main()
