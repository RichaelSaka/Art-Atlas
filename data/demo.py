"""
Art Atlas - Technical Demo
Shows how the system works end-to-end with a small example.
"""

import requests
import json

API_KEY = "1a21c3e1-9d8b-4bba-96a5-79a8ffbb2bd2"
BASE_URL = "https://api.harvardartmuseums.org"

# ──────────────────────────────────────────────
# STEP 1: Fetch a small set of artworks
# ──────────────────────────────────────────────
print("=" * 60)
print("STEP 1: Fetching artworks from Harvard Art Museums API")
print("=" * 60)

resp = requests.get(f"{BASE_URL}/object", params={
    "apikey": API_KEY,
    "size": 5,
    "hasimage": 1,
    "classification": "Paintings",
    "fields": "id,title,dated,datebegin,people,medium,culture,places,colors,primaryimageurl",
})

objects = resp.json().get("records", [])
print(f"Fetched {len(objects)} paintings\n")

for obj in objects:
    artist = obj["people"][0]["name"] if obj.get("people") else "Unknown"
    print(f"  [{obj['id']}] {obj.get('title', 'Untitled')}")
    print(f"         Artist: {artist}")
    print(f"         Date:   {obj.get('dated', '?')}")
    print(f"         Medium: {obj.get('medium', '?')}")
    print(f"         Culture: {obj.get('culture', '?')}")
    print()

# ──────────────────────────────────────────────
# STEP 2: Build nodes (simplified records)
# ──────────────────────────────────────────────
print("=" * 60)
print("STEP 2: Building nodes")
print("=" * 60)

nodes = []
for obj in objects:
    node = {
        "id": str(obj["id"]),
        "title": obj.get("title", "Untitled"),
        "artist": obj["people"][0]["name"] if obj.get("people") else "Unknown",
        "date": obj.get("datebegin"),
        "medium": obj.get("medium", ""),
        "culture": obj.get("culture", ""),
        "places": [p.get("displayname", "") for p in (obj.get("places") or [])],
        "colors": [c.get("color", "") for c in (obj.get("colors") or [])],
    }
    nodes.append(node)

print(f"Created {len(nodes)} nodes\n")
print("Example node:")
print(json.dumps(nodes[0], indent=2))
print()

# ──────────────────────────────────────────────
# STEP 3: Compute edges with explanations
# ──────────────────────────────────────────────
print("=" * 60)
print("STEP 3: Computing explainable edges")
print("=" * 60)
print()

edges = []
for i, a in enumerate(nodes):
    for j, b in enumerate(nodes):
        if i >= j:
            continue

        reasons = []

        # Culture match
        if a["culture"] and a["culture"] == b["culture"]:
            reasons.append(f"Both from {a['culture']} culture")

        # Medium match
        if a["medium"] and b["medium"]:
            words_a = set(a["medium"].lower().split())
            words_b = set(b["medium"].lower().split())
            shared = words_a & words_b - {"on", "and", "with", "the", "a"}
            if len(shared) >= 2:
                reasons.append(f"Shared materials: {', '.join(shared)}")

        # Temporal proximity
        if a["date"] and b["date"]:
            gap = abs(a["date"] - b["date"])
            if gap == 0:
                reasons.append(f"Created the same year ({a['date']})")
            elif gap <= 10:
                reasons.append(f"Created {gap} years apart ({a['date']}, {b['date']})")

        # Color overlap
        shared_colors = set(a["colors"]) & set(b["colors"])
        if len(shared_colors) >= 2:
            reasons.append(f"Shared palette: {', '.join(list(shared_colors)[:3])}")

        # Geographic overlap
        shared_places = set(a["places"]) & set(b["places"])
        if shared_places:
            reasons.append(f"Connected to: {', '.join(shared_places)}")

        if reasons:
            edge = {
                "source": a["id"],
                "target": b["id"],
                "weight": round(len(reasons) / 5, 2),
                "explanation": reasons,
            }
            edges.append(edge)

            # Print the explanation
            print(f"  EDGE: \"{a['title']}\" <-> \"{b['title']}\"")
            print(f"  Weight: {edge['weight']}")
            for r in reasons:
                print(f"    - {r}")
            print()

if not edges:
    print("  No edges found in this small sample (try a larger fetch)")

# ──────────────────────────────────────────────
# STEP 4: Summary
# ──────────────────────────────────────────────
print("=" * 60)
print("STEP 4: Summary")
print("=" * 60)
print(f"""
  Nodes: {len(nodes)} artworks
  Edges: {len(edges)} connections

  Each edge carries an EXPLANATION — this is the core
  contribution of Art Atlas. Instead of just showing that
  two artworks are linked, we show WHY:

    - Shared materials (e.g., both oil on canvas)
    - Temporal proximity (created within 10 years)
    - Cultural origin (both from the same culture)
    - Color palette overlap
    - Geographic connections

  The frontend renders this as an interactive network
  where users click edges to see these explanations,
  enabling discovery without a fixed search query.
""")
