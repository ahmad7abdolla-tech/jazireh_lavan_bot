import json
from typing import List, Dict, Optional

LOCATIONS_FILE = 'bot/locations/locations.json'

def load_locations() -> List[Dict]:
    try:
        with open(LOCATIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_locations(locations: List[Dict]) -> None:
    with open(LOCATIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(locations, f, ensure_ascii=False, indent=4)

def get_location_by_id(location_id: str) -> Optional[Dict]:
    locations = load_locations()
    for loc in locations:
        if loc.get('id') == location_id:
            return loc
    return None

def add_location(new_location: Dict) -> bool:
    locations = load_locations()
    if any(loc['id'] == new_location['id'] for loc in locations):
        return False  # شناسه تکراری است
    locations.append(new_location)
    save_locations(locations)
    return True

def update_location(location_id: str, updated_data: Dict) -> bool:
    locations = load_locations()
    for i, loc in enumerate(locations):
        if loc.get('id') == location_id:
            locations[i].update(updated_data)
            save_locations(locations)
            return True
    return False

def delete_location(location_id: str) -> bool:
    locations = load_locations()
    new_locations = [loc for loc in locations if loc.get('id') != location_id]
    if len(new_locations) == len(locations):
        return False  # لوکیشن پیدا نشد
    save_locations(new_locations)
    return True
