from Message import Message
import random
from Fallible import Fallible

class Node:

    def __init__(self, env, node_id):
        self.env = env
        self.node_id = node_id
        self.left_neighbor = None
        self.right_neighbor = None
        self.inbox = []
        self.failstate = Fallible.ALIVE  # Corrected attribute name
        self.finished = env.event()  # Event to track message processing completion
        #self.env.process(self.process_messages())  # Start processing messages

    def join_ring(self, network):
        print("---JOIN RING --------------------------------")
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
        print("--- LEAVE RING --------------------------------")
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
        print("----*----*----*----*----*----*----*----")
        if self.failstate == Fallible.DEAD:
            print(f"Node {self.node_id} has failed during send.")
        else:
            message.recipient.inbox.append(message)
            print(f"Node {message.sender.node_id} send a JOIN message from {message.recipient.node_id}")
            self.process_messages(message) 

    def process_messages(self, message):

        if message.message_type == 'JOIN':
            print(f"Node {message.recipient.node_id} received a JOIN message from {message.sender.node_id}")
        elif message.message_type == 'BROADCAST':
            print(f"Node {message.recipient.node_id} received a BROADCAST message from {message.sender.node_id}")
        elif message.message_type == 'LEAVE':
            print(f"Node {message.recipient.node_id} received a LEAVE message from {message.sender.node_id}")
        elif message.message_type == 'FORWARD':
            print(f"Node {message.recipient.node_id} received FORWARD message from {message.sender.node_id}")
        elif message.message_type == 'TEST':
            print(f"Node {message.recipient.node_id} received a TEST message from {message.sender.node_id}")
        elif message.message_type == 'ARRIVED':
            print(f"Node {message.recipient.node_id} received a ARRIVED message from {message.sender.node_id}:{message.data}")
        else:
            print("Unknown message type")

    def send_hello_message(self, network):
        # Choose a random node in the network to send the hello message
        recipient_node = random.choice(network.nodes)
        hello_message = Message(sender=self, recipient=recipient_node, message_type='HELLO')
        self.send(hello_message)

    def receive(self, message):
        # Simulate failure during receive
        if self.failstate == Fallible.DEAD:
            print(f"Node {self.node_id} is dead. Message cannot be received.")
            return
        if not self.inbox:
            return None
        else:
            return self.deliver()

    def deliver(self):
        if not self.inbox:
            return None
        else:
            message = self.inbox.pop(0)
            print(f"Message received: Node {self.node_id} received a {message.message_type} message from Node {message.sender.node_id}")
            print(f"RECEIVE: Node {self.node_id} <- Node {message.sender.node_id}, Type: {message.message_type}")
            return message

    def setfailstate(self, state):
        self.failstate = state