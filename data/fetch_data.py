import requests
import json
import time

API_KEY = "1a21c3e1-9d8b-4bba-96a5-79a8ffbb2bd2"
BASE_URL = "https://api.harvardartmuseums.org"

def fetch_objects(total=500):
    """Fetch artwork records from the Harvard Art Museums API."""
    objects = []
    page = 1
    per_page = 100

    while len(objects) < total:
        print(f"Fetching page {page}...")
        resp = requests.get(f"{BASE_URL}/object", params={
            "apikey": API_KEY,
            "size": per_page,
            "page": page,
            "hasimage": 1,
            "fields": "id,title,dated,datebegin,people,medium,classification,culture,places,primaryimageurl,colors,techniques",
        })

        if resp.status_code != 200:
            print(f"Error: {resp.status_code} - {resp.text}")
            break

        data = resp.json()
        records = data.get("records", [])
        objects.extend(records)
        print(f"  Got {len(records)} records (total so far: {len(objects)})")

        if not data["info"].get("next"):
            break

        page += 1
        time.sleep(0.5)

    return objects[:total]


def build_nodes(objects):
    """Convert raw API records into simplified nodes."""
    nodes = []
    for obj in objects:
        artist = ""
        if obj.get("people"):
            artist = obj["people"][0].get("name", "")

        nodes.append({
            "id": str(obj["id"]),
            "title": obj.get("title", "Untitled"),
            "artist": artist,
            "date": obj.get("datebegin"),
            "medium": obj.get("medium", ""),
            "classification": obj.get("classification", ""),
            "culture": obj.get("culture", ""),
            "places": [p.get("displayname", "") for p in (obj.get("places") or [])],
            "colors": [c.get("color", "") for c in (obj.get("colors") or [])],
            "image_url": obj.get("primaryimageurl", ""),
        })
    return nodes


def build_edges(nodes):
    """Compute edges based on shared attributes."""
    edges = []
    for i, a in enumerate(nodes):
        for j, b in enumerate(nodes):
            if i >= j:
                continue

            reasons = []

            if a["culture"] and a["culture"] == b["culture"]:
                reasons.append(f"Both from {a['culture']} culture")

            if a["medium"] and b["medium"] and a["medium"] == b["medium"]:
                reasons.append(f"Same medium: {a['medium']}")

            if a["classification"] and a["classification"] == b["classification"]:
                reasons.append(f"Both classified as {a['classification']}")

            shared_colors = set(a["colors"]) & set(b["colors"])
            if len(shared_colors) >= 2:
                reasons.append(f"Shared colors: {', '.join(list(shared_colors)[:3])}")

            if a["date"] and b["date"] and abs(a["date"] - b["date"]) <= 10:
                reasons.append(f"Created within 10 years ({a['date']}, {b['date']})")

            shared_places = set(a["places"]) & set(b["places"])
            if shared_places:
                reasons.append(f"Shared places: {', '.join(list(shared_places)[:2])}")

            if len(reasons) >= 5:
                edges.append({
                    "source": a["id"],
                    "target": b["id"],
                    "weight": round(len(reasons) / 6, 2),
                    "reasons": reasons,
                    "explanation": "; ".join(reasons),
                })

        if i % 50 == 0 and i > 0:
            print(f"Processed edges for {i}/{len(nodes)} nodes...")

    return edges


if __name__ == "__main__":
    print("Fetching objects from Harvard Art Museums API...")
    objects = fetch_objects(500)
    print(f"\nFetched {len(objects)} objects total")

    print("\nBuilding nodes...")
    nodes = build_nodes(objects)

    print("Building edges...")
    edges = build_edges(nodes)
    print(f"Generated {len(edges)} edges")

    with open("nodes.json", "w", encoding="utf-8") as f:
        json.dump(nodes, f, indent=2, ensure_ascii=False)

    with open("edges.json", "w", encoding="utf-8") as f:
        json.dump(edges, f, indent=2, ensure_ascii=False)

    print(f"\nDone! Saved {len(nodes)} nodes and {len(edges)} edges")
