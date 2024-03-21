import simpy
from node import Node
import random

class DhtRing:
    def __init__(self, env, print_ring=False):  # Ajouter le paramètre print_ring ici
        self.env = env
        self.nodes = []
        self.print_ring = print_ring  # Conserve cet argument dans une variable d'instance.

    def initiate_insertion(self, node_id, env):
        yield env.timeout(random.randint(1, 10))  # Un délai avant l'insertion.
        new_node = Node(env, node_id)
        if not self.nodes:
            # Si l'anneau est vide, le nouveau nœud se référence lui-même.
            new_node.left_neighbor = new_node
            new_node.right_neighbor = new_node
            self.nodes.append(new_node)
        else:
            start_node = random.choice(self.nodes)  # Choisir un nœud existant au hasard.
            start_node.find_position(new_node)
            self.nodes.append(new_node)  # Ajouter le nouveau nœud à la liste.
        if self.print_ring:
            self.print_current_ring()

    def print_current_ring(self):
        if self.nodes:
            print("Current state of the DHT Ring:")
            for node in self.nodes:
                print(f"Node {node.id} (Left: {node.left_neighbor.id}, Right: {node.right_neighbor.id})")
            print("End of ring state\n")
        else:
            print("The DHT Ring is currently empty.\n")



