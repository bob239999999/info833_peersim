from Fallible import Fallible
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

    def broadcast_recursive(self, sender_node, initial_sender):
        print(F"Broadcasting {sender_node.node_id}  {sender_node.failstate}")
        
        #if sender_node.failstate == Fallible.DEAD:
        #    return  # Skip broadcasting from failed nodes
      
        # Check if initial_sender is None (i.e., the first call of the recursion)
        if initial_sender is None:
            print(f"Broadcasting 1 {initial_sender} ")
            initial_sender = sender_node

        if sender_node.right_neighbor:
            print(f"Broadcasting 2 {sender_node.right_neighbor.node_id}")
            recipient_node = sender_node.right_neighbor
            message = Message(initial_sender, recipient=recipient_node, message_type='BROADCAST')
            sender_node.send(message)
            # Continue broadcasting recursively
            if recipient_node != initial_sender:  # Ensure circular broadcasting
                print("continue broadcasting")
                self.broadcast_recursive(recipient_node, initial_sender)
            else:
                # Broadcasting has completed the cycle
                return

        elif sender_node.left_neighbor:
            print("Broadcasting 4  {sender_node.left_neighbor.node_id}")
            recipient_node = sender_node.left_neighbor
            message = Message(sender_node, recipient=recipient_node, message_type='BROADCAST')
            sender_node.send(message)
            # Continue broadcasting recursively
            if recipient_node != initial_sender:  # Ensure circular broadcasting
                self.broadcast_recursive(recipient_node, initial_sender)
            else:
                # Broadcasting has completed the cycle
                return

    

        

    def deliver(self):
        for node in self.nodes:
            if node.failstate == Fallible.DEAD:
                continue  # Skip delivering messages to failed nodes
            # Process messages in the inbox
            while node.inbox:
                message = node.deliver()
                if message:
                    # Forward the message to all other nodes except the sender
                    for recipient_node in self.nodes:
                        if recipient_node != message.sender:
                            forward_message = Message(node, recipient=recipient_node, message_type='FORWARD')
                            message.setdata(message.data)
                            node.send(forward_message)


    