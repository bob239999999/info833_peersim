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

    def broadcast(self, message):
        for node in self.nodes:
            node.send(message)
    
    def deliver(self, message):
        for node in self.nodes:
            node.receive(message)