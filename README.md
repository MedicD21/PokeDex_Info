# Pokemon Data Collection System

A comprehensive Python-based system for scraping Pokemon data from Serebii.net and importing data from Excel spreadsheets. This system collects, processes, and organizes Pokemon data for analysis and future programming projects.

## Project Structure

```
PokeDex_Info/
├── main.py                               # Main orchestrator script
├── requirements.txt                      # Python dependencies
├── Master_Pokedex_Database.xlsx         # Excel data source
├── venv/                                # Virtual environment
├── data/                                # Data storage
│   ├── pokemon_data.json               # Main Pokemon dataset (1025 entries)
│   ├── pokemon_data_backup_before_excel.json # Backup before Excel import
│   ├── pokemon_games.json              # Pokemon games information
│   └── abilities_data.json             # Abilities database
├── scrapers/                            # Data collection scripts
│   ├── pokemon_info.py                 # Basic Pokemon info scraper
│   ├── comprehensive_scraper.py        # Detailed Pokemon data scraper
│   ├── game_dex_scraper.py            # Game-specific dex numbers
│   ├── abilities_scraper.py           # Abilities scraper
│   └── excel_importer.py              # Excel data importer & merger
└── utils/                               # Shared utilities
    ├── config.py                       # Configuration and utilities
    └── grab_info.py                    # Data access functions
```

## What Each Component Does

### 📁 Data Files (`data/`)

- **`pokemon_data.json`** - The main Pokemon dataset containing 1025 Pokemon with comprehensive information including base stats, breeding info, physical data, game appearances, evolution chains, and Pokedex entries across all games
- **`pokemon_data_backup_before_excel.json`** - Backup created before Excel imports to preserve data integrity
- **`pokemon_games.json`** - Database of all Pokemon games with regional information and chronological data
- **`abilities_data.json`** - Complete abilities database with descriptions and effects

### 🔧 Scrapers (`scrapers/`)

1. **`pokemon_info.py`** - Basic Pokemon Data Scraper

   - Scrapes fundamental Pokemon data from Serebii's main Pokedex
   - Collects: National dex number, name, types, abilities, base stats (HP, Attack, Defense, Sp. Attack, Sp. Defense, Speed)
   - Fast and efficient for basic data collection

2. **`comprehensive_scraper.py`** - Detailed Pokemon Data Scraper

   - Collects comprehensive information from individual Pokemon pages
   - Adds: Physical stats, species info, regional dex numbers, game appearances, locations
   - Parses complex HTML structures and handles concatenated data
   - More thorough but slower than basic scraper

3. **`game_dex_scraper.py`** - Regional Pokedex Number Scraper

   - Focuses specifically on regional Pokedex numbers across all games
   - Maps regional entries to specific games (e.g., "Kanto (RBY)" → Red/Blue/Yellow)
   - Handles DLC areas and special regions like Isle of Armor, Crown Tundra

4. **`abilities_scraper.py`** - Abilities Database Scraper

   - Scrapes detailed ability information from Serebii
   - Collects descriptions, effects, and lists of Pokemon that have each ability
   - Creates comprehensive abilities reference

5. **`excel_importer.py`** - Excel Data Importer & Merger
   - Imports data from `Master_Pokedex_Database.xlsx`
   - Merges Excel data with existing JSON data intelligently
   - Handles data normalization (e.g., fixes comma-separated gender ratios)
   - Creates backups before making changes
   - Processes breeding info, game mechanics, physical data, and Pokedex entries

### 🛠️ Utilities (`utils/`)

- **`config.py`** - Configuration System & Utilities

  - Centralized settings and URL management for all scrapers
  - Data file path management and constants
  - Common parsing utilities and helper functions
  - Request handling with rate limiting to respect Serebii's servers
  - Shared data structures and validation functions

- **`grab_info.py`** - Data Access Functions
  - Easy programmatic access to Pokemon data
  - Game information queries and filtering
  - Search functions for finding specific Pokemon or data
  - Helper functions for analyzing and working with the dataset

### 📊 Excel Integration

- **`Master_Pokedex_Database.xlsx`** - Excel Data Source
  - Comprehensive Excel spreadsheet with 1025+ Pokemon entries
  - Contains base stats, breeding information, physical data, and game-specific information
  - Serves as authoritative source for certain data fields
  - Updated and maintained separately, then imported via `excel_importer.py`

### 🚀 Main Script

- **`main.py`** - Orchestrator Script
  - Coordinates all scrapers and data collection processes
  - Manages the workflow for comprehensive data gathering
  - Handles error recovery and progress tracking
  - Entry point for running the complete data collection system

## Usage

### Quick Start

```bash
# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt

# Run the main orchestrator
python main.py
```

### Running Individual Components

