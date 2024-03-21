import simpy
import random
import matplotlib.pyplot as plt
import networkx as nx

class Node:
    def __init__(self, env, node_id):
        self.env = env
        self.node_id = node_id
        self.left_neighbor = None
        self.right_neighbor = None

    def join_ring(self, network):
        if not network.nodes:
            self.left_neighbor = self
            self.right_neighbor = self
        else:
            joining_node = random.choice(network.nodes)
            self.left_neighbor = joining_node
            self.right_neighbor = joining_node.right_neighbor
            joining_node.right_neighbor.left_neighbor = self
            joining_node.right_neighbor = self
            print(f"Node {self.node_id} contacting node {joining_node.node_id} to join the ring")

        network.add_node(self)
        print(f"Node {self.node_id} joined the ring at time {self.env.now}")
        self.print_neighbors()
        self.print_ring(network)


    def leave_ring(self, network):
        print(f"Node {self.node_id} leaving the ring at time {self.env.now}")
        self.print_neighbors()
        self.print_ring(network)
        if self.left_neighbor == self and self.right_neighbor == self:
            network.remove_node(self)
        else:
            self.right_neighbor.left_neighbor = self.left_neighbor
            self.left_neighbor.right_neighbor = self.right_neighbor
            if network.nodes[0] == self:  # Update the left neighbor of the right neighbor of the first node
                network.nodes[-1].right_neighbor = self.right_neighbor
            # Update the left and right neighbors of the leaving node's new neighbors
            self.left_neighbor.right_neighbor = self.right_neighbor
            self.right_neighbor.left_neighbor = self.left_neighbor
            network.remove_node(self)

    def print_neighbors(self):
        print(f"Node {self.node_id}: Left Neighbor = {self.left_neighbor.node_id}, Right Neighbor = {self.right_neighbor.node_id}")

    def print_ring(self, network):
        ring = "->".join(str(node.node_id) for node in network.nodes)
        print(f"Ring: {ring}")

class Network:
    def __init__(self):
        self.nodes = []

    def add_node(self, node):
        self.nodes.append(node)
        self.nodes.sort(key=lambda x: x.node_id)

    def remove_node(self, node):
        self.nodes.remove(node)

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
    new_node = Node(env, new_node_id)
    new_node.join_ring(network)

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
