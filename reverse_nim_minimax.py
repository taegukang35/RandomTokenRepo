import matplotlib.pyplot as plt
import networkx as nx
from functools import lru_cache

def check_lose(state, early_exit=False):
    if early_exit:
        if len(state) == 3:
            if state[0] == 1 and state[1] == 1 and state[2] == 1:
                return True # (1, 1, 1)
            if state[0] == 1 and state[1] > 1 and (state[1] % 2 == 0 and state[2] == state[1] + 1):
                return True # (1, 2n, 2n+1)
        if len(state) == 2:
            if state[0] > 1 and (state[0] == state[1]):
                return True # (n, n)
    return sum(state) == 1 # (1, )

def normalize(state):
    return tuple(sorted([s for s in state if s > 0]))

root = normalize(tuple(map(int, input("type init state (e.g. 1 3 5): ").split())))

G = nx.DiGraph()
tree_levels = {}
node_counter = [0]
win_cache = {}  # (state, is_max) → bool (True if winning for current player)
optimal_edges = set()


def get_state_id(state, depth):
    node_id = f"S{node_counter[0]}"
    node_counter[0] += 1
    tree_levels[node_id] = depth
    return node_id

@lru_cache(maxsize=None)
def minimax(state, is_maximizing, depth=0):
    state = normalize(state)
    state_id = get_state_id(state, depth)

    if check_lose(state):
        G.add_node(state_id, label=str(state), color='red')
        win_cache[(state, is_maximizing)] = not is_maximizing
        return state_id

    G.add_node(state_id, label=str(state),
               color='lightblue' if is_maximizing else 'lightgreen')

    children = []
    outcomes = []
    if len(state) == 1:
        for r in range(1, state[0]):
            new_state = list(state)
            new_state[0] -= r
            new_state_t = normalize(tuple(new_state))
            child_id = minimax(new_state_t, not is_maximizing, depth + 1)
            G.add_edge(state_id, child_id, label=f"{state[0]}-{r}")
            children.append((new_state_t, child_id))
            outcomes.append(win_cache[(new_state_t, not is_maximizing)])
    else:
        for i in range(len(state)):
            for r in range(1, state[i] + 1):
                new_state = list(state)
                new_state[i] -= r
                new_state_t = normalize(tuple(new_state))
                child_id = minimax(new_state_t, not is_maximizing, depth + 1)
                G.add_edge(state_id, child_id, label=f"{state[i]}-{r}")
                children.append((new_state_t, child_id))
                outcomes.append(win_cache[(new_state_t, not is_maximizing)])

    # minimax 결정
    if is_maximizing:
        result = any(outcomes)
    else:
        result = all(outcomes)

    win_cache[(state, is_maximizing)] = result

    # 최적 경로 edge 저장
    for (child_state, child_id), win in zip(children, outcomes):
        if is_maximizing and win == True:
            optimal_edges.add((state_id, child_id))
        elif not is_maximizing and win == False:
            optimal_edges.add((state_id, child_id))

    return state_id

root_id = minimax(root, True)
p1_wins = win_cache[(root, True)]
print("P1 wins" if p1_wins else "P2 wins")

pos = {}
layer_counts = {}

for node, level in tree_levels.items():
    if level not in layer_counts:
        layer_counts[level] = 0
    pos[node] = (layer_counts[level], -level)
    layer_counts[level] += 1

node_colors = [G.nodes[n]['color'] for n in G.nodes]
labels = nx.get_node_attributes(G, 'label')
edge_labels = nx.get_edge_attributes(G, 'label')

# visualize the graph
default_edges = [(u, v) for u, v in G.edges if (u, v) not in optimal_edges]
optimal_edges_list = list(optimal_edges)

plt.figure(figsize=(18, 12))
nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=1200)
nx.draw_networkx_labels(G, pos, labels=labels, font_size=10)
nx.draw_networkx_edges(G, pos, edgelist=default_edges, edge_color='gray')
nx.draw_networkx_edges(G, pos, edgelist=optimal_edges_list, edge_color='black', width=3)
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
plt.title("Reverse Nim Game Tree (Minimax Path Highlighted)")
plt.axis('off')

filename = f"reverse_nim_minimax_path_{'-'.join(map(str, root))}" + ".png"
plt.savefig(filename, dpi=300, bbox_inches='tight')
print("Saved", filename)
