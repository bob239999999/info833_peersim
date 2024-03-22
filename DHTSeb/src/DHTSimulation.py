import simpy
import random
import matplotlib.pyplot as plt
import networkx as nx

class Message:
    def __init__(self, sender, recipient, message_type):
        self.sender = sender
        self.recipient = recipient
        self.type = message_type

class Node:
    def __init__(self, env, node_id):
        self.env = env
        self.node_id = node_id
        self.left_neighbor = None
        self.right_neighbor = None
        self.inbox = []
        self.finished = env.event()  # Event to track message processing completion
        self.env.process(self.process_messages())  # Start processing messages

    def join_ring(self, network):
        if not network.nodes:
            self.left_neighbor = self
            self.right_neighbor = self
            network.add_node(self)
            print(f"Node {self.node_id} joined the ring at time {self.env.now}")
            self.print_neighbors()
            self.print_ring(network)
            return

        # Find the correct position for the new node in the ring based on its ID
        insert_index = 0
        for i, node in enumerate(network.nodes):
            if node.node_id > self.node_id:
                insert_index = i
                break

        # Update the neighbors
        self.left_neighbor = network.nodes[insert_index]
        self.right_neighbor = network.nodes[insert_index].right_neighbor
        self.right_neighbor.left_neighbor = self
        self.left_neighbor.right_neighbor = self
        network.add_node(self)

        print(f"Node {self.node_id} joined the ring at time {self.env.now}")
        self.print_neighbors()
        self.print_ring(network)

    def leave_ring(self, network):
        print(f"Node {self.node_id} leaving the ring at time {self.env.now}")
        self.print_neighbors()
        self.print_ring(network)

        # Inform neighbors about leaving
        leave_message = Message(sender=self, recipient=self.left_neighbor, message_type='LEAVE')
        self.send(leave_message)
        leave_message = Message(sender=self, recipient=self.right_neighbor, message_type='LEAVE')
        self.send(leave_message)

        if self.left_neighbor == self and self.right_neighbor == self:
            network.remove_node(self)
            return

        self.left_neighbor.right_neighbor = self.right_neighbor
        self.right_neighbor.left_neighbor = self.left_neighbor

        if network.nodes[0] == self:
            network.nodes[-1].right_neighbor = self.right_neighbor

        network.remove_node(self)

        # Contact neighbors to set new connections
        self.left_neighbor.right_neighbor = self.right_neighbor
        self.right_neighbor.left_neighbor = self.left_neighbor

        print(f"Neighbors of Node {self.node_id} updated:")
        self.left_neighbor.print_neighbors()
        self.right_neighbor.print_neighbors()

    def print_neighbors(self):
        print(f"Node {self.node_id}: Left Neighbor = {self.left_neighbor.node_id}, Right Neighbor = {self.right_neighbor.node_id}")

    def print_ring(self, network):
        ring = "->".join(str(node.node_id) for node in network.nodes)
        print(f"Ring: {ring}")

    def send(self, message):
        message.recipient.inbox.append(message)
        print(f"Message sent: Node {self.node_id} sent a {message.type} message to Node {message.recipient.node_id}")
        print(f"SEND: Node {self.node_id} -> Node {message.recipient.node_id}, Type: {message.type}")

    def process_messages(self):
        while True:
            # Check if there are messages in the inbox
            if self.inbox:
                # Process each message in the inbox
                for _ in range(len(self.inbox)):
                    message = self.receive()
                    if message is not None:
                        if message.type == 'JOIN':
                            print(f"Node {self.node_id} received a JOIN message from {message.sender.node_id}")
                        elif message.type == 'LEAVE':
                            print(f"Node {self.node_id} received a LEAVE message from {message.sender.node_id}")
                        elif message.type == 'FORWARD':
                            print(f"Node {self.node_id} received FORWARD message from {message.sender.node_id}: {message.data}")
                    yield self.env.timeout(20)  # Timeout after processing each message
                self.finished.succeed()  # Signal that all messages in the inbox have been processed
            else:
                # If there are no messages, wait for a timeout
                yield self.env.timeout(1)

    def receive(self):
        if not self.inbox:
            return None
        else:
            return self.deliver()

    def deliver(self):
        if not self.inbox:
            return None
        else:
            message = self.inbox.pop(0)
            print(f"Message received: Node {self.node_id} received a {message.type} message from Node {message.sender.node_id}")
            print(f"RECEIVE: Node {self.node_id} <- Node {message.sender.node_id}, Type: {message.type}")
            return message

    def send_hello_message(self, network):
        # Choose a random node in the network to send the hello message
        recipient_node = random.choice(network.nodes)
        hello_message = Message(sender=self, recipient=recipient_node, message_type='HELLO')
        self.send(hello_message)

class Network:
    def __init__(self):
        self.nodes = []

    def add_node(self, node):
        # Find the correct position to insert the node based on its ID
        index = 0
        for existing_node in self.nodes:
            if existing_node.node_id > node.node_id:
                break
            index += 1
        self.nodes.insert(index, node)

    def remove_node(self, node):
        self.nodes.remove(node)

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
        yield env.timeout(random.randint(1, 5))
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

    yield env.timeout(1)

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

if __name__ == "__main__":
    env = simpy.Environment()
    network = Network()

    env.process(create_nodes(env, network, 5))

    try:
        env.run(until=100)  # Exécuter la simulation jusqu'à un certain temps (100 dans cet exemple)
    except Exception as e:
        print(f"An error occurred during the simulation: {e}")
    finally:
        create_graph(network.nodes)







