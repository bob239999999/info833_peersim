from Message import Message
import random
class Network:
    def __init__(self):
        self.nodes = []
        self.routing_table = {}

    def add_node(self, node):
        # Find the correct position to insert the nodae based on its ID
        index = 0
        for existing_node in self.nodes:
            if existing_node.node_id > node.node_id:
                break
            index += 1
        self.nodes.insert(index, node)

    def remove_node(self, node):
        self.nodes.remove(node)

    def find_responsible_node(self, key):
        if not self.nodes:  # Vérifier si la liste des nœuds est vide
            print("Erreur : Il n'y a aucun nœud dans le réseau DHT.")
            return None
        # Trouver le nœud avec l'ID le plus proche de la clé
        closest_node = min(self.nodes, key=lambda node: abs(node.node_id - key))
        return closest_node

    


    