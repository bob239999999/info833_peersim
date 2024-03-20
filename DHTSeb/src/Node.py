class Node:
    storage = {}

    def __init__(self, id):
        self.id = id
        self.left = self
        self.right = self
        Node.storage[id] = ""

    def join(self, new_node):
        current = self
        while new_node.id <= current.id or new_node.id >= current.right.id:
            current = current.right
            if current == self:
                break
        new_node.right = current.right
        new_node.left = current
        current.right.left = new_node
        current.right = new_node

    def leave(self):
        self.left.right = self.right
        self.right.left = self.left

    def send_message(self, destination_id, message):
        target = self
        while target.id != destination_id:
            print("Routing through node:", target.id)
            target = target.right
            if target == self:
                print("Destination not found.")
                return
        print("Delivered to node", destination_id, ":", message)

    @staticmethod
    def put(key, value):
        if key in Node.storage:
            Node.storage[key] = value
        else:
            nearest_key = Node.find_nearest_key(key)
            if nearest_key != -1:
                Node.storage[nearest_key] = value
            else:
                Node.storage[key] = value

    def get(self, key):
        if key in Node.storage:
            return Node.storage[key]
        else:
            nearest_key = Node.find_nearest_key(key)
            return Node.storage[nearest_key] if nearest_key != -1 else None

    @staticmethod
    def find_nearest_key(key):
        min_diff = float('inf')
        nearest_key = -1
        for stored_key in Node.storage.keys():
            diff = abs(stored_key - key)
            if diff < min_diff:
                min_diff = diff
                nearest_key = stored_key
        return nearest_key
