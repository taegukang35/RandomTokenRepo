import matplotlib.pyplot as plt
import networkx as nx
from functools import lru_cache

def check_lose(state):
    return sum(state) == 1

def normalize(state):
    return tuple(sorted([s for s in state if s > 0]))

root = normalize(tuple(map(int, input("type init state (e.g. 1 3 4 4): ").split())))

G = nx.DiGraph()
state_ids = {}
counter = [0]
tree_levels = {}

def get_state_id(state):
    state = normalize(state)
    if state not in state_ids:
        state_ids[state] = f"S{counter[0]}"
        counter[0] += 1
    return state_ids[state]

# Minimax expl + construct graph
@lru_cache(maxsize=None)
def minimax(state, is_maximizing, depth=0):
    state = normalize(state)
    state_id = get_state_id(state)
    tree_levels[state_id] = depth

    # node color based on player
    if check_lose(state):
        G.add_node(state_id, label=str(state), color='red')
        return not is_maximizing

    G.add_node(state_id, label=str(state),
               color='lightblue' if is_maximizing else 'lightgreen')

    # child nodes 
    if is_maximizing:
        for i in range(len(state)):
            for r in range(1, state[i] + 1):
                new_state = list(state)
                new_state[i] -= r
                new_state_t = normalize(tuple(new_state))
                child_id = get_state_id(new_state_t)
                G.add_edge(state_id, child_id, label=f"{state[i]}-{r}")
                if minimax(new_state_t, False, depth+1):
                    return True
        return False
    else:
        for i in range(len(state)):
            for r in range(1, state[i] + 1):
                new_state = list(state)
                new_state[i] -= r
                new_state_t = normalize(tuple(new_state))
                child_id = get_state_id(new_state_t)
                G.add_edge(state_id, child_id, label=f"{state[i]}-{r}")
                if not minimax(new_state_t, True, depth+1):
                    return False
        return True

print("P1 wins" if minimax(root, True) else "P2 wins")

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
filename = f"reverse_nim_tree_{'-'.join(map(str, root))}.png"

plt.figure(figsize=(18, 12))
nx.draw(G, pos, labels=labels, with_labels=True,
        node_size=1200, node_color=node_colors, font_size=10)
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
plt.title("Extensive Form Tree of Reverse Nim Game")
plt.axis('off')
plt.savefig(filename, dpi=300, bbox_inches='tight')
print("Saved ", filename)