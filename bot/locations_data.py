import json
import os

LOCATIONS_FILE = os.path.join(os.path.dirname(__file__), 'locations.json')

def load_locations():
    if not os.path.exists(LOCATIONS_FILE):
        return []
    with open(LOCATIONS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_locations(locations):
    with open(LOCATIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(locations, f, ensure_ascii=False, indent=2)

def get_location_by_id(location_id):
    locations = load_locations()
    for loc in locations:
        if loc['id'] == location_id:
            return loc
    return None

def add_location(location_data):
    locations = load_locations()
    locations.append(location_data)
    save_locations(locations)

def update_location(location_id, updated_data):
    locations = load_locations()
    for i, loc in enumerate(locations):
        if loc['id'] == location_id:
            locations[i].update(updated_data)
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

def search_locations(keyword):
    keyword_lower = keyword.lower()
    locations = load_locations()
    result = []
    for loc in locations:
        if (keyword_lower in loc.get('name', '').lower() or
            keyword_lower in loc.get('description', '').lower() or
            any(keyword_lower in kw.lower() for kw in loc.get('keywords', []))):
            result.append(loc)
    return result
