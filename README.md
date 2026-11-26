# Intelligent Campus Navigation Agent – PTU Kadoorie
**AI course – Individual project (Uninformed search)** · مشروع فردي – مساق الذكاء الاصطناعي

Live site / الموقع المباشر: LIVE_LINK_HERE

An agent that finds routes between buildings of Palestine Technical University – Kadoorie using **BFS, DFS and IDS** over a weighted campus graph (26 places, 37 roads; distances are estimates read from the campus map).

## Project structure
| File | Purpose |
|---|---|
| `campus_agent.py` | The required Python program: graph, BFS/DFS/DLS/IDS, printed search trace, 6 test scenarios, comparison |
| `index.html` | The website (Arabic / English) |
| `css/style.css` | Design, hero, map, responsive layout |
| `js/data.js` | Graph data: nodes, edges, costs, map positions, names |
| `js/algorithms.js` | BFS, DFS, IDS in JavaScript (same logic as the Python file) + Dijkstra reference |
| `js/app.js` | Interface: map, controls, step-by-step animation, comparison table |
| `assets/` | Campus photo, official map, university logo |

## Run
- Python: `python campus_agent.py` (add `--plot` to save figures; needs matplotlib)
- Website: open `index.html` in a browser (no build step), or visit the live link.

Note: BFS minimises the number of moves, not metres; Dijkstra appears only as a check and is not one of the project algorithms.