#### Website Scrapers

```bash
# Basic Pokemon data from Serebii
python scrapers/pokemon_info.py

# Comprehensive data collection
python scrapers/comprehensive_scraper.py

# Game-specific dex numbers
python scrapers/game_dex_scraper.py

# Abilities database
python scrapers/abilities_scraper.py
```

#### Excel Data Processing

```bash
# Import and merge Excel data (creates backup automatically)
python scrapers/excel_importer.py
```

### Using Data Access Functions

```python
from utils.grab_info import pk_names, get_pokemon_by_name, get_all_games

# Get all Pokemon names
pokemon_names = pk_names()

# Get specific Pokemon data
bulbasaur = get_pokemon_by_name("Bulbasaur")

# Get all games
games = get_all_games()
```

## Data Structure

### Pokemon Data Format

The main `pokemon_data.json` contains comprehensive Pokemon information organized into logical categories:

```json
{
  "ref_id": "0001-00",
  "number": "#0001",
  "name": "Bulbasaur",
  "types": ["Grass", "Poison"],
  "abilities": ["Overgrow", "Chlorophyll"],
  "base_stats": {
    "hp": 45,
    "attack": 49,
    "defense": 49,
    "sp_attack": 65,
    "sp_defense": 65,
    "speed": 45,
    "total": 318
  },
  "physical_info": {
    "species": "Seed Pokémon",
    "height": "0.7 m (2′04″)",
    "weight": "6.9 kg (15.2 lbs)"
  },
  "breeding_info": {
    "egg_groups": ["Grass", "Monster"],
    "gender_ratio": "87.5% male, 12.5% female",
    "egg_cycles": 20,
    "base_friendship": 50
  },
  "game_mechanics": {
    "catch_rate": 45,
    "base_exp": 64,
    "growth_rate": "Medium Slow",
    "ev_yield": "1 Sp. Atk"
  },
  "evolution_info": {
    "evolution_chain": "Bulbasaur → Ivysaur (Level 16) → Venusaur (Level 32)"
  },
  "game_appearances": {
    "Red": {
      "dex_number": 1,
      "available": true,
      "location": "Pallet Town",
      "dex_entry": "A strange seed was planted on its back at birth..."
    }
  }
}
```

### Games Data Format

```json
{
  "generation": 1,
  "region": "Kanto",
  "games": ["Red", "Blue", "Yellow"],
  "release_year": 1996,
  "platform": "Game Boy"
}
```

## Data Integration Features

### Excel to JSON Merging

- **Intelligent Merging**: Excel data takes precedence for base stats, breeding info, and physical data
- **Data Normalization**: Automatically fixes formatting issues (e.g., comma-separated gender ratios)
- **Backup Creation**: Creates automatic backups before any data modifications
- **Validation**: Ensures data integrity during import process

### Regional Dex Mapping

The system automatically maps regional Pokedex entries to specific games:

- **Kanto (RBY)** → Red, Blue, Yellow
- **Kanto (Let's Go)** → Let's Go Pikachu, Let's Go Eevee
- **Johto (GSC)** → Gold, Silver, Crystal
- **Johto (HGSS)** → HeartGold, SoulSilver
- **Central Kalos** → X, Y
- **Isle of Armor** → Sword, Shield (DLC)
- **Blueberry** → Scarlet, Violet (DLC)
- **Lumiose** → Legends Z-A
- And many more...

## Development & Maintenance

### Adding New Scrapers

1. Create new scraper in `scrapers/` directory
2. Import and add to `main.py` orchestrator
3. Follow existing patterns for data structure
4. Use utilities from `utils/config.py` for consistency
5. Include respectful delays and error handling

### Data Management Best Practices

- **Automatic Backups**: System creates backups before major operations
- **Data Validation**: Built-in integrity checking and validation
- **Progress Tracking**: Long-running operations save progress
- **Error Recovery**: Robust error handling for network issues and parsing errors

### Excel Data Updates

1. Update `Master_Pokedex_Database.xlsx` with new information
2. Run `python scrapers/excel_importer.py` to merge changes
3. System automatically creates backup and validates data
4. Check console output for merge statistics and any issues

## System Features

- **Respectful Scraping**: 0.5-second delays between requests to avoid overwhelming servers
- **Data Integrity**: Comprehensive validation and backup systems
- **Flexible Architecture**: Easy to extend with new scrapers and data sources
- **Excel Integration**: Seamless merging of spreadsheet data with scraped information
- **Clean Data Structure**: Organized JSON format perfect for analysis and programming

## Contributing

When contributing:

1. Follow the established directory structure
2. Use the shared utilities for consistency
3. Include error handling and progress reporting
4. Test scrapers on small datasets first
5. Document any new data fields or structures
