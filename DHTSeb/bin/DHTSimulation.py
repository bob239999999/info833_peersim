import simpy
import random
import matplotlib.pyplot as plt
import networkx as nx

class Message:
    def __init__(self, sender, recipient, message_type, data=None):
        self.sender = sender
        self.recipient = recipient
        self.type = message_type
        self.data = data

class Node:
    def __init__(self, env, node_id):
        self.env = env
        self.node_id = node_id
        self.left_neighbor = None
        self.right_neighbor = None
        self.inbox = []

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

    def process_messages(self):
        while True:
            message = self.receive()
            if message is None:
                yield self.env.timeout(1)
            else:
                if message.type == 'JOIN':
                    print(f"Node {self.node_id} received a JOIN message from Node {message.sender.node_id}")
                elif message.type == 'LEAVE':
                    print(f"Node {self.node_id} received a LEAVE message from Node {message.sender.node_id}")
                elif message.type == 'FORWARD':
                    print(f"Node {self.node_id} received FORWARD message from Node {message.sender.node_id}: {message.data}")
                yield self.env.timeout(20)

    def receive(self):
        if not self.inbox:
            return None
        else:
            return self.inbox.pop(0)

    def send_message(self, message_type, data=None):
        if message_type == 'JOIN':
            recipient = random.choice(self.network.nodes)
            message = Message(sender=self, recipient=recipient, message_type=message_type)
            recipient.receive_message(message)
            print(f"Node {self.node_id} sent a JOIN message to Node {recipient.node_id}")
        elif message_type == 'LEAVE':
            left_neighbor = self.left_neighbor
            right_neighbor = self.right_neighbor
            message = Message(sender=self, recipient=left_neighbor, message_type=message_type)
            left_neighbor.receive_message(message)
            print(f"Node {self.node_id} sent a LEAVE message to Node {left_neighbor.node_id}")
            message = Message(sender=self, recipient=right_neighbor, message_type=message_type)
            right_neighbor.receive_message(message)
            print(f"Node {self.node_id} sent a LEAVE message to Node {right_neighbor.node_id}")

    def receive_message(self, message):
        if message.type == 'JOIN':
            print(f"Node {self.node_id} received a JOIN message from Node {message.sender.node_id}")
        elif message.type == 'LEAVE':
            print(f"Node {self.node_id} received a LEAVE message from Node {message.sender.node_id}")
        elif message.type == 'FORWARD':
            print(f"Node {self.node_id} received a FORWARD message from Node {message.sender.node_id}: {message.data}")

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
        node.network = network  # Assign the network reference to the node
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
    closest_node = find_closest_node(new_node_id,network.nodes)
    # Inform the closest node about the new node
    print(f"Node {closest_node.node_id} received a JOIN request from Node {new_node_id}")
    closest_node.send_message('JOIN')

    # Inform neighbors of the closest node
    closest_node.send_message('FORWARD')

    yield env.timeout(1)

    print(f"Elapsed time: {env.now}")
    network.nodes[0].print_ring(network)

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

    env.run()
    create_graph(network.nodes)
