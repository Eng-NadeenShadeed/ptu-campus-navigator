"""
Intelligent Campus Navigation Agent
Palestine Technical University - Kadoorie (PTU)
-----------------------------------------------------------------------------
AI Course - Individual Project
Student: Nadeen Monther Shadeed        Student ID: 202312411

The agent finds a route between places on the campus map using uninformed
search. Implemented algorithms:
    1. Breadth-First Search (BFS)
    2. Depth-First Search (DFS)
    3. Iterative Deepening Search (IDS)  (built on Depth-Limited Search, DLS)

Problem formulation
    State            : the agent's current location (a node of the campus graph)
    Initial state    : START (chosen per test)
    Actions          : "Go to X" for every location X directly connected to the
                       current location by a road/path
    Transition model : RESULT(s, "Go to X") = X
    Goal test        : state == GOAL
    Path cost        : sum of the (estimated) road distances in metres

NOTE: the distances below are ESTIMATES read from the campus map picture,
not surveyed measurements. Replace them with real values if you have them.

Run:
    python campus_agent.py            # full demo + tests
    python campus_agent.py --plot     # also saves PNG figures (needs matplotlib)
"""

import heapq
import sys
from collections import deque

# =============================================================================
# 1. STATE SPACE: the campus map as a weighted, undirected graph
# =============================================================================

# Building letters follow the legend on the official campus map.
DESCRIPTIONS = {
    "South_Gate":      "South Gate (University southern entrance)",
    "Main_Gate":       "Main Gate (University main entrance)",
    "NW_Roundabout":   "North-west roundabout",
    "Khadoorie_Rbt":   "Khadoorie roundabout (south-west)",
    "J_South":         "Road junction near building D (winding road starts)",
    "J_NE":            "Road junction near the stadium (north-east)",
    "J_Mid":           "Road junction near building E / mosque",
    "J_West":          "Junction on the west road near building B",
    "J_East":          "Junction on the east road near the east parking",
    "J_SE":            "Junction on the south road, east of the main gate",
    "A_Main":          "A - Main Building, Faculty of Economics & Business, Diploma College",
    "B_OldEng":        "B - Old Engineering College",
    "C_Sports":        "C - Sports Department",
    "F_ContEd":        "F - Continuing Education",
    "Bank":            "Bank (next to the south road)",
    "Cafeteria":       "Cafeteria (next to building E)",
    "D_Registration":  "D - Registration & Finance Building",
    "E_Sciences":      "E - Applied Sciences / Arts & Educational Sciences",
    "L_Graduate":      "L - Graduate Studies College",
    "G_Library":       "G - Library",
    "H_NewEng":        "H - New Engineering College",
    "S_Culture":       "S - Culture Building",
    "Stadium":         "University stadium",
    "Mosque":          "University mosque",
    "Parking_East":    "East parking lot",
    "Parking_Student": "Student parking",
}

# (place_1, place_2, estimated distance in metres). Roads are two-way.
EDGES = [
    # northern road
    ("NW_Roundabout", "South_Gate", 90),
    ("South_Gate", "J_South", 200),
    ("J_South", "D_Registration", 60),
    ("J_South", "J_NE", 120),
    ("J_South", "A_Main", 110),
    ("J_South", "J_Mid", 230),          # winding internal road
    # north-east zone
    ("J_NE", "Stadium", 80),
    ("J_NE", "G_Library", 140),
    ("G_Library", "H_NewEng", 70),
    ("G_Library", "S_Culture", 100),
    ("H_NewEng", "J_East", 130),
    ("J_NE", "J_East", 280),            # east vertical road
    # east zone
    ("J_East", "Parking_East", 70),
    ("J_East", "C_Sports", 150),
    ("J_East", "J_SE", 220),
    ("J_East", "J_Mid", 240),
    # southern road / main gate
    ("J_SE", "Main_Gate", 70),
    ("Main_Gate", "L_Graduate", 150),
    ("Main_Gate", "Parking_Student", 90),
    ("Main_Gate", "Khadoorie_Rbt", 320),
    ("Khadoorie_Rbt", "L_Graduate", 170),
    ("Khadoorie_Rbt", "Parking_Student", 90),
    # western road
    ("Khadoorie_Rbt", "J_West", 230),
    ("J_West", "NW_Roundabout", 240),
    ("J_West", "B_OldEng", 120),
    ("J_West", "J_Mid", 210),            # middle horizontal road
    # central zone
    ("J_West", "F_ContEd", 70),
    ("F_ContEd", "B_OldEng", 60),
    ("F_ContEd", "Mosque", 60),
    ("J_South", "Bank", 50),
    ("E_Sciences", "Cafeteria", 30),
    ("J_Mid", "A_Main", 90),
    ("J_Mid", "E_Sciences", 70),
    ("J_Mid", "Mosque", 80),
    ("J_Mid", "B_OldEng", 130),
    ("E_Sciences", "L_Graduate", 130),
    ("A_Main", "B_OldEng", 120),
]

