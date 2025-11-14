#!/usr/bin/env python3
"""
Pokemon Items Scraper
Scrapes comprehensive item data from Serebii.net including item details and locations.
"""

import sys
import os
import json
import time
import re
from typing import Dict, List, Any, Optional

# Add project paths
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "utils"))

from config import PokeDataUtils, DATA_FILES


class ItemsDataScraper:
    """Scrapes Pokemon items data from Serebii"""

    def __init__(self):
        self.utils = PokeDataUtils()
        self.items_data = []
        self.base_url = "https://www.serebii.net/itemdex/"

        # Item categories
        self.item_categories = {
            "tm": "Technical Machine",
            "tr": "Technical Record",
            "berry": "Berry",
            "ball": "Poké Ball",
            "medicine": "Medicine",
            "battle": "Battle Item",
            "key": "Key Item",
            "general": "General Item",
            "hold": "Hold Item",
            "evolution": "Evolution Item",
        }

    def scrape_items_list(self) -> List[str]:
        """Get list of all items from the main item dex"""
        print("Fetching items list from Serebii...")

        try:
            soup = self.utils.safe_request(self.base_url)
            if not soup:
                return []

            item_links = []

            # Look for all links that could be item pages
            for link in soup.find_all("a", href=True):
                href = link.get("href", "")
                if href.endswith(".shtml") and not href.startswith("http"):
                    item_file = href.replace(".shtml", "")
                    if item_file and item_file != "index":
                        item_links.append(item_file)

            # Also try to find items from category pages
            category_pages = ["tm", "berry", "ball", "medicine", "keyitem"]
            for category in category_pages:
                try:
                    category_url = f"{self.base_url}{category}.shtml"
                    category_soup = self.utils.safe_request(category_url)
                    if category_soup:
                        for link in category_soup.find_all("a", href=True):
                            href = link.get("href", "")
                            if href.endswith(".shtml") and not href.startswith("http"):
                                item_file = href.replace(".shtml", "")
                                if item_file and item_file not in item_links:
                                    item_links.append(item_file)
                    time.sleep(0.3)  # Rate limiting
                except Exception as e:
                    print(f"Error fetching {category} items: {e}")

            print(f"Found {len(item_links)} items to scrape")
            return list(set(item_links))  # Remove duplicates

        except Exception as e:
            print(f"Error fetching items list: {e}")
            return []

    def scrape_item_data(self, item_filename: str) -> Optional[Dict[str, Any]]:
        """Scrape detailed data for a specific item"""
        item_url = f"{self.base_url}{item_filename}.shtml"

        try:
            soup = self.utils.safe_request(item_url)
            if not soup:
                return None

            item_data = {
                "name": "",
                "category": "",
                "description": "",
                "effect": "",
                "buy_price": None,
                "sell_price": None,
                "locations": [],  # Where to find this item
                "games_available": [],  # Which games have this item
            }

            # Extract item name from page title
            title = soup.find("title")
            if title:
                title_text = title.get_text()
                if " - " in title_text:
                    item_data["name"] = title_text.split(" - ")[0].strip()

            # Look for item data tables
            tables = soup.find_all("table")
            for table in tables:
                rows = table.find_all("tr")
                for row in rows:
                    cells = row.find_all(["td", "th"])
                    if len(cells) >= 2:
                        header = cells[0].get_text().strip().lower()
                        value = cells[1].get_text().strip()

                        if "category" in header or "type" in header:
                            item_data["category"] = value
                        elif "description" in header or "effect" in header:
                            item_data["description"] = value
                        elif "buy" in header and "price" in header:
                            try:
                                # Extract number from price string
                                price_match = re.search(
                                    r"(\d+)", value.replace(",", "")
                                )
                                if price_match:
                                    item_data["buy_price"] = int(price_match.group(1))
                            except:
                                pass
                        elif "sell" in header and "price" in header:
                            try:
                                price_match = re.search(
                                    r"(\d+)", value.replace(",", "")
                                )
                                if price_match:
                                    item_data["sell_price"] = int(price_match.group(1))
                            except:
                                pass

            # Extract locations where item can be found
            item_data["locations"] = self.extract_item_locations(soup)

            # Extract games where item is available
            item_data["games_available"] = self.extract_games_available(soup)

            # Determine category from filename if not found
            if not item_data["category"]:
                if "tm" in item_filename.lower():
                    item_data["category"] = "Technical Machine"
                elif "berry" in item_filename.lower():
                    item_data["category"] = "Berry"
                elif "ball" in item_filename.lower():
                    item_data["category"] = "Poké Ball"
                else:
                    item_data["category"] = "General Item"

            # Extract description from page content if not found in table
            if not item_data["description"]:
                for element in soup.find_all(["p", "div"]):
                    text = element.get_text().strip()
                    if len(text) > 30 and not any(
                        skip in text.lower()
                        for skip in ["copyright", "serebii", "navigation", "menu"]
                    ):
                        item_data["description"] = (
                            text[:300] + "..." if len(text) > 300 else text
                        )
                        break

            # Set fallback name
            if not item_data["name"]:
                item_data["name"] = item_filename.replace("-", " ").title()

            return item_data

        except Exception as e:
            print(f"Error scraping item {item_filename}: {e}")
            return None

    def extract_item_locations(self, soup) -> List[Dict[str, Any]]:
        """Extract locations where this item can be found"""
        locations = []

        try:
            tables = soup.find_all("table")
            for table in tables:
                rows = table.find_all("tr")
                for row in rows:
                    cells = row.find_all(["td", "th"])
                    if len(cells) >= 2:
                        # Look for location information
                        for i, cell in enumerate(cells):
                            text = cell.get_text().strip()

                            # Common location keywords
                            location_keywords = [
                                "route",
                                "city",
                                "town",
                                "cave",
                                "forest",
                                "mountain",
                                "tower",
                                "gym",
                                "shop",
                                "mart",
                            ]

                            if any(
                                keyword in text.lower() for keyword in location_keywords
                            ):
                                location_data = {
                                    "location": text,
                                    "method": "Found",
                                    "game": "Various",
                                }

                                # Try to find method in nearby cells
                                if i + 1 < len(cells):
                                    method_text = cells[i + 1].get_text().strip()
                                    if method_text and len(method_text) < 50:
                                        location_data["method"] = method_text

                                # Try to find game in nearby cells
                                for other_cell in cells:
                                    other_text = other_cell.get_text().strip()
                                    if any(
                                        game in other_text
                                        for game in [
                                            "Red",
                                            "Blue",
                                            "Yellow",
                                            "Gold",
                                            "Silver",
                                            "Ruby",
                                            "Sapphire",
                                            "Diamond",
                                            "Pearl",
                                            "Black",
                                            "White",
                                            "X",
                                            "Y",
                                        ]
                                    ):
                                        location_data["game"] = other_text
                                        break

                                locations.append(location_data)

        except Exception as e:
            print(f"Error extracting locations: {e}")

        return locations

    def extract_games_available(self, soup) -> List[str]:
        """Extract which games this item appears in"""
        games = []

        try:
            # Look for game names in the page content
            content = soup.get_text().lower()

            game_names = [
                "red",
                "blue",
                "yellow",
                "gold",
                "silver",
                "crystal",
                "ruby",
                "sapphire",
                "emerald",
                "firered",
                "leafgreen",
                "diamond",
                "pearl",
                "platinum",
                "heartgold",
                "soulsilver",
                "black",
                "white",
                "x",
                "y",
                "omega ruby",
                "alpha sapphire",
                "sun",
                "moon",
                "ultra sun",
                "ultra moon",
                "sword",
                "shield",
                "scarlet",
                "violet",
            ]

            for game in game_names:
                if game in content:
                    games.append(game.title())

        except Exception as e:
            print(f"Error extracting games: {e}")

        return list(set(games))  # Remove duplicates

    def scrape_all_items(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Scrape all items data"""
        print("=== Pokemon Items Scraper ===")
        print("Fetching comprehensive items data from Serebii.net")
        print()

        # Get list of items
        item_files = self.scrape_items_list()
        if not item_files:
            print("No items found to scrape!")
            return []

        if limit:
            item_files = item_files[:limit]
            print(f"Limiting to first {limit} items for testing")

        print(f"Scraping {len(item_files)} items...")
        print()

        items_data = []

        for i, item_file in enumerate(item_files, 1):
            print(f"[{i:3d}/{len(item_files)}] Scraping {item_file}...")

            item_data = self.scrape_item_data(item_file)
            if item_data:
                items_data.append(item_data)
                location_count = len(item_data["locations"])
                print(
                    f"  ✓ {item_data['name']} - {item_data['category']}, {location_count} locations"
                )
            else:
                print(f"  ✗ Failed to scrape {item_file}")

            # Rate limiting
            time.sleep(0.5)

            # Progress update every 25 items
            if i % 25 == 0:
                print(f"\n--- Progress: {i}/{len(item_files)} items completed ---\n")

        print(f"\n✅ Scraping complete! Collected {len(items_data)} items")
        return items_data

    def save_items_data(self, items_data: List[Dict[str, Any]]):
        """Save items data to JSON file"""
        output_file = DATA_FILES["items"]

        # Create backup if file exists
        if os.path.exists(output_file):
            backup_file = output_file.replace(".json", "_backup.json")
            os.rename(output_file, backup_file)
            print(f"Created backup: {backup_file}")

        # Save new data
        self.utils.save_json_data(items_data, output_file)
        print(f"✅ Saved {len(items_data)} items to {output_file}")

        # Print summary stats
        categories_count = {}
        total_locations = 0
        items_with_prices = 0

        for item in items_data:
            # Count by category
            category = item.get("category", "Unknown")
            categories_count[category] = categories_count.get(category, 0) + 1

            # Count locations
            total_locations += len(item.get("locations", []))

            # Count items with prices
            if item.get("buy_price") or item.get("sell_price"):
                items_with_prices += 1

        print(f"\n📊 Items Data Summary:")
        print(f"   Total Items: {len(items_data)}")
        print(f"   Total Item Locations: {total_locations}")
        print(f"   Items with Price Data: {items_with_prices}")
        print(f"   Item Categories: {len(categories_count)}")
        for category, count in sorted(categories_count.items()):
            print(f"     {category}: {count}")


def main():
    """Main execution function"""
    scraper = ItemsDataScraper()

    # Ask user for scraping options
    print("Pokemon Items Scraper")
    print("1. Scrape all items (full dataset)")
    print("2. Scrape first 50 items (testing)")
    print("3. Scrape first 10 items (quick test)")

    choice = input("Choose option (1-3): ").strip()

    limit = None
    if choice == "2":
        limit = 50
    elif choice == "3":
        limit = 10
    elif choice != "1":
        print("Invalid choice, defaulting to full scrape")

    # Scrape items data
    items_data = scraper.scrape_all_items(limit=limit)

    if items_data:
        # Save data
        scraper.save_items_data(items_data)
        print(f"\n🎉 Items scraping completed successfully!")
    else:
        print("❌ No items data collected")


if __name__ == "__main__":
    main()
