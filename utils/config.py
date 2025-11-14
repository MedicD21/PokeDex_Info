#!/usr/bin/env python3
"""
Pokemon Data Collection System - Configuration and Utilities
Central configuration and shared utilities for all scrapers
"""

import json
import time
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional

# Configuration
BASE_URLS = {
    "serebii_pokemon": "https://www.serebii.net/pokemon/",
    "serebii_pokedex": "https://www.serebii.net/pokedex-sv/",
    "serebii_abilities": "https://www.serebii.net/abilitydex/",
    "serebii_moves": "https://www.serebii.net/attackdex-sv/",
}

# Data file paths
DATA_FILES = {
    "pokemon": "data/pokemon_data.json",
    "abilities": "data/abilities_data.json",
    "moves": "data/moves_data_gen9.json",
    "items": "data/items_data.json",
    "games": "data/pokemon_games.json",
}

# Request settings
REQUEST_DELAY = 0.5  # Seconds between requests
REQUEST_TIMEOUT = 10  # Timeout for requests


class PokeDataUtils:
    """Utility class for Pokemon data operations"""

    @staticmethod
    def load_json_data(file_path: str) -> List[Dict] | Dict:
        """Load JSON data from file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError as e:
            print(f"Error loading {file_path}: {e}")
            return []

    @staticmethod
    def save_json_data(data: List[Dict] | Dict, file_path: str):
        """Save data to JSON file"""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving {file_path}: {e}")

    @staticmethod
    def format_pokemon_name_for_url(name: str) -> str:
        """Format Pokemon name for URL usage"""
        return (
            name.lower()
            .replace(" ", "")
            .replace(".", "")
            .replace("'", "")
            .replace("-", "")
        )

    @staticmethod
    def safe_request(url: str, delay: float = REQUEST_DELAY) -> Optional[BeautifulSoup]:
        """Make a safe HTTP request with error handling"""
        try:
            time.sleep(delay)
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return BeautifulSoup(response.content, "html.parser")
        except requests.RequestException as e:
            print(f"Request failed for {url}: {e}")
            return None

    @staticmethod
    def extract_number_from_text(text: str) -> Optional[int]:
        """Extract number from text, handling various formats"""
        import re

        # Remove common prefixes and extract digits
        cleaned = re.sub(r"[^\d]", "", text)
        if cleaned:
            try:
                return int(cleaned.lstrip("0")) if cleaned != "0" else 0
            except ValueError:
                return None
        return None

    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text"""
        return text.strip().replace("\n", " ").replace("\r", "").replace("\t", " ")

    @staticmethod
    def parse_height_weight(text: str) -> Dict[str, Any]:
        """Parse height/weight text like '2\'04"0.7m' or '15.2lbs6.9kg'"""
        import re

        result = {}

        # Height parsing
        height_match = re.search(r"(\d+)'(\d+)\"", text)
        if height_match:
            feet, inches = height_match.groups()
            result["height_imperial"] = f"{feet}'{inches}\""
            result["height_feet"] = int(feet)
            result["height_inches"] = int(inches)

        meter_match = re.search(r"(\d+\.?\d*)m", text)
        if meter_match:
            result["height_metric"] = f"{meter_match.group(1)}m"
            result["height_meters"] = float(meter_match.group(1))

        # Weight parsing
        lbs_match = re.search(r"(\d+\.?\d*)lbs", text)
        if lbs_match:
            result["weight_imperial"] = f"{lbs_match.group(1)}lbs"
            result["weight_pounds"] = float(lbs_match.group(1))

        kg_match = re.search(r"(\d+\.?\d*)kg", text)
        if kg_match:
            result["weight_metric"] = f"{kg_match.group(1)}kg"
            result["weight_kilograms"] = float(kg_match.group(1))

        return result


# Load game data for reference
def load_pokemon_games() -> List[Dict]:
    """Load Pokemon games data"""
    data = PokeDataUtils.load_json_data(DATA_FILES["games"])
    return data if isinstance(data, list) else []


def get_all_game_names() -> List[str]:
    """Get list of all Pokemon game names"""
    games_data = load_pokemon_games()
    all_games = []
    for gen_data in games_data:
        all_games.extend(gen_data.get("games", []))
    return all_games


def get_pokemon_names() -> List[str]:
    """Get list of all Pokemon names from existing data"""
    pokemon_data = PokeDataUtils.load_json_data(DATA_FILES["pokemon"])
    return [p.get("name", "") for p in pokemon_data if p.get("name")]


# Mapping dictionaries for parsing
REGION_TO_GAMES = {
    "Kanto (RBY)": ["Red", "Blue", "Yellow"],
    "Kanto (FRLG)": ["FireRed", "LeafGreen"],
    "Kanto (Let's Go)": ["Let's Go Pikachu", "Let's Go Eevee"],
    "Johto (GSC)": ["Gold", "Silver", "Crystal"],
    "Johto (HGSS)": ["HeartGold", "SoulSilver"],
    "Hoenn (RSE)": ["Ruby", "Sapphire", "Emerald"],
    "Hoenn (ORAS)": ["Omega Ruby", "Alpha Sapphire"],
    "Sinnoh (DPPt)": ["Diamond", "Pearl", "Platinum"],
    "Sinnoh (BDSP)": ["Brilliant Diamond", "Shining Pearl"],
    "Unova (BW)": ["Black", "White"],
    "Unova (B2W2)": ["Black 2", "White 2"],
    "Central Kalos": ["X", "Y"],
    "Coastal Kalos": ["X", "Y"],
    "Mountain Kalos": ["X", "Y"],
    "Alola (SM)": ["Sun", "Moon"],
    "Alola (USUM)": ["Ultra Sun", "Ultra Moon"],
    "Galar": ["Sword", "Shield"],
    "Isle of Armor": ["Sword", "Shield"],
    "Crown Tundra": ["Sword", "Shield"],
    "Paldea": ["Scarlet", "Violet"],
    "Kitakami": ["Scarlet", "Violet"],
    "Blueberry": ["Scarlet", "Violet"],
    "Hisui": ["Legends Arceus"],
    "Lumiose": ["Legends Z-A"],
}

if __name__ == "__main__":
    print("Pokemon Data Collection System - Configuration Module")
    print(f"Data files: {list(DATA_FILES.keys())}")
    print(f"Base URLs: {list(BASE_URLS.keys())}")

    # Test utilities
    utils = PokeDataUtils()
    print(f"Pokemon names available: {len(get_pokemon_names())}")
    print(f"Game names available: {len(get_all_game_names())}")