# Approximate (x, y) positions used only for drawing the figures.
POSITIONS = {
    "NW_Roundabout": (145, 530), "South_Gate": (215, 530), "J_South": (420, 525),
    "D_Registration": (320, 480), "J_NE": (500, 530), "Stadium": (610, 570),
    "G_Library": (560, 490), "H_NewEng": (610, 380), "S_Culture": (730, 485),
    "Parking_East": (640, 310), "C_Sports": (610, 180), "J_East": (520, 280),
    "J_SE": (520, 75), "Main_Gate": (450, 60), "Khadoorie_Rbt": (145, 70),
    "Parking_Student": (330, 20), "L_Graduate": (290, 155), "E_Sciences": (435, 235),
    "J_Mid": (345, 305), "Mosque": (225, 230), "A_Main": (430, 370),
    "B_OldEng": (255, 360), "J_West": (140, 295), "F_ContEd": (190, 350), "Bank": (475, 485),
    "Cafeteria": (490, 205),
}


def build_graph(edges):
    """Turn the edge list into an adjacency list: {place: [(neighbour, cost), ...]}"""
    graph = {}
    for a, b, cost in edges:
        graph.setdefault(a, []).append((b, cost))
        graph.setdefault(b, []).append((a, cost))
    return graph


CAMPUS = build_graph(EDGES)


# =============================================================================
# 2. PROBLEM FORMULATION helpers
# =============================================================================

def successors(graph, state):
    """Successor function: returns (action, next_state, step_cost) triples."""
    return [(f"Go to {nxt}", nxt, cost) for nxt, cost in graph[state]]


def goal_test(state, goal):
    """Goal test: has the agent reached the destination?"""
    return state == goal


def path_cost(graph, path):
    """Path cost = sum of the road distances along the path (in metres)."""
    total = 0
    for a, b in zip(path, path[1:]):
        total += dict(graph[a])[b]
    return total


def make_result(name, found, path, graph, expanded, extra=None):
    """Bundle everything a search run produced into one dictionary."""
    return {
        "algorithm": name,
        "found": found,
        "path": path,
        "cost": path_cost(graph, path) if found else None,
        "hops": len(path) - 1 if found else None,
        "expanded": expanded,            # list of states in the order expanded
        "n_expanded": len(expanded),
        **(extra or {}),
    }


# =============================================================================
# 3. SEARCH ALGORITHMS (uninformed)
#    Convention used by all of them: the goal test is applied when a node is
#    taken out of the frontier to be expanded.
# =============================================================================

def bfs(graph, start, goal, verbose=False):
    """Breadth-First Search: FIFO queue; explores level by level."""
    frontier = deque([(start, [start])])       # queue of (state, path so far)
    in_frontier = {start}
    explored = set()
    expanded = []
    step = 0
    while frontier:
        state, path = frontier.popleft()       # FIFO -> shallowest node first
        in_frontier.discard(state)
        step += 1
        expanded.append(state)
        if verbose:
            print(f"  step {step:2d}: expand {state:<16} "
                  f"frontier after = {[s for s, _ in frontier]}")
        if goal_test(state, goal):
            return make_result("BFS", True, path, graph, expanded)
        explored.add(state)
        for _, nxt, _ in successors(graph, state):
            if nxt not in explored and nxt not in in_frontier:
                frontier.append((nxt, path + [nxt]))
                in_frontier.add(nxt)
    return make_result("BFS", False, [], graph, expanded)


def dfs(graph, start, goal, verbose=False):
    """Depth-First Search (graph version with an explored set): LIFO stack."""
    frontier = [(start, [start])]              # stack of (state, path so far)
    explored = set()
    expanded = []
    step = 0
    while frontier:
        state, path = frontier.pop()           # LIFO -> deepest node first
        if state in explored:
            continue                           # already expanded earlier
        step += 1
        expanded.append(state)
        if verbose:
            print(f"  step {step:2d}: expand {state:<16} "
                  f"stack size after pop = {len(frontier)}")
        if goal_test(state, goal):
            return make_result("DFS", True, path, graph, expanded)
        explored.add(state)
        # push in reverse so the FIRST neighbour in the list is expanded first
        for _, nxt, _ in reversed(successors(graph, state)):
            if nxt not in explored:
                frontier.append((nxt, path + [nxt]))
    return make_result("DFS", False, [], graph, expanded)


