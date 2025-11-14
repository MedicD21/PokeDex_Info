from bs4 import BeautifulSoup
import requests

url_base = "https://www.serebii.net/abilitydex/"
ability_list = []


def fetch_ability_list():
    response = requests.get(url_base)
    soup = BeautifulSoup(response.content, "html.parser")

    # Find both dropdown menus for abilities
    # Look for forms named "ability" and "ability2"
    form1 = soup.find("form", {"name": "ability"})
    form2 = soup.find("form", {"name": "ability2"})

    ability_dropdowns = []

    if form1:
        select1 = form1.find("select")
        if select1:
            ability_dropdowns.append(("ability (A-L)", select1))

    if form2:
        select2 = form2.find("select")
        if select2:
            ability_dropdowns.append(("ability2 (M-Z)", select2))

    if not ability_dropdowns:
        print("Could not find any ability select dropdowns")
        return ability_list

    print(f"Found {len(ability_dropdowns)} dropdown menu(s)")

    # Use a set to track unique abilities and avoid duplicates
    seen_abilities = set()

    # Process all dropdown menus
    for dropdown_name, select_element in ability_dropdowns:
        print(f"Processing dropdown: {dropdown_name}")

        options = select_element.find_all("option")
        dropdown_count = 0

        for option in options:
            ability_link = option.get("value", "")
            ability_name = option.get_text(strip=True)

            # Skip the header options and any empty values
            if (
                ability_link
                and ability_link != "index.shtml"
                and "AbilityDex"
                not in ability_name  # Skip both "AbilityDex A-L" and "AbilityDex M-Z"
            ):
                # Clean up the link - remove leading slash if present
                if ability_link.startswith("/"):
                    ability_link = ability_link[1:]

                # Create a unique identifier for this ability
                ability_identifier = (ability_name.lower(), ability_link.lower())

                # Only add if we haven't seen this ability before
                if ability_identifier not in seen_abilities:
                    ability_list.append((ability_name, ability_link))
                    seen_abilities.add(ability_identifier)
                    dropdown_count += 1
                else:
                    print(f"    Skipping duplicate: {ability_name}")

        print(f"  - Found {dropdown_count} unique abilities in {dropdown_name}")

    print(f"Total unique abilities found: {len(ability_list)}")
    return ability_list


