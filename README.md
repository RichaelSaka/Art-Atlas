# Art Atlas
## Interactive Networks for Collections Exploration and Art Discovery

### Research Question
How can tailored node-link visualization designs improve users' interpretation of art historical relationships, beyond simply conveying connectivity?

### What We've Built So Far

**Data Pipeline (work in progress)**
- Python script that fetches 500 artwork records from the Harvard Art Museums REST API
- Transforms raw API records into structured nodes (title, artist, date, medium, culture, places, colors, image)
- Computes edges by comparing every pair of artworks across 6 relationship dimensions
- Outputs `nodes.json` (500 nodes) and `edges.json` (~1,420 edges) for the frontend

**Multi-Relational Network Visualization (complete)**
- Interactive force-directed graph built with D3.js
- Nodes represent artworks, edges represent multi-dimensional relationships
- Edges are color-coded by relationship type:
  - Red = shared culture
  - Blue = shared medium
  - Cyan = same classification
  - Teal = overlapping color palette
  - Orange = temporal proximity (within 10 years)
  - Purple = shared geographic places
- Toggle buttons to show/hide each edge type independently
- Click any node to see artwork details + image in a side panel
- Click any edge to see an explanation of **why** two artworks are connected
- Zoom, pan, and drag to explore the network

### Data Source
Harvard Art Museums REST API (`https://api.harvardartmuseums.org`)
- JSON responses, paginated (max 100/page)
- Fields used: title, date, medium, culture, places, colors, images, classification
- Images served via IIIF (International Image Interoperability Framework)
- Rate limit: 2,500 requests/day

### Relationship Dimensions

| Dimension      | What it captures              | How it's computed                        |
|----------------|-------------------------------|------------------------------------------|
| Temporal       | Proximity in time             | Works created within 10 years            |
| Material       | Shared medium/technique       | Exact match on medium field              |
| Cultural       | Same culture of origin        | Direct match on culture field            |
| Geographic     | Shared associated places      | Overlap in places array                  |
| Visual         | Color palette similarity      | 2+ shared dominant colors                |
| Classification | Same artwork type             | Match on classification field            |

Edges require at least 5 matching dimensions to keep the graph readable (~1,420 edges for 500 nodes).

### Visualization Approaches (planned)
We will implement and compare four tailored designs plus a baseline:

| Variant           | Status      | Description |
|-------------------|-------------|-------------|
| Baseline          | Complete    | Standard force-directed graph, no special encoding |
| Multi-Relational  | Complete    | Color-coded edges with toggle filters per dimension |
| Temporal          | Planned     | Nodes positioned along a time axis |
| Geographic        | Planned     | Nodes placed on a map by associated places |
| Narrative         | Planned     | Guided step-by-step path through the network |

### Evaluation Plan
- **Study type:** Empirical user study (within-subjects)
- **Participants:** Harvard students / Cambridge-area residents
- **Why Harvard data:** Participants have personal familiarity with the collection
- **Measures:** Interpretation accuracy, discovery rate, confidence, preference

### Tech Stack
- **Data processing:** Python 3 + requests library
- **Frontend:** D3.js v7
- **Data format:** Static JSON (nodes + edges)
- **Image delivery:** IIIF via Harvard Art Museums

### Project Structure
```
ArtAtlas/
├── README.md
├── data/
│   ├── fetch_data.py       # Fetches and processes API data
│   ├── demo.py             # Technical demo script
│   ├── nodes.json          # Generated artwork nodes
│   └── edges.json          # Generated relationship edges
└── vis/
    └── index.html          # D3.js network visualization
```

### How to Run
```bash
# 1. Install dependencies
python -m pip install requests

# 2. Fetch data (generates nodes.json and edges.json)
cd ArtAtlas/data
python fetch_data.py

# 3. Start local server (from project root)
cd ArtAtlas
python -m http.server 8000

# 4. Open in browser
# http://localhost:8000/vis/
```