CUTOFF = "cutoff"


def _dls_recursive(graph, state, goal, limit, path, expanded):
    """Recursive DLS. Returns a path, CUTOFF, or None (no solution)."""
    expanded.append(state)
    if goal_test(state, goal):
        return path
    if limit == 0:
        return CUTOFF
    cutoff_occurred = False
    for _, nxt, _ in successors(graph, state):
        if nxt in path:                        # avoid loops along the current path
            continue
        result = _dls_recursive(graph, nxt, goal, limit - 1, path + [nxt], expanded)
        if result == CUTOFF:
            cutoff_occurred = True
        elif result is not None:
            return result
    return CUTOFF if cutoff_occurred else None


def dls(graph, start, goal, limit):
    """Depth-Limited Search: DFS that never goes deeper than `limit` moves."""
    expanded = []
    result = _dls_recursive(graph, start, goal, limit, [start], expanded)
    if result == CUTOFF or result is None:
        return make_result(f"DLS(l={limit})", False, [], graph, expanded,
                           {"cutoff": result == CUTOFF})
    return make_result(f"DLS(l={limit})", True, result, graph, expanded)


def ids(graph, start, goal, max_depth=None, verbose=False):
    """Iterative Deepening Search: run DLS with limit 0, 1, 2, ... until solved."""
    max_depth = max_depth if max_depth is not None else len(graph)
    all_expanded = []
    iterations = []                            # (limit, states expanded in that iteration)
    for limit in range(max_depth + 1):
        res = dls(graph, start, goal, limit)
        all_expanded.extend(res["expanded"])
        iterations.append((limit, res["expanded"]))
        if verbose:
            status = "SOLVED" if res["found"] else "cutoff"
            print(f"  limit {limit}: expanded {res['n_expanded']:4d} nodes -> {status}")
        if res["found"]:
            return make_result("IDS", True, res["path"], graph, all_expanded,
                               {"final_limit": limit, "iterations": iterations})
        if not res.get("cutoff"):              # no cutoff -> no solution exists
            break
    return make_result("IDS", False, [], graph, all_expanded,
                       {"iterations": iterations})


# -----------------------------------------------------------------------------
# Reference only (NOT one of the required algorithms): Dijkstra gives the
# cheapest route so we can check whether BFS/DFS/IDS happened to be cheapest.
# -----------------------------------------------------------------------------
def cheapest_cost_reference(graph, start, goal):
    best = {start: 0}
    heap = [(0, start, [start])]
    while heap:
        cost, state, path = heapq.heappop(heap)
        if state == goal:
            return cost, path
        if cost > best.get(state, float("inf")):
            continue
        for nxt, c in graph[state]:
            new = cost + c
            if new < best.get(nxt, float("inf")):
                best[nxt] = new
                heapq.heappush(heap, (new, nxt, path + [nxt]))
    return None, []


# =============================================================================
# 4. OUTPUT / TESTING
# =============================================================================

def print_result(res):
    print(f"\n[{res['algorithm']}]")
    if "iterations" in res:                    # IDS: show every iteration in full
        print(f"  Expanded {res['n_expanded']} states in total "
              f"(repeated visits are counted):")
        for limit, states in res["iterations"]:
            print(f"    limit {limit}: {' -> '.join(states)}")
    else:                                      # BFS / DFS: one expansion order
        print(f"  Expansion order ({res['n_expanded']} states): "
              f"{' -> '.join(res['expanded'])}")
    if res["found"]:
        print(f"  Solution path : {' -> '.join(res['path'])}")
        print(f"  Moves (hops)  : {res['hops']}")
        print(f"  Path cost     : {res['cost']} m")
    else:
        print("  No solution found.")


