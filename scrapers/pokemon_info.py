from bs4 import BeautifulSoup
import requests
import json
from typing import List, Dict
import os

url_base = "https://www.serebii.net/pokemon"


def fetch_pokemon():
    pokemon_list = []
    response = requests.get(f"{url_base}/nationalpokedex.shtml")
    soup = BeautifulSoup(response.content, "html.parser")

    # Find all dextable tables (there might be multiple)
    tables = soup.find_all("table", {"class": "dextable"})

    if not tables:
        print("Could not find any Pokemon tables")
        return pokemon_list

    print(f"Found {len(tables)} tables")

    for table_idx, table in enumerate(tables):
        print(f"Processing table {table_idx + 1}")
        rows = table.find_all("tr")
        print(f"Found {len(rows)} rows in table {table_idx + 1}")

        # Skip header rows - look for rows with Pokemon data
        for row_idx, row in enumerate(rows):
            cols = row.find_all("td")

            # Skip if not enough columns or if it's a header row
            if len(cols) < 12:
                continue

            try:
                # Extract Pokemon number from first column, keeping the format #0001
                number_text = cols[0].get_text(strip=True)
                if not number_text.startswith("#") or len(number_text) < 2:
                    continue

                # Keep the original format (#0001) but also extract numeric value for comparisons
                number = number_text  # Keep original format like "#0001"
                numeric_number = int(
                    number_text.replace("#", "")
                )  # For numeric comparisons

                # Extract Pokemon name from the name column (index 3)
                name_cell = cols[3]
                name_link = name_cell.find("a")
                if name_link:
                    name = name_link.get_text(strip=True)
                else:
                    name = name_cell.get_text(strip=True)

                # Extract abilities - they are in <a> tags linking to ability pages
                abilities = []

                # Look through all columns for ability links
                for col in cols:
                    ability_links = col.find_all("a")
                    for link in ability_links:
                        href = link.get("href")
                        if href and "abilitydex" in str(href):
                            ability_name = link.get_text(strip=True)
                            if ability_name and ability_name not in abilities:
                                abilities.append(ability_name)

                # Extract types - they are <img> tags with type images
                types = []
                for col in cols:
                    type_images = col.find_all("img")
                    for img in type_images:
                        src = img.get("src")
                        if src and "/type/" in str(src):
                            type_name = (
                                str(src)
                                .split("/type/")[-1]
                                .replace(".gif", "")
                                .replace(".png", "")
                            )
                            if type_name and type_name not in types:
                                types.append(type_name.title())

                # Extract base stats from specific columns
                hp = None
                attack = None
                defense = None
                sp_attack = None
                sp_defense = None
                speed = None

                # Debug: print all column values for first Pokemon
                if number_text == "#0001":
                    print(f"Bulbasaur columns ({len(cols)} total):")
                    for i, col in enumerate(cols):
                        print(f"  Col {i}: '{col.get_text(strip=True)}'")

                # HP is in column 7
                if len(cols) > 7:
                    hp_value = cols[7].get_text(strip=True)
                    if hp_value.isdigit():
                        hp = int(hp_value)

                # Attack is in column 8
                if len(cols) > 8:
                    att_value = cols[8].get_text(strip=True)
                    if att_value.isdigit():
                        attack = int(att_value)

                # Defense is in column 9
                if len(cols) > 9:
                    defense_value = cols[9].get_text(strip=True)
                    if defense_value.isdigit():
                        defense = int(defense_value)

                # Special Attack is in column 10
                if len(cols) > 10:
                    sp_attack_value = cols[10].get_text(strip=True)
                    if sp_attack_value.isdigit():
                        sp_attack = int(sp_attack_value)

                # Special Defense is in column 11
                if len(cols) > 11:
                    sp_defense_value = cols[11].get_text(strip=True)
                    if sp_defense_value.isdigit():
                        sp_defense = int(sp_defense_value)

                # Speed is in column 12 (13th column, 0-indexed)
                if len(cols) > 12:
                    speed_value = cols[12].get_text(strip=True)
                    if speed_value.isdigit():
                        speed = int(speed_value)  # Only add if we have valid data
                if number and name and name != "Unknown":

                    base_stats = {
                        "hp": hp,
                        "attack": attack,
                        "defense": defense,
                        "sp_attack": sp_attack,
                        "sp_defense": sp_defense,
                        "speed": speed,
                    }

                    pokemon_data = {
                        "number": number,
                        "name": name,
                        "abilities": abilities,
                        "types": types,
                        "base_stats": base_stats,
                    }

                    pokemon_list.append(pokemon_data)

                    print(
                        f"Added: {number} {name} - Abilities: {abilities}, Types: {types} - Base Stats: hp: {hp} attack: {attack} defense: {defense} sp_attack: {sp_attack} sp_defense: {sp_defense} speed: {speed}"
                    )

                # Stop if we've reached the expected end
                if numeric_number >= 1025:
                    break

            except (ValueError, IndexError) as e:
                print(f"Error processing row {row_idx} in table {table_idx}: {e}")
                continue

    return pokemon_list


# running the scraper and saving to JSON

if __name__ == "__main__":
    print("Starting Pokemon scraper...")
    pokemons = fetch_pokemon()
    print(f"Found {len(pokemons)} Pokemon")
    if pokemons:
        print("First few Pokemon:")
        for i, p in enumerate(pokemons[:4]):
            print(f"  {i+1}: {p}")
    else:
        print("No Pokemon found!")

    output_path = "../data/pokemon_data.json"

    with open(output_path, "w") as f:
        json.dump(pokemons, f, indent=2)
    print(f"Saved to {output_path}")
