import json
import os

LOCATIONS_FILE = "bot/locations/locations.json"

def load_locations():
    if not os.path.exists(LOCATIONS_FILE):
        return []
    with open(LOCATIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_locations(locations):
    with open(LOCATIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(locations, f, ensure_ascii=False, indent=2)

def get_location_by_id(location_id):
    locations = load_locations()
    for loc in locations:
        if loc['id'] == location_id:
            return loc
    return None

def add_location(new_location):
    locations = load_locations()
    if any(loc['id'] == new_location['id'] for loc in locations):
        return False
    locations.append(new_location)
    save_locations(locations)
    return True

def update_location(location_id, updated_data):
    locations = load_locations()
    for idx, loc in enumerate(locations):
        if loc['id'] == location_id:
            locations[idx].update(updated_data)
            save_locations(locations)
            return True
    return False

def delete_location(location_id):
    locations = load_locations()
    new_locations = [loc for loc in locations if loc['id'] != location_id]
    if len(new_locations) == len(locations):
        return False
    save_locations(new_locations)
    return True
