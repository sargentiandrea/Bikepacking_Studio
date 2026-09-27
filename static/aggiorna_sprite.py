import json
import os

sprite_path = r"C:\Users\sarge\Desktop\Bikepacking_Studio\static\sprite.json"

if not os.path.exists(sprite_path):
    print(f"Errore: Non trovo il file sprite.json in {sprite_path}")
    exit()

with open(sprite_path, 'r', encoding='utf-8') as f:
    sprite_data = json.load(f)

# Trova un'icona di riserva sicura
default_key = list(sprite_data.keys())[0] if sprite_data else None
default_props = sprite_data[default_key] if default_key else {"width": 16, "height": 16, "x": 0, "y": 0, "pixelRatio": 1}

def get_props(preferred_name):
    if preferred_name in sprite_data:
        return sprite_data[preferred_name]
    for key in sprite_data.keys():
        if preferred_name in key:
            return sprite_data[key]
    return default_props

# MAPPATURA MIRATA E DETTAGLIATA
mapping_rules = {
    # --- Ristorazione e Cibo ---
    "pub": "restaurant", "biergarten": "restaurant", "bar": "cafe", "fast_food": "restaurant", 
    "ice_cream": "cafe", "deli": "bakery", "confectionery": "bakery", "beverages": "restaurant", 
    "alcohol": "shop", "wine": "shop", "alcohol_shop": "shop", "food_court": "restaurant",
    "coffee": "cafe", "bakery": "bakery", "butcher": "shop", "greengrocer": "shop",
    
    # --- Salute e Medicina ---
    "doctors": "hospital", "dentist": "hospital", "veterinary": "hospital", "clinic": "hospital", 
    "pharmacy": "hospital", "chemist": "hospital", "nursing_home": "hospital", "hearing_aids": "hospital",
    
    # --- Scuola e Cultura ---
    "university": "school", "kindergarten": "school", "college": "school", 
    "educational_institution": "school", "library": "library", "books": "library",
    "arts_centre": "museum", "gallery": "museum", "theatre": "cinema", "cinema": "cinema",
    "museum": "museum", "artwork": "museum",
    
    # --- Trasporti e Mobilità ---
    "tram_stop": "bus_stop", "halt": "station", "subway": "station", "ferry_terminal": "harbor",
    "bus_station": "bus_stop", "taxi": "car", "car_rental": "car", "bicycle_rental": "bicycle",
    "charging_station": "fuel", "motorcycle_parking": "parking", "bicycle_parking": "parking",
    "subway_entrance": "station", "train_station_entrance": "station", "terminal": "station",
    "aeroway": "airfield", "aerodrome_label": "airfield", "aerialway": "aerialway",
    
    # --- Finanza e Istituzioni ---
    "atm": "bank", "financial": "bank", "financial_advisor": "bank", "accountant": "bank", 
    "insurance": "bank", "post_office": "post", "post_box": "post", "parcel_locker": "post",
    "community_centre": "townhall", "courthouse": "townhall", "police": "police", 
    "fire_station": "fire_station", "prison": "townhall", "embassy": "townhall", "government": "townhall",
    "social_facility": "hospital", "lawyer": "townhall", "tax_advisor": "bank",
    
    # --- Alloggi e Turismo ---
    "hostel": "hotel", "guest_house": "hotel", "chalet": "hotel", "motel": "hotel", 
    "lodging": "hotel", "dormitory": "hotel", "alpine_hut": "hotel", "caravan_site": "camp_site",
    "camp_site": "camp_site", "attraction": "viewpoint", "viewpoint": "viewpoint", "information": "information",
    
    # --- Sport e Attività ---
    "soccer": "pitch", "basketball": "pitch", "bowls": "pitch", "tennis": "pitch", "baseball": "pitch", 
    "shooting": "pitch", "athletics": "pitch", "paddle_tennis": "pitch", "table_tennis": "pitch", 
    "golf_course": "golf", "miniature_golf": "golf", "golf": "golf", "sports_centre": "pitch", 
    "swimming_pool": "swimming", "ice_rink": "pitch", "running": "pitch", "climbing": "pitch", 
    "archery": "pitch", "badminton": "pitch", "beachvolleyball": "pitch", "billiards": "pitch", 
    "bmx": "bicycle", "canoe": "boat", "cricket": "pitch", "curling": "pitch", "cycling": "bicycle", 
    "equestrian": "pitch", "free_flying": "airfield", "horse_racing": "pitch", "pitch": "pitch", 
    "playground": "playground", "stadium": "stadium", "park": "park", "dog_park": "park",
    
    # --- Negozi Specifici ---
    "shoes": "shop", "clothes": "shop", "bag": "shop", "second_hand": "shop", "perfumery": "shop", 
    "cosmetics": "shop", "tailor": "shop", "mall": "shop", "tobacco": "shop", "mobile_phone": "shop", 
    "optician": "shop", "florist": "shop", "tattoo": "shop", "furniture": "shop", "gift": "shop", 
    "copyshop": "shop", "sports": "shop", "computer": "shop", "travel_agency": "shop", "motorcycle": "shop", 
    "toys": "shop", "beauty": "shop", "fabric": "shop", "supermarket": "shop", "marketplace": "shop", 
    "car_parts": "shop", "car_repair": "shop", "hairdresser": "shop", "estate_agent": "shop", 
    "dry_cleaning": "shop", "hardware": "shop", "garden_centre": "shop", "interior_decoration": "shop", 
    "photo": "shop", "carpet": "shop", "massage": "shop", "erotic": "shop", "antiques": "shop", 
    "watches": "shop", "department_store": "shop", "electronics": "shop", "musical_instrument": "shop",
    "kiosk": "shop", "stationery": "shop", "newsagent": "shop", "convenience": "shop", "jewelry": "shop"
}

