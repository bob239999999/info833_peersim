import simpy
import random
import matplotlib.pyplot as plt
import networkx as nx

from Message import Message
from Node import Node
from Network import Network 
from Fallible import Fallible

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
        node = Node(env, node_id)
        node.join_ring(network)
        yield env.timeout(int(random.randint(1, 5)))
        print(f"Elapsed time: {env.now}")

    leaving_node = random.choice(network.nodes)
    leaving_node.leave_ring(network)
    yield env.timeout(1)

    new_node_id = random.randint(1, 100)
    while new_node_id in used_ids:
        new_node_id = random.randint(1, 100)

    # Find the closest node to the new node ID
    closest_node = find_closest_node(new_node_id, network.nodes)

    # Inform the closest node about the new node
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

def create_graph(listeNode):
    G = nx.Graph()

    for node in listeNode:
        G.add_node(node.node_id, label=f"Node {node.node_id}\nLeft: {node.left_neighbor.node_id}\nRight: {node.right_neighbor.node_id}")

    for node in listeNode:
        G.add_edge(node.node_id, node.left_neighbor.node_id)
        G.add_edge(node.node_id, node.right_neighbor.node_id)

    pos = nx.spring_layout(G)  # Compute layout for better visualization
    node_labels = nx.get_node_attributes(G, 'label')
    nx.draw(G, pos, with_labels=True, labels=node_labels)
    plt.show()

def simulate_failures(network):
    # Choisissez aléatoirement certains nœuds et attribuez-leur l'état DEAD
    num_failures = random.randint(1, len(network.nodes) // 2)  # Simulez jusqu'à la moitié des nœuds échoués
    print(f"There is {num_failures} node failures")
    failed_nodes = random.sample(network.nodes, num_failures)
    for node in failed_nodes:
        node.setfailstate(Fallible.DEAD)

if __name__ == "__main__":
    env = simpy.Environment()
    network = Network()
    env.process(create_nodes(env, network, 5))
    try:
        env.run(until=100)  # Exécuter la simulation jusqu'à un certain temps (100 dans cet exemple)
        simulate_failures(network)
        create_graph(network.nodes)

         # Sending messages between nodes to fill inboxes
        for node in network.nodes:
            if node.right_neighbor:  # Ensure the node has a right neighbor
                recipient_node = random.choice(network.nodes)
                message = Message(node, recipient=recipient_node, message_type='HELLO')
                node.send(message)

    except Exception as e:
        print(f"An error occurred during the simulation: ")








