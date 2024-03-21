class Node:
    def __init__(self, env, node_id):
        self.env = env
        self.id = node_id
        self.left_neighbor = None
        self.right_neighbor = None

    def find_position(self, new_node, starting_node=None):
        if starting_node is None:
            starting_node = self

        # Éviter la récursion infinie en vérifiant si nous avons fait un tour complet.
        if new_node.id != starting_node.id:
            if self.id < new_node.id < self.right_neighbor.id or (self.right_neighbor == starting_node and (new_node.id < self.id or new_node.id > self.right_neighbor.id)):
                # Insérer ici
                new_node.left_neighbor = self
                new_node.right_neighbor = self.right_neighbor
                self.right_neighbor.left_neighbor = new_node
                self.right_neighbor = new_node
                print(f"Inserting node {new_node.id} between {self.id} and {new_node.right_neighbor.id}")
            else:
                # Continuer la recherche.
                self.right_neighbor.find_position(new_node, starting_node)