missing_items = [
    "tram_stop", "bus_stop", "university", "kindergarten", "community_centre", "townhall", "grave_yard", "books", "post_office", "parcel_locker",
    "post_box", "kiosk", "stationery", "shoes", "newsagent", "cosmetics", "convenience", "jewelry", "tailor", "mall",
    "tobacco", "mobile_phone", "hearing_aids", "optician", "florist", "tattoo", "furniture", "gift", "copyshop", "sports",
    "computer", "travel_agency", "motorcycle", "toys", "beauty", "fabric", "supermarket", "greengrocer", "marketplace", "deli",
    "clothes", "sports_centre", "shelter", "car_repair", "car_parts", "hairdresser", "charging_station", "butcher", "educational_institution", "estate_agent",
    "dry_cleaning", "hostel", "artwork", "arts_centre", "doctors", "moving_company", "company", "government", "insurance", "christian",
    "wine", "it", "political_party", "atm", "ngo", "parking", "hotel", "soccer", "religion", "brownfield",
    "energy_supplier", "gate", "pub", "biergarten", "hardware", "ticket", "recycling", "bollard", "basketball", "lift_gate",
    "waste_basket", "bicycle_parking", "bowls", "cycle_barrier", "pattinaggio", "motorcycle_parking", "swimming_pool", "tennis", "baseball",
    "shooting", "athletics", "ruins", "basketball;pickleball", "terminal", "toilets", "running", "taxi", "yes", "paddle_tennis",
    "multi", "courthouse", "chemist", "bed", "perfumery", "pet", "second_hand", "outdoor", "electronics", "confectionery", 
    "coffee", "garden_centre", "interior_decoration", "photo", "carpet", "massage", "erotic", "charity", "antiques", "watches",
    "department_store", "bag", "nightclub", "dormitory", "coworking", "financial", "lawyer", "escape_game", "guest_house", "logistics",
    "consulting", "employment_agency", "financial_advisor", "newspaper", "tax_advisor", "association", "union", "beverages", "security", "publisher",
    "jewish", "skateboard;roller_skating", "engineer", "telecommunication", "accountant", "musical_instrument", "yoga", "architect", "art", "office",
    "foundation", "alcohol", "board", "telephone", "table_tennis", "terminal;map", "basketball;tennis", "gallery", "caravan_site",
    "restaurant", "bar", "cafe", "fast_food", "pub", "ice_cream", "pharmacy", "hospital", "clinic", "school",
    "library", "books", "police", "fire_station", "bank",
    "fuel", "alpine_hut", "attraction", "viewpoint",
    "museum", "theatre", "cinema", "park", "playground", "pitch", "stadium", "bakery",
    "butcher", "subway", "station", "halt", "ferry_terminal", "place_of_worship",
    "lodging", "chalet", "motel", "dentist", "veterinary", "bus_station", "car_rental",
    "bicycle_rental", "flats", "house", "townhall", "courthouse", "prison",
    "embassy", "social_facility", "recycling", "telephone",
    "drinking_water", "shower", "bbq", "bench", "picnic_site", "viewpoint", "information","aeroway",
    "chemist", "castle", "biergarten", "aerodrome_label", "boundary", "park", "place",
    "aerialway", "station", "alcohol_shop", "alcohol", "aquarium", "archery",
    "gallery", "basin", "basketball", "badminton", "beachvolleyball", "biergarten", "bicycle",
    "billiards", "bmx", "bollard", "border_control", "camp_site", "caravan_site", "canoe", "car",
    "cemetery", "grave_yard", "climbing", "climbing_adventure", "clothes", "bag", "college", "cricket", "curling",
    "cycling", "dog_park", "subway_entrance", "train_station_entrance", "equestrian", "food_court", "free_flying",
    "gate", "golf_course", "miniature_golf", "golf", "greengrocer", "hackerspace",
    "marina", "dock", "horse_racing", "nursing_home", "ice_rink", "guidepost", "board", "map", "route_marker", "trail_blaze"
]

updated_count = 0
for item in missing_items:
    if item:
        target = mapping_rules.get(item)
        if not target:
            if "sport" in item or "ball" in item or "tennis" in item: target = "pitch"
            elif "shop" in item or "store" in item: target = "shop"
            elif "food" in item or "eat" in item: target = "restaurant"
            else: target = "shop"
            
        sprite_data[item] = dict(get_props(target))
        updated_count += 1

with open(sprite_path, 'w', encoding='utf-8') as f:
    json.dump(sprite_data, f, indent=2, ensure_ascii=False)

print(f"Fatto! Aggiornate correttamente {updated_count} categorie nel file sprite.json con le nuove icone mirate.")