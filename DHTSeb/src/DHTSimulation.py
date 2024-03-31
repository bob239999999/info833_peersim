import simpy
import random
import matplotlib.pyplot as plt
import networkx as nx

from Message import Message
from Node import Node
from Network import Network 

use_advanced_routing = False  # Mettez à False pour désactiver le routage avancé


def find_closest_node(node_id, node_list):
    closest_node = None
    min_distance = float('inf')
    for node in node_list:
        distance = min(abs(node_id - node.node_id), len(node_list) - abs(node_id - node.node_id))
        if distance < min_distance:
            closest_node = node
            min_distance = distance
    return closest_node

def create_nodes(env, network, num_nodes):
    used_ids = set()
    for i in range(num_nodes):
        node_id = random.randint(1, 100)
        while node_id in used_ids:
            node_id = random.randint(1, 100)
        used_ids.add(node_id)
        # Passez use_advanced_routing comme argument à Node
        node = Node(env, node_id, advanced_routing=use_advanced_routing)
        node.join_ring(network)
        yield env.timeout(int(random.randint(1, 5)))
        print(f"Elapsed time: {env.now}")
        create_graph(network.nodes, f"create_nodes_{i}.png")  # Generate image after adding a node

    leaving_node = random.choice(network.nodes)
    leaving_node.leave_ring(network)
    yield env.timeout(1)
    create_graph(network.nodes, "leaving_node.png")  # Generate image after a node leaves

    new_node_id = random.randint(1, 100)
    while new_node_id in used_ids:
        new_node_id = random.randint(1, 100)

    # Find the closest node to the new node ID
    closest_node = find_closest_node(new_node_id, network.nodes)

    # Inform the closest node about the new node
    print("\n=== Un nouveau noeud s'ajoute dans l'anneau après le départ d'un autre noeud ===")
    print(f"Node {closest_node.node_id} received a JOIN request from Node {new_node_id}")

    # Inform neighbors of the closest node
    print(f"Node {closest_node.node_id } contacting neighbors {closest_node.left_neighbor.node_id} and {closest_node.right_neighbor.node_id}")
    left_closest_node = find_closest_node(closest_node.left_neighbor.node_id, network.nodes)
    right_closest_node = find_closest_node(closest_node.right_neighbor.node_id, network.nodes)

    print(f"Node {left_closest_node.node_id} and Node {right_closest_node.node_id} contacted")
    print(f"Node {left_closest_node.node_id} and Node {right_closest_node.node_id} comparing IDs...")
    # Choose the neighbor with the closest ID
    if abs(left_closest_node.node_id - new_node_id) < abs(right_closest_node.node_id - new_node_id):
        chosen_neighbor = left_closest_node
    else:
        chosen_neighbor = right_closest_node

    print(f"Node {chosen_neighbor.node_id} selected as closest neighbor")

    # Update neighbors of the chosen node
    new_node = Node(env, new_node_id)
    new_node.left_neighbor = chosen_neighbor
    new_node.right_neighbor = chosen_neighbor.right_neighbor
    chosen_neighbor.right_neighbor.left_neighbor = new_node
    chosen_neighbor.right_neighbor = new_node

    network.add_node(new_node)

    print(f"Node {new_node_id} joined the ring at time {env.now}")
    new_node.print_neighbors()
    new_node.print_ring(network)

    yield env.timeout(int(1))
    print(f"Elapsed time: {env.now}")
    network.nodes[0].print_ring(network)

    # Sending a hello message
    new_node.send_hello_message(network)

    create_graph(network.nodes, "join_ring.png")  # Generate image after a new node joins

def create_graph(listeNode, filename):
    G = nx.Graph()

    for node in listeNode:
        G.add_node(node.node_id, label=f"Node {node.node_id}\nLeft: {node.left_neighbor.node_id}\nRight: {node.right_neighbor.node_id}")

    for node in listeNode:
        G.add_edge(node.node_id, node.left_neighbor.node_id)
        G.add_edge(node.node_id, node.right_neighbor.node_id)

    pos = nx.kamada_kawai_layout(G)  # Compute Kamada-Kawai layout
    node_labels = nx.get_node_attributes(G, 'label')
    nx.draw(G, pos, with_labels=True, labels=node_labels)
    plt.savefig(filename)  # Save the graph to an image file
    plt.close()

if __name__ == "__main__":
    print("\n=== Début de la simulation DHT ===")

    env = simpy.Environment()
    network = Network()
    env.process(create_nodes(env, network, 8))  # S'assurer que cette opération ajoute des nœuds

    try:
        env.run(until=100)  # Exécute la simulation, ce qui inclut l'ajout de nœuds

        
        print("\n=== Début du Stockage des Données dans le Réseau DHT l'étape 3 ===")
        key = random.randint(1, 100)
        value = "DonnéeTest"
        responsible_node = network.find_responsible_node(key)
        if responsible_node:  # S'assurer qu'un nœud responsable a été trouvé
            responsible_node.put_data(key, value)

            # Test de récupération
            print(f"Récupération de la donnée pour la clé {key} : {responsible_node.get_data(key)}")
        
        # Après la création des nœuds, établissez des liens longs
        print("\n=== Routage l'étape 4 ===")
        print("\n=== Établissement des liens longs entre les nœuds (en trichant) ===")
        for node in network.nodes:
            node.establish_long_links(network.nodes)

        # Affichage des tables de routage uniquement si le routage avancé est activé
        if use_advanced_routing:
            print("\n=== Affichage des Tables de Routage ===")
            for node in network.nodes:
                node.display_routing_table()
        

        print("\n=== Fin de la simulation DHT ===")
        print(f"Nombre total de nœuds restants dans le réseau DHT : {len(network.nodes)}")

    except Exception as e:
        print(f"Une erreur est survenue pendant la simulation : {e}")


