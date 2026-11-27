# Intelligent Campus Navigation Agent – PTU Kadoorie
 
**Palestine Technical University – Kadoorie · Artificial Intelligence course · Individual project (Using AI Search Techniques)**
 
| | |
|---|---|
| 🌐 **Live website** | https://eng-nadeenshadeed.github.io/ptu-campus-navigator/ |
| 💻 **Source code** | https://github.com/Eng-NadeenShadeed/ptu-campus-navigator |
| 📄 **Project report (PDF)** | [`Project_Report.pdf`](Project_Report.pdf) |
| 👩‍🎓 **Student** | Nadeen Monther Shadeed  |
 

 
## What is this project?
 
A smart guide for the university campus. The user chooses **where they are** and **where they want to go**, and an **intelligent agent** finds a route over the campus road network using **uninformed search algorithms**: **BFS**, **DFS** and **IDS** (built on DLS). The website lets you watch the search happen step by step on the official campus map, in **Arabic or English**.
 

## Features
 
- Interactive official campus map: click buildings to set the start and the goal, or use the lists.
- Three algorithms: BFS, DFS and IDS, with **Run search**, **Next step** (one expansion per click) and **Reset**.
- Live status line, the frontier, the expansion order, the final route with distance for every road, and walking time.
- Six ready-made test trips and a comparison table of the three algorithms for the selected trip.
- Arabic / English switch (RTL / LTR), responsive layout, dark-mode friendly.
- A command-line Python program with a readable search trace (the required course deliverable).
## How it works
 
**State space.** The map is a weighted undirected graph: **26 places** (buildings, gates, roundabouts, parking lots, road junctions) and **37 roads**. Road lengths are in metres.
 
| Problem component | Definition |
|---|---|
| State | The agent's current place |
| Initial state | The chosen start |
| Actions | `Go to X` for every place X connected by a road |
| Transition model | `RESULT(s, Go to X) = X` |
| Goal test | `state == GOAL` (applied when a node is expanded) |
| Path cost | Sum of the road distances in metres |
 
**PEAS.** *Performance:* valid route, short distance, few expanded states. *Environment:* the campus road network. *Actuators:* move to a neighbouring place. *Sensors:* current place and its connections. **Agent type:** goal-based. **Environment:** fully observable, single-agent, deterministic, sequential, static, discrete, known.
 
**Algorithms.**
- **BFS**: FIFO queue; finds the route with the *fewest moves*.
- **DFS**: LIFO stack with an explored set; fast to start, but the route can be long.
- **IDS**: repeated depth-limited searches (limits 0, 1, 2, …); fewest moves with small memory, at the price of repeated expansions.
> Fewest moves is not the same as fewest metres when roads have different lengths, so BFS and IDS are **not claimed to be cost-optimal** here. Dijkstra is used **only** as a reference check and is not one of the project algorithms.
 
## Test results (6 scenarios)
 
Path cost in metres (number of expanded states in brackets). *Cheapest* is the Dijkstra reference.
 
| # | Trip | Cheapest | BFS | DFS | IDS |
|---|---|---|---|---|---|
| 1 | South Gate → Library | 460 | 460 (14) | 1370 (9) | 460 (25) |
| 2 | Main Gate → Registration (D) | 610 | 750 (25) | 810 (21) | 750 (124) |
| 3 | Student Parking → Stadium | 740 | 740 (23) | 800 (23) | 740 (96) |
| 4 | Mosque → Culture Bldg (S) | 620 | 670 (26) | 1270 (23) | 670 (247) |
| 5 | Old Engineering (B) → East Parking | 440 | 440 (20) | 1030 (24) | 440 (59) |
| 6 | Continuing Ed. (F) → Cafeteria | 240 | 380 (23) | 1670 (17) | 380 (101) |
 
BFS and IDS gave the cheapest route in 3 of 6 trips; DFS in none. IDS always expanded the most states because it repeats shallow levels. The full discussion is in the report.
 
## Project structure
 
```
ptu-campus-navigator/
├── index.html            # the website (Arabic / English)
├── campus_agent.py       # Python program: graph, BFS, DFS, DLS, IDS, 6 tests, comparison
├── css/style.css         # design: hero, map, panel, responsive layout, theme colours
├── js/
│   ├── data.js           # graph data: places, roads, costs, map positions, names (AR / EN)
│   ├── algorithms.js     # BFS, DFS, IDS (same logic as the Python file) + Dijkstra reference
│   └── app.js            # interface: map, controls, step-by-step animation, comparison table
├── assets/               # campus photo, official map, university logo, screenshots
├── docs/Project_Report.pdf
└── README.md
```
 
## Run it
 
**Python (Python 3, standard library only):**
 
```bash
python campus_agent.py          # full demo: trace + six tests + comparison
python campus_agent.py --plot   # also saves figures (needs matplotlib)
```
 
**Website:** open `index.html` in a browser (no build step), or visit https://eng-nadeenshadeed.github.io/ptu-campus-navigator/
 
**Deploy on GitHub Pages:** *Settings → Pages → Deploy from a branch → `main` → `/ (root)`*.
 
## Limitations
 
- Distances are **estimates read from the campus map picture**, not surveyed measurements.
- The model is static: closed roads, crowds, stairs and accessibility are not modelled.