def run_scenario(title, start, goal, verbose=False):
    """Run BFS, DFS and IDS on one start/goal pair and print everything."""
    print("\n" + "=" * 78)
    print(f"SCENARIO: {title}")
    print(f"  Start = {start}   Goal = {goal}")
    print("=" * 78)

    results = []
    for name, fn in (("BFS", bfs), ("DFS", dfs), ("IDS", ids)):
        if verbose:
            print(f"\n--- {name} trace ---")
            res = fn(CAMPUS, start, goal, verbose=True)
        else:
            res = fn(CAMPUS, start, goal)
        print_result(res)
        results.append(res)

    ref_cost, ref_path = cheapest_cost_reference(CAMPUS, start, goal)
    print(f"\n  (Reference) cheapest possible route = {ref_cost} m: "
          f"{' -> '.join(ref_path)}")

    # comparison table
    print("\n  Comparison")
    print(f"  {'Algorithm':<10}{'Found':<7}{'Hops':<6}{'Cost (m)':<10}"
          f"{'Expanded':<10}{'Cheapest?'}")
    for r in results:
        cheapest = "yes" if r["cost"] == ref_cost else "NO"
        print(f"  {r['algorithm']:<10}{str(r['found']):<7}{r['hops']!s:<6}"
              f"{r['cost']!s:<10}{r['n_expanded']:<10}{cheapest}")
    return results, (ref_cost, ref_path)


TEST_SCENARIOS = [
    ("1. From the South Gate to the Library",            "South_Gate",      "G_Library"),
    ("2. From the Main Gate to Registration (D)",        "Main_Gate",       "D_Registration"),
    ("3. From student parking to the Stadium",           "Parking_Student", "Stadium"),
    ("4. From the Mosque to the Culture Building (S)",   "Mosque",          "S_Culture"),
    ("5. From Old Engineering (B) to the East parking",  "B_OldEng",        "Parking_East"),
    ("6. From Continuing Education (F) to the Cafeteria", "F_ContEd",       "Cafeteria"),
]


# =============================================================================
# 5. OPTIONAL FIGURES (matplotlib)
# =============================================================================

def draw_graph(path=None, title="Campus state-space graph", filename="campus_graph.png",
               start=None, goal=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(11, 8))
    # edges + cost labels
    for a, b, cost in EDGES:
        (x1, y1), (x2, y2) = POSITIONS[a], POSITIONS[b]
        ax.plot([x1, x2], [y1, y2], color="#b0b0b0", lw=1.5, zorder=1)
        ax.text((x1 + x2) / 2, (y1 + y2) / 2, str(cost), fontsize=7,
                color="#555", ha="center", va="center",
                bbox=dict(fc="white", ec="none", pad=0.6, alpha=0.85), zorder=2)
    # highlighted path
    if path:
        for a, b in zip(path, path[1:]):
            (x1, y1), (x2, y2) = POSITIONS[a], POSITIONS[b]
            ax.plot([x1, x2], [y1, y2], color="#d62728", lw=4, zorder=3)
    # nodes
    for node, (x, y) in POSITIONS.items():
        is_junction = node.startswith(("J_", "NW_", "Khadoorie")) or node.endswith("Gate")
        color = "#9ecae1" if is_junction else "#fdd49e"
        if node == start:
            color = "#74c476"
        if node == goal:
            color = "#fb6a4a"
        ax.scatter(x, y, s=420, color=color, edgecolor="black", zorder=4)
        ax.text(x, y - 28, node, fontsize=8, ha="center", va="top", zorder=5)
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.set_aspect("equal")
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(filename, dpi=160)
    plt.close(fig)
    print(f"saved {filename}")


def make_figures(outdir="."):
    draw_graph(title="Campus state-space graph (edge labels = estimated metres)",
               filename=f"{outdir}/campus_graph.png")
    s, g = "Main_Gate", "D_Registration"
    for name, fn in (("bfs", bfs), ("dfs", dfs), ("ids", ids)):
        r = fn(CAMPUS, s, g)
        draw_graph(r["path"], f"{r['algorithm']} route {s} -> {g}  "
                   f"(cost {r['cost']} m, {r['n_expanded']} expanded)",
                   f"{outdir}/path_{name}.png", s, g)


# =============================================================================
# 6. MAIN
# =============================================================================

if __name__ == "__main__":
    print("INTELLIGENT CAMPUS NAVIGATION AGENT - PTU Kadoorie")
    print(f"State space: {len(CAMPUS)} locations, {len(EDGES)} two-way roads")

    # Detailed step-by-step trace for the first scenario (shows the search process)
    run_scenario(TEST_SCENARIOS[0][0], TEST_SCENARIOS[0][1], TEST_SCENARIOS[0][2],
                 verbose=True)

    # Remaining scenarios: concise output
    for title, s, g in TEST_SCENARIOS[1:]:
        run_scenario(title, s, g)

    if "--plot" in sys.argv:
        make_figures()