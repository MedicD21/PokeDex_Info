import json


def _load_pokemon_data():
    """Helper function to load Pokemon data once and reuse it."""
    import os

    data_path = os.path.join(
        os.path.dirname(__file__), "..", "data", "pokemon_data.json"
    )
    with open(data_path, "r") as file:
        return json.load(file)


def _load_games_data():
    """Helper function to load Pokemon games data once and reuse it."""
    import os

    data_path = os.path.join(
        os.path.dirname(__file__), "..", "data", "pokemon_games.json"
    )
    with open(data_path, "r") as file:
        return json.load(file)


def pk_names():
    """Returns a list of all Pokemon names."""
    data = _load_pokemon_data()
    return [pokemon["name"] for pokemon in data]


def pk_nat_numbers():
    """Returns a list of all Pokemon numbers in #0001 format."""
    data = _load_pokemon_data()
    return [pokemon["number"] for pokemon in data]


def pk_abilities():
    """Returns a list of all Pokemon abilities (each item is a list of abilities for that Pokemon)."""
    data = _load_pokemon_data()
    return [pokemon["abilities"] for pokemon in data]


def pk_types():
    """Returns a list of all Pokemon types (each item is a list of types for that Pokemon)."""
    data = _load_pokemon_data()
    return [pokemon["types"] for pokemon in data]


def pk_base_stats():
    """Returns a list of all Pokemon base stats (each item is a dict with hp, attack, etc.)."""
    data = _load_pokemon_data()
    return [pokemon["base_stats"] for pokemon in data]


def get_pokemon_by_name(name):
    """Returns the complete data for a specific Pokemon by name."""
    data = _load_pokemon_data()
    for pokemon in data:
        if pokemon["name"].lower() == name.lower():
            return pokemon
    return None


def get_pokemon_by_number(number):
    """Returns the complete data for a specific Pokemon by number (e.g., '#0001' or '1')."""
    data = _load_pokemon_data()
    # Handle both '#0001' and '1' formats
    if isinstance(number, int):
        number = f"#{number:04d}"
    elif not number.startswith("#"):
        number = f"#{int(number):04d}"

    for pokemon in data:
        if pokemon["number"] == number:
            return pokemon
    return None


# Pokemon Games Functions
def get_all_games():
    """Returns a list of all Pokemon games across all generations."""
    data = _load_games_data()
    all_games = []
    for generation in data:
        all_games.extend(generation["games"])
    return all_games


def get_games_by_generation(gen_number):
    """Returns games for a specific generation number (1-9)."""
    data = _load_games_data()
    for generation in data:
        if generation["generation"] == gen_number:
            return generation["games"]
    return None


def get_games_by_region(region_name):
    """Returns games for a specific region (e.g., 'Kanto', 'Johto')."""
    data = _load_games_data()
    for generation in data:
        if generation["region"].lower() == region_name.lower():
            return generation["games"]
    return None


def get_generation_info(gen_number):
    """Returns complete information for a specific generation."""
    data = _load_games_data()
    for generation in data:
        if generation["generation"] == gen_number:
            return generation
    return None


def get_games_by_platform(platform_name):
    """Returns all games for a specific platform (e.g., 'Nintendo Switch')."""
    data = _load_games_data()
    platform_games = []
    for generation in data:
        if platform_name.lower() in generation["platform"].lower():
            platform_games.extend(generation["games"])
    return platform_games


# Game Appearance Functions
def get_pokemon_in_game(game_name):
    """Returns all Pokemon available in a specific game with their dex numbers."""
    data = _load_pokemon_data()
    pokemon_in_game = []

    for pokemon in data:
        if "game_appearances" in pokemon and game_name in pokemon["game_appearances"]:
            game_data = pokemon["game_appearances"][game_name]
            if game_data["available"]:
                pokemon_in_game.append(
                    {
                        "name": pokemon["name"],
                        "national_number": pokemon["number"],
                        "game_dex_number": game_data["dex_number"],
                    }
                )

    return sorted(
        pokemon_in_game,
        key=lambda x: x["game_dex_number"] if x["game_dex_number"] else 9999,
    )


def get_pokemon_game_availability(pokemon_name):
    """Returns all games where a specific Pokemon appears with dex numbers."""
    data = _load_pokemon_data()

    for pokemon in data:
        if pokemon["name"].lower() == pokemon_name.lower():
            if "game_appearances" in pokemon:
                return pokemon["game_appearances"]

    return None


def count_pokemon_in_game(game_name):
    """Returns the total number of Pokemon available in a specific game."""
    pokemon_in_game = get_pokemon_in_game(game_name)
    return len(pokemon_in_game)


# Example usage (uncomment to test)
# print(get_all_games())
# print(get_games_by_generation(1))
# print(get_pokemon_in_game("Scarlet")[:5])  # First 5 Pokemon in Scarlet
