# node.py
import simpy
import random
from Message import Message

class Node:
    def __init__(self, env, node_id):
        self.env = env
        self.node_id = node_id
        self.left_neighbor = None
        self.right_neighbor = None
        self.inbox = []
        self.data_store = {}  # Dictionnaire pour stocker les données
        self.finished = env.event()  # Event to track message processing completion
        self.env.process(self.process_messages())  # Start processing messages

    def join_ring(self, network):
        print("\n=== Join Ring ===")
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
        print("\n=== Leave Ring ===")
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
        print(f"SEND: Node {self.node_id} -> Node {message.recipient.node_id}, Type: {message.type}, Time: {self.env.now}")

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
                if not self.finished.triggered:
                    self.finished.succeed()
  # Signal that all messages in the inbox have been processed
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
            print(f"RECEIVE: Node {self.node_id} <- Node {message.sender.node_id}, Type: {message.type}, Time: {self.env.now}")
            return message

    def send_hello_message(self, network):
        # Choose a random node in the network to send the hello message
        print("\n=== Envoi d'un message HELLO d'un noeud à un autre noeud aléatoire de l'anneau ===")
        recipient_node = random.choice(network.nodes)
        hello_message = Message(sender=self, recipient=recipient_node, message_type='HELLO')
        self.send(hello_message)

    def put_data(self, key, value):
        # Affichage avant le stockage des données
        print(f"\n=== Stockage de Données ===")
        print(f"[Nœud {self.node_id}] Tente de stocker la donnée : Clé={key}, Valeur='{value}'.")

        # Stocker la donnée dans le nœud actuel
        self.data_store[key] = value
        print(f"[Nœud {self.node_id}] Stockage réussi.")

        # Propager la donnée aux deux voisins immédiats pour réplication
        self.left_neighbor.data_store[key] = value
        print(f"[Nœud {self.left_neighbor.node_id}] Réplication de la donnée : Clé={key}.")
        
        self.right_neighbor.data_store[key] = value
        print(f"[Nœud {self.right_neighbor.node_id}] Réplication de la donnée : Clé={key}.")

        print("La donnée a été stockée et répliquée avec succès.")


    def get_data(self, key):
        # Vérifier si la clé existe dans le stockage actuel
        if key in self.data_store:
            return self.data_store[key]
        else:
            print(f"[Nœud {self.node_id}] La clé {key} n'est pas trouvée.")
            return None

