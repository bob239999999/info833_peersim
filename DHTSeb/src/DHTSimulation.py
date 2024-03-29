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

def simulate_failures(network):
    # Choose randomly some nodes and set their state to DEAD
    num_failures = random.randint(1, len(network.nodes) // 2)  # Simulate up to half of the nodes failed
    print(f"There are {num_failures} node failures")
    failed_nodes = random.sample(network.nodes, num_failures)
    for node in failed_nodes:
        node.failstate = Fallible.DEAD
    create_graph(network.nodes, "failures.png")  # Generate image after simulating failures

def test_test(network, recipient_node):
    # Send messages from other nodes to the recipient node
    for sender_node in network.nodes:
        if sender_node != recipient_node:
            if sender_node.left_neighbor == recipient_node or sender_node.right_neighbor == recipient_node:
                message = Message(sender=sender_node, recipient=recipient_node, message_type='ARRIVED')
            else:
                message = Message(sender=sender_node, recipient=recipient_node, message_type='FORWARD')
            sender_node.send(message)
    create_graph(network.nodes, "test_test.png")  # Generate image after testing

def test_scenario(env, network):
    print("Testing inbox delivery scenario")
    # Choose a node to receive messages
    recipient_node = random.choice(network.nodes)
    print(f"Recipient node: {recipient_node.node_id}")

    # Let the network deliver the messages to the recipient node
    network.deliver()

    # Display the contents of the recipient node's inbox
    print(f"Recipient node's inbox after delivery:")
    for msg in recipient_node.inbox:
        print(f"Message from Node {msg.sender.node_id}, Type: {msg.message_type}")
    create_graph(network.nodes, "test_scenario.png")  # Generate image after testing

if __name__ == "__main__":
    env = simpy.Environment()
    network = Network()
    env.process(create_nodes(env, network, 8))
    
    try:
        env.run(until=100)  
        simulate_failures(network)

        print("-+-+-+-+")
        network.broadcast()
        network.print_inboxes()
        #test_scenario(env, network)
        create_graph(network.nodes, "broadcast.png")  # Generate image after broadcasting
    except Exception as e:
        print(f"An error occurred during the simulation: {e}")