def fetch_ability_details(ability_link):
    # Construct the full URL
    if ability_link.startswith("http"):
        full_url = ability_link
    elif ability_link.startswith("/"):
        full_url = "https://www.serebii.net" + ability_link
    else:
        # The ability_link already contains abilitydex/ prefix from the dropdown
        full_url = "https://www.serebii.net/" + ability_link

    try:
        response = requests.get(full_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        ability_details = {}

        # Try to find the ability name - could be in h1, h2, or title
        name_element = soup.find("h1") or soup.find("h2") or soup.find("title")
        if name_element:
            ability_details["name"] = name_element.get_text(strip=True)
        else:
            ability_details["name"] = "Unknown"

        # Initialize all fields
        ability_details["japanese_name"] = ""
        ability_details["game_text"] = ""
        ability_details["in_depth_effect"] = ""
        ability_details["blocks_abilities"] = []
        ability_details["pokemon_with_ability"] = []

        # Find the dextable with the ability details
        tables = soup.find_all("table", {"class": "dextable"})
        for table in tables:
            rows = table.find_all("tr")
            i = 0
            while i < len(rows):
                row = rows[i]
                cells = row.find_all(["td", "th"])

                # Look for Japanese name
                for cell in cells:
                    cell_text = cell.get_text(strip=True)
                    if "Jp. Name" in cell_text and i + 1 < len(rows):
                        next_row = rows[i + 1]
                        jp_cells = next_row.find_all(["td", "th"])
                        if len(jp_cells) >= 4:  # Name table has 4 columns
                            ability_details["japanese_name"] = jp_cells[3].get_text(
                                strip=True
                            )
                        break

                # Look for "Game's Text:"
                for cell in cells:
                    if "Game's Text:" in cell.get_text(strip=True):
                        if i + 1 < len(rows):
                            next_row = rows[i + 1]
                            desc_cells = next_row.find_all(["td", "th"])
                            if desc_cells:
                                ability_details["game_text"] = desc_cells[0].get_text(
                                    strip=True
                                )
                        break

                # Look for "In-Depth Effect:"
                for cell in cells:
                    if "In-Depth Effect:" in cell.get_text(strip=True):
                        if i + 1 < len(rows):
                            next_row = rows[i + 1]
                            desc_cells = next_row.find_all(["td", "th"])
                            if desc_cells:
                                ability_details["in_depth_effect"] = desc_cells[
                                    0
                                ].get_text(strip=True)
                        break

                # Look for blocking information
                for cell in cells:
                    cell_text = cell.get_text(strip=True)
                    if "Blocks" in cell_text and cell_text != "Blocks":
                        ability_details["blocks_abilities"].append(cell_text)

                i += 1

        # Look for Pokemon that have this ability
        pokemon_tables = soup.find_all("table", {"class": "dextable"})
        for table in pokemon_tables:
            # Check if this table contains Pokemon data (has "No." header)
            headers = table.find_all("tr")
            if headers:
                header_cells = headers[0].find_all(["td", "th"])
                if any("No." in cell.get_text() for cell in header_cells):
                    # This is a Pokemon table
                    pokemon_rows = table.find_all("tr")[2:]  # Skip header rows
                    for row in pokemon_rows:
                        cells = row.find_all(["td", "th"])
                        if len(cells) >= 3:
                            pokemon_name_cell = cells[
                                2
                            ]  # Name is usually in 3rd column
                            pokemon_name = pokemon_name_cell.get_text(strip=True)
                            if (
                                pokemon_name
                                and pokemon_name
                                not in ability_details["pokemon_with_ability"]
                            ):
                                ability_details["pokemon_with_ability"].append(
                                    pokemon_name
                                )

        # Set description as combination of game text and in-depth effect
        if ability_details["game_text"] and ability_details["in_depth_effect"]:
            ability_details["description"] = (
                f"{ability_details['game_text']} (Effect: {ability_details['in_depth_effect']})"
            )
        else:
            ability_details["description"] = (
                ability_details["game_text"]
                or ability_details["in_depth_effect"]
                or "Description not found"
            )

        return ability_details

    except requests.RequestException as e:
        print(f"Error fetching {full_url}: {e}")
        return {"name": "Error", "description": f"Failed to fetch: {e}"}


def export_to_json(abilities_data, filename="../data/abilities_data.json"):
    """Export abilities data to a JSON file for web app use"""
    import json
    from datetime import datetime

    # Create a structured JSON object
    json_data = {
        "metadata": {
            "source": "Serebii.net",
            "scraped_date": datetime.now().isoformat(),
            "total_abilities": len(abilities_data),
            "version": "1.0",
        },
        "abilities": [],
    }

    for ability in abilities_data:
        # Clean up the data for JSON export
        ability_json = {
            "name": ability["name"],
            "game_description": ability.get("game_text", ""),
            "technical_effect": ability.get("in_depth_effect", ""),
            "full_description": ability.get("description", ""),
            "interactions": {"blocks": ability.get("blocks_abilities", [])},
            "pokemon": ability.get("pokemon_with_ability", []),
        }
        json_data["abilities"].append(ability_json)

    # Write JSON file
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

    print(f"JSON data exported to {filename}")


def export_to_text(abilities_data, filename="../data/abilities_data.txt"):
    """Export abilities data to a structured text file"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("POKEMON ABILITY DEX\n")
        f.write("Scraped from Serebii.net\n")
        f.write(f"Total Abilities: {len(abilities_data)}\n")
        f.write("=" * 80 + "\n\n")

        for i, ability in enumerate(abilities_data, 1):
            f.write(f"[{i:03d}] {ability['name'].upper()}\n")
            f.write("-" * 60 + "\n")

            if ability["japanese_name"]:
                f.write(f"Japanese Name: {ability['japanese_name']}\n")

            f.write(f"Game Description: {ability['game_text']}\n")

            if ability["in_depth_effect"]:
                f.write(f"Technical Effect: {ability['in_depth_effect']}\n")

            if ability["blocks_abilities"]:
                f.write("Interactions:\n")
                for block in ability["blocks_abilities"]:
                    f.write(f"  - {block}\n")

            if ability["pokemon_with_ability"]:
                f.write(
                    f"Pokemon with this ability ({len(ability['pokemon_with_ability'])}):\n"
                )
                # Write Pokemon names in a more readable format
                pokemon_list = ", ".join(
                    ability["pokemon_with_ability"][:10]
                )  # Limit to first 10
                if len(ability["pokemon_with_ability"]) > 10:
                    pokemon_list += (
                        f" ... and {len(ability['pokemon_with_ability']) - 10} more"
                    )
                f.write(f"  {pokemon_list}\n")

            f.write("\n" + "=" * 80 + "\n\n")

    print(f"Text data exported to {filename}")


if __name__ == "__main__":
    abilities = fetch_ability_list()
    print(f"Found {len(abilities)} abilities")
    print("Starting to scrape ability details...")

    all_abilities_data = []

    for i, (ability_name, ability_link) in enumerate(abilities, 1):
        print(f"Processing ({i}/{len(abilities)}): {ability_name}")
        details = fetch_ability_details(ability_link)
        all_abilities_data.append(details)

        # Add a small delay to be respectful to the server
        import time

        time.sleep(0.5)

    print(f"\nSuccessfully scraped {len(all_abilities_data)} abilities!")

    # Export to both formats
    export_to_json(all_abilities_data)
    export_to_text(all_abilities_data)

    # Also print a summary of the first few abilities
    print("\nFirst 3 abilities preview:")
    for ability in all_abilities_data[:3]:
        print(f"- {ability['name']}: {ability['game_text'][:60]}...")
    print(f"\nData exported to both Ability_Dex.json and Ability_Dex.txt")
