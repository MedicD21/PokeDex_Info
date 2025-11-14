#!/usr/bin/env python3
"""
Game Dex Scraper - Final Version
Scrapes game-specific Pokedex numbers from Serebii.net individual Pokemon pages
Handles the concatenated format where all dex info is in one cell
"""

import json
import requests
import time
import re
from bs4 import BeautifulSoup
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "utils"))
from grab_info import pk_names, get_all_games


def parse_dex_info(text):
    """Parse concatenated dex info like 'National:#0001Kanto (RBY):#001Kanto (Let's Go):#001'"""
    entries = []

    # Use regex to find all patterns like "Region (details):#number" or "Region:#number"
    # This handles the concatenated format
    pattern = r"([^#:]+?):#(\d+)"
    matches = re.findall(pattern, text)

    for region_info, dex_number in matches:
        region_info = region_info.strip()
        try:
            dex_num = int(dex_number.lstrip("0")) if dex_number != "0" else 0
            entries.append((region_info, dex_num))
        except ValueError:
            continue

    return entries


def map_region_to_games(region_info, dex_num):
    """Map region information to specific game names"""
    games_updated = []

    if "National" in region_info:
        # Skip national dex (already in our data)
        return []
    elif "Kanto" in region_info:
        if "RBY" in region_info:
            games_updated = ["Red", "Blue", "Yellow"]
        elif "FRLG" in region_info:
            games_updated = ["FireRed", "LeafGreen"]
        elif "Let's Go" in region_info or "LGPE" in region_info:
            games_updated = ["Let's Go Pikachu", "Let's Go Eevee"]
    elif "Johto" in region_info:
        if "GSC" in region_info:
            games_updated = ["Gold", "Silver", "Crystal"]
        elif "HGSS" in region_info:
            games_updated = ["HeartGold", "SoulSilver"]
    elif "Hoenn" in region_info:
        if "RSE" in region_info:
            games_updated = ["Ruby", "Sapphire", "Emerald"]
        elif "ORAS" in region_info:
            games_updated = ["Omega Ruby", "Alpha Sapphire"]
    elif "Sinnoh" in region_info:
        if "DPPt" in region_info or "DP" in region_info:
            games_updated = ["Diamond", "Pearl", "Platinum"]
        elif "BDSP" in region_info:
            games_updated = ["Brilliant Diamond", "Shining Pearl"]
    elif "Unova" in region_info:
        if "BW" in region_info and "B2W2" not in region_info:
            games_updated = ["Black", "White"]
        elif "B2W2" in region_info:
            games_updated = ["Black 2", "White 2"]
    elif "Central Kalos" in region_info or (
        "Kalos" in region_info and "Central" in region_info
    ):
        games_updated = ["X", "Y"]
    elif "Coastal Kalos" in region_info:
        games_updated = ["X", "Y"]  # Same games, different dex section
    elif "Mountain Kalos" in region_info:
        games_updated = ["X", "Y"]  # Same games, different dex section
    elif "Alola" in region_info:
        if "SM" in region_info and "USUM" not in region_info:
            games_updated = ["Sun", "Moon"]
        elif "USUM" in region_info:
            games_updated = ["Ultra Sun", "Ultra Moon"]
    elif "Galar" in region_info:
        games_updated = ["Sword", "Shield"]
    elif "Isle of Armor" in region_info:
        # DLC area for Sword/Shield
        games_updated = ["Sword", "Shield"]
    elif "Crown Tundra" in region_info:
        # DLC area for Sword/Shield
        games_updated = ["Sword", "Shield"]
    elif "Paldea" in region_info:
        games_updated = ["Scarlet", "Violet"]
    elif "Blueberry" in region_info:
        # DLC area for Scarlet/Violet
        games_updated = ["Scarlet", "Violet"]
    elif "Lumiose" in region_info:
        games_updated = ["Legends Z-A"]
    elif "Hisui" in region_info:
        games_updated = ["Legends Arceus"]

    return games_updated


