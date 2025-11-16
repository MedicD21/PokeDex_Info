#!/usr/bin/env python3
"""
Pokemon Data Collection System - Main Orchestrator
Manages and coordinates all specialized scrapers to build a comprehensive Pokemon database.

Project Structure:
- data/           - JSON data files
- scrapers/       - Specialized scraper modules
- utils/          - Shared utilities and configuration
- main.py         - This orchestrator script
"""

import os
import sys
import json
from typing import Dict, Any

# Add project paths
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), "utils"))
sys.path.append(os.path.join(os.path.dirname(__file__), "scrapers"))

from utils.config import PokeDataUtils, DATA_FILES


class PokemonDataOrchestrator:
    """Main orchestrator for the Pokemon data collection system"""

    def __init__(self):
        self.utils = PokeDataUtils()
        self.available_scrapers = {
            "basic": "Basic Pokemon info (name, number, types, abilities, base stats)",
            "comprehensive": "Detailed Pokemon data (physical info, regional dex, etc.)",
            "abilities": "Pokemon abilities database",
            "games": "Pokemon games and regional dex numbers",
            "moves": "Pokemon moves and move sets",
            "locations": "Pokemon locations and encounter data",
        }

    def show_project_status(self):
        """Display current project status and data completeness"""
        print("=== Pokemon Data Collection System Status ===")
        print()

        # Check data files
        print("Data Files Status:")
        for data_type, file_path in DATA_FILES.items():
            if os.path.exists(file_path):
                try:
                    data = self.utils.load_json_data(file_path)
                    if isinstance(data, list):
                        count = len(data)
                    elif isinstance(data, dict):
                        count = len(data.keys())
                    else:
                        count = 0
                    print(f"  ✓ {data_type.title()}: {count} entries ({file_path})")
                except Exception as e:
                    print(f"  ✗ {data_type.title()}: Error loading ({e})")
            else:
                print(f"  ○ {data_type.title()}: Not found ({file_path})")

        print()

        # Check Pokemon data completeness if available
        pokemon_data = self.utils.load_json_data(DATA_FILES["pokemon"])
        if isinstance(pokemon_data, list) and pokemon_data:
            print("Pokemon Data Completeness:")
            total = len(pokemon_data)

            # Basic stats
            with_abilities = sum(1 for p in pokemon_data if p.get("abilities"))
            with_base_stats = sum(1 for p in pokemon_data if p.get("base_stats"))
            with_types = sum(1 for p in pokemon_data if p.get("types"))

            # Extended stats
            with_physical = sum(1 for p in pokemon_data if p.get("physical_info"))
            with_games = sum(1 for p in pokemon_data if p.get("game_appearances"))
            with_evolution = sum(1 for p in pokemon_data if p.get("evolution_info"))

            print(f"  Basic Info Coverage:")
            print(f"    Types: {with_types}/{total} ({(with_types/total*100):.1f}%)")
            print(
                f"    Abilities: {with_abilities}/{total} ({(with_abilities/total*100):.1f}%)"
            )
            print(
                f"    Base Stats: {with_base_stats}/{total} ({(with_base_stats/total*100):.1f}%)"
            )

            print(f"  Extended Info Coverage:")
            print(
                f"    Physical Info: {with_physical}/{total} ({(with_physical/total*100):.1f}%)"
            )
            print(
                f"    Game Appearances: {with_games}/{total} ({(with_games/total*100):.1f}%)"
            )
            print(
                f"    Evolution Info: {with_evolution}/{total} ({(with_evolution/total*100):.1f}%)"
            )

        print()

    def run_scraper(self, scraper_name: str):
        """Run a specific scraper"""
        print(f"Running {scraper_name} scraper...")

        import subprocess
        import sys

        try:
            if scraper_name == "basic":
                print("Running basic Pokemon scraper...")
                result = subprocess.run(
                    [sys.executable, "scrapers/pokemon_info.py"],
                    cwd=os.path.dirname(__file__),
                    capture_output=False,
                )
                if result.returncode != 0:
                    print(f"Basic scraper exited with code {result.returncode}")

            elif scraper_name == "comprehensive":
                from scrapers.comprehensive_scraper import main as run_comprehensive_scraper

                run_comprehensive_scraper()

            elif scraper_name == "abilities":
                print("Running abilities scraper...")
                result = subprocess.run(
                    [sys.executable, "scrapers/abilities_scraper.py"],
                    cwd=os.path.dirname(__file__),
                    capture_output=False,
                )
                if result.returncode != 0:
                    print(f"Abilities scraper exited with code {result.returncode}")

            elif scraper_name == "games":
                print("Running game dex scraper...")
                result = subprocess.run(
                    [sys.executable, "scrapers/game_dex_scraper.py"],
                    cwd=os.path.dirname(__file__),
                    capture_output=False,
                )
                if result.returncode != 0:
                    print(f"Game dex scraper exited with code {result.returncode}")

            elif scraper_name == "moves":
                print("Running moves scraper...")
                result = subprocess.run(
                    [sys.executable, "scrapers/moves_scraper.py"],
                    cwd=os.path.dirname(__file__),
                    capture_output=False,
                )
                if result.returncode != 0:
                    print(f"Moves scraper exited with code {result.returncode}")

            elif scraper_name == "items":
                print("Running items scraper...")
                result = subprocess.run(
                    [sys.executable, "scrapers/items_scraper.py"],
                    cwd=os.path.dirname(__file__),
                    capture_output=False,
                )
                if result.returncode != 0:
                    print(f"Items scraper exited with code {result.returncode}")

            else:
                print(f"Scraper '{scraper_name}' not implemented yet")

        except Exception as e:
            print(f"Error running {scraper_name} scraper: {e}")

    def run_excel_import(self):
        """Run Excel data import"""
        print("Running Excel data import...")

        import subprocess
        import sys

        try:
            print("Importing data from Master_Pokedex_Database.xlsx...")
            result = subprocess.run(
                [sys.executable, "scrapers/excel_importer.py"],
                cwd=os.path.dirname(__file__),
                capture_output=False,
            )
            if result.returncode == 0:
                print("✅ Excel import completed successfully!")
            else:
                print(f"Excel import exited with code {result.returncode}")

        except Exception as e:
            print(f"Error running Excel import: {e}")

    def show_menu(self):
        """Display main menu"""
        print("=== Pokemon Data Collection System ===")
        print()
        print("Data Sources:")
        print("1. Show project status - [READ ONLY]")
        print()
        print("Excel Import:")
        print("2. Import from Excel spreadsheet - [MERGES WITH data/pokemon_data.json]")
        print()
        print("Serebii Web Scrapers:")
        print("3. Run basic Pokemon scraper - [SAVES TO data/pokemon_data.json]")
        print("4. Run comprehensive Pokemon scraper - [HAS PREVIEW & SAVE OPTIONS]")
        print("5. Run game dex scraper - [SAVES TO data/pokemon_data.json]")
        print("6. Run abilities scraper - [SAVES TO data/abilities_data.json]")
        print("7. Run moves scraper - [SAVES TO data/moves_data.json]")
        print("8. Run items scraper - [SAVES TO data/items_data.json]")
        print("9. Run all scrapers (complete collection) - [SAVES ALL DATA]")
        print()
        print("Tools & Management:")
        print("10. Data management tools - [BACKUP/VALIDATION TOOLS]")
        print("11. Exit")
        print()

    def data_management_menu(self):
        """Data management and utility menu"""
        while True:
            print("=== Data Management Tools ===")
            print("1. Backup current data")
            print("2. Validate data integrity")
            print("3. Export data summary")
            print("4. Check Excel file status")
            print("5. Clean up duplicate entries")
            print("6. Reset specific dataset")
            print("7. Return to main menu")

            choice = input("Choose option (1-7): ").strip()

            if choice == "1":
                self.backup_data()
            elif choice == "2":
                self.validate_data()
            elif choice == "3":
                self.export_summary()
            elif choice == "4":
                self.check_excel_status()
            elif choice == "5":
                self.clean_duplicates()
            elif choice == "6":
                self.reset_dataset()
            elif choice == "7":
                break
            else:
                print("Invalid choice.")
            print()

    def backup_data(self):
        """Create backup of all data files"""
        import shutil
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = f"data/backups/backup_{timestamp}"
        os.makedirs(backup_dir, exist_ok=True)

        for data_type, file_path in DATA_FILES.items():
            if os.path.exists(file_path):
                backup_path = os.path.join(backup_dir, os.path.basename(file_path))
                shutil.copy2(file_path, backup_path)
                print(f"  Backed up {data_type} to {backup_path}")

        print(f"Backup completed in {backup_dir}")

    def validate_data(self):
        """Validate data integrity"""
        print("Validating data integrity...")

        issues = []

        # Check Pokemon data
        pokemon_data = self.utils.load_json_data(DATA_FILES["pokemon"])
        if isinstance(pokemon_data, list):
            names = [p.get("name") for p in pokemon_data]
            duplicates = set([name for name in names if names.count(name) > 1])
            if duplicates:
                issues.append(f"Duplicate Pokemon names: {list(duplicates)}")

            missing_fields = []
            for i, pokemon in enumerate(pokemon_data):
                if not pokemon.get("name"):
                    missing_fields.append(f"Pokemon {i}: missing name")
                if not pokemon.get("number"):
                    missing_fields.append(f"Pokemon {i}: missing number")

            if missing_fields:
                issues.extend(missing_fields[:10])  # Show first 10 issues

        if issues:
            print("Data integrity issues found:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("Data integrity check passed!")

    def export_summary(self):
        """Export data summary"""
        summary = {
            "project_info": {
                "name": "Pokemon Data Collection System",
                "data_files": len(DATA_FILES),
                "scrapers": len(self.available_scrapers),
            },
            "data_counts": {},
        }

        for data_type, file_path in DATA_FILES.items():
            if os.path.exists(file_path):
                data = self.utils.load_json_data(file_path)
                if isinstance(data, list):
                    summary["data_counts"][data_type] = len(data)
                elif isinstance(data, dict):
                    summary["data_counts"][data_type] = len(data.keys())

        summary_file = "data/project_summary.json"
        self.utils.save_json_data(summary, summary_file)
        print(f"Summary exported to {summary_file}")
        print(json.dumps(summary, indent=2))

    def check_excel_status(self):
        """Check Excel file status and information"""
        excel_file = "Master_Pokedex_Database.xlsx"

        print("=== Excel File Status ===")

        if os.path.exists(excel_file):
            from datetime import datetime

            # Get file info
            file_size = os.path.getsize(excel_file)
            mod_time = os.path.getmtime(excel_file)
            mod_date = datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M:%S")

            print(f"✅ Excel file found: {excel_file}")
            print(f"   Size: {file_size:,} bytes ({file_size/(1024*1024):.1f} MB)")
            print(f"   Last modified: {mod_date}")

            # Try to get basic Excel info
            try:
                import pandas as pd

                excel_info = pd.ExcelFile(excel_file)
                sheet_names = [str(name) for name in excel_info.sheet_names]
                print(f"   Sheets: {', '.join(sheet_names)}")

                # Check main sheet
                if "MasterDex" in excel_info.sheet_names:
                    df = pd.read_excel(excel_file, sheet_name="MasterDex", header=1)
                    print(
                        f"   MasterDex sheet: {len(df)} rows, {len(df.columns)} columns"
                    )

                    # Check for ref_id column
                    if "ref_id" in df.columns:
                        base_forms = df[df["ref_id"].str.endswith("-00", na=False)]
                        print(f"   Base forms (-00): {len(base_forms)} entries")
                    else:
                        print("   Warning: 'ref_id' column not found")

            except ImportError:
                print("   Note: Install pandas to see detailed Excel info")
            except Exception as e:
                print(f"   Error reading Excel file: {e}")

        else:
            print(f"❌ Excel file not found: {excel_file}")
            print("   Make sure the Excel file is in the project root directory")

        print()

    def clean_duplicates(self):
        """Clean duplicate entries"""
        print("Duplicate cleaning not yet implemented")

    def reset_dataset(self):
        """Reset a specific dataset"""
        print("Available datasets to reset:")
        for i, (data_type, file_path) in enumerate(DATA_FILES.items(), 1):
            print(f"{i}. {data_type.title()} ({file_path})")

        choice = input("Choose dataset to reset (number or 'cancel'): ").strip()
        if choice.lower() == "cancel":
            return

        try:
            choice_idx = int(choice) - 1
            data_types = list(DATA_FILES.keys())
            if 0 <= choice_idx < len(data_types):
                data_type = data_types[choice_idx]
                file_path = DATA_FILES[data_type]

                confirm = (
                    input(f"Really reset {data_type}? This cannot be undone (y/n): ")
                    .strip()
                    .lower()
                )
                if confirm == "y":
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        print(f"Reset {data_type} dataset")
                    else:
                        print(f"{data_type} dataset doesn't exist")
        except (ValueError, IndexError):
            print("Invalid choice")

    def run(self):
        """Main program loop"""
        while True:
            self.show_menu()
            choice = input("Choose option (1-11): ").strip()

            if choice == "1":
                self.show_project_status()
            elif choice == "2":
                self.run_excel_import()
                input("\nPress Enter to continue...")
            elif choice == "3":
                self.run_scraper("basic")
                input("\nPress Enter to continue...")
            elif choice == "4":
                self.run_scraper("comprehensive")
                input("\nPress Enter to continue...")
            elif choice == "5":
                self.run_scraper("games")
                input("\nPress Enter to continue...")
            elif choice == "6":
                self.run_scraper("abilities")
                input("\nPress Enter to continue...")
            elif choice == "7":
                self.run_scraper("moves")
                input("\nPress Enter to continue...")
            elif choice == "8":
                self.run_scraper("items")
                input("\nPress Enter to continue...")
            elif choice == "9":
                print("Running all scrapers...")
                for scraper in [
                    "basic",
                    "comprehensive",
                    "games",
                    "abilities",
                    "moves",
                    "items",
                ]:
                    print(f"\n--- Running {scraper} scraper ---")
                    self.run_scraper(scraper)
                print("All scrapers completed!")
            elif choice == "10":
                self.data_management_menu()
            elif choice == "11":
                print("Goodbye!")
                break
            else:
                print("Invalid choice.")

            print("\n" + "=" * 50 + "\n")


def main():
    """Entry point"""
    orchestrator = PokemonDataOrchestrator()
    orchestrator.run()


if __name__ == "__main__":
    main()