def scrape_game_dex_data(limit=None):
    """Scrape game dex data for all Pokemon from their individual pages."""
    print("Starting game dex data scraping...")

    # Get list of all Pokemon names
    pokemon_names = pk_names()

    if limit:
        pokemon_names = pokemon_names[:limit]
        print(f"Limited to first {limit} Pokemon for testing")

    # Load existing Pokemon data
    with open("pokemon_data.json", "r") as f:
        pokemon_data = json.load(f)

    print(f"Processing {len(pokemon_names)} Pokemon...")

    for i, pokemon_name in enumerate(pokemon_names, 1):
        # Find the corresponding Pokemon in our data
        pokemon = None
        for p in pokemon_data:
            if p["name"] == pokemon_name:
                pokemon = p
                break

        if not pokemon:
            print(f"  Pokemon {pokemon_name} not found in data")
            continue

        # Initialize game_appearances if not exists
        if "game_appearances" not in pokemon:
            pokemon["game_appearances"] = {}

        try:
            print(f"  [{i}/{len(pokemon_names)}] Processing {pokemon_name}...")

            # Format URL for individual Pokemon page
            formatted_name = (
                pokemon_name.lower().replace(" ", "").replace(".", "").replace("'", "")
            )
            url = f"https://www.serebii.net/pokemon/{formatted_name}/"

            response = requests.get(url)
            if response.status_code != 200:
                print(
                    f"    Failed to fetch page for {pokemon_name} (status: {response.status_code})"
                )
                continue

            soup = BeautifulSoup(response.content, "html.parser")

            # Look for dex number information in td class="fooinfo"
            fooinfo_cells = soup.find_all("td", class_="fooinfo")

            found_entries = 0
            for cell in fooinfo_cells:
                text = cell.get_text(strip=True)

                # Check if this cell contains dex information
                if "#" in text and any(
                    region in text
                    for region in [
                        "National",
                        "Kanto",
                        "Johto",
                        "Hoenn",
                        "Sinnoh",
                        "Unova",
                        "Kalos",
                        "Alola",
                        "Galar",
                        "Paldea",
                        "Hisui",
                        "Central",
                        "Isle of Armor",
                        "Blueberry",
                        "Lumiose",
                        "Crown Tundra",
                    ]
                ):
                    # Parse all dex entries from this cell
                    dex_entries = parse_dex_info(text)

                    for region_info, dex_num in dex_entries:
                        games_to_update = map_region_to_games(region_info, dex_num)

                        for game in games_to_update:
                            pokemon["game_appearances"][game] = {
                                "dex_number": dex_num,
                                "available": True,
                            }

                        if games_to_update:
                            found_entries += 1
                            print(
                                f"    Found {region_info} #{dex_num} -> {', '.join(games_to_update)}"
                            )

            if found_entries == 0:
                print(f"    No dex entries found for {pokemon_name}")

            # Small delay to be respectful to the server
            time.sleep(0.5)

        except Exception as e:
            print(f"  Error processing {pokemon_name}: {e}")
            continue

    # Save updated data
    print("Saving updated Pokemon data...")
    with open("../data/pokemon_data.json", "w") as f:
        json.dump(pokemon_data, f, indent=2)

    print("Game dex data scraping completed!")


def test_single_pokemon(pokemon_name):
    """Test the scraper on a single Pokemon to verify it's working."""
    print(f"Testing scraper on {pokemon_name}...")

    # Format URL for individual Pokemon page
    formatted_name = (
        pokemon_name.lower().replace(" ", "").replace(".", "").replace("'", "")
    )
    url = f"https://www.serebii.net/pokemon/{formatted_name}/"

    print(f"URL: {url}")

    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch page (status: {response.status_code})")
        return

    soup = BeautifulSoup(response.content, "html.parser")

    # Look for dex number information in td class="fooinfo"
    fooinfo_cells = soup.find_all("td", class_="fooinfo")

    print(f"Found {len(fooinfo_cells)} fooinfo cells:")

    for i, cell in enumerate(fooinfo_cells):
        text = cell.get_text(strip=True)
        print(
            f"  Cell {i+1}: {text[:100]}..."
            if len(text) > 100
            else f"  Cell {i+1}: {text}"
        )

        # Test our parsing logic
        if "#" in text and any(
            region in text
            for region in [
                "National",
                "Kanto",
                "Johto",
                "Hoenn",
                "Sinnoh",
                "Unova",
                "Kalos",
                "Alola",
                "Galar",
                "Paldea",
                "Hisui",
                "Central",
                "Isle of Armor",
                "Blueberry",
                "Lumiose",
                "Crown Tundra",
            ]
        ):
            dex_entries = parse_dex_info(text)
            print(f"    Found {len(dex_entries)} dex entries:")

            for region_info, dex_num in dex_entries:
                games_mapped = map_region_to_games(region_info, dex_num)
                if games_mapped:
                    print(
                        f"      {region_info} #{dex_num} -> {', '.join(games_mapped)}"
                    )
                else:
                    print(f"      {region_info} #{dex_num} -> (no games mapped)")


if __name__ == "__main__":
    # Test on a single Pokemon first
    print("Testing on Bulbasaur...")
    test_single_pokemon("Bulbasaur")

    print("\n" + "=" * 50 + "\n")

    # Ask user if they want to proceed with full scraping
    response = (
        input("Run full scraping? (y/n, or enter number for limited test): ")
        .strip()
        .lower()
    )

    if response == "y" or response == "yes":
        scrape_game_dex_data()
    elif response.isdigit():
        limit = int(response)
        scrape_game_dex_data(limit=limit)
    else:
        print("Scraping cancelled.")
