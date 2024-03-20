from Node import Node

class DHTSimulation:
    def __init__(self):
        pass

    @staticmethod
    def main():
        var1 = Node(1)
        var2 = Node(2)
        var1.join(var2)
        var3 = Node(4)
        var1.join(var3)
        var4 = Node(3)
        var1.join(var4)

        print("After insertion:")
        print("Node 1 Neighbors: left =", var1.left.id, ", right =", var1.right.id)
        print("Node 2 Neighbors: left =", var2.left.id, ", right =", var2.right.id)
        print("Node 0 Neighbors: left =", var3.left.id, ", right =", var3.right.id)
        print("Node 3 Neighbors: left =", var4.left.id, ", right =", var4.right.id)

        print("\nTest message routing:")
        var1.send_message(3, "Hello, Node 3!")
        print()

        print("\nTest data storage:")
        Node.put(1, "Data A")
        Node.put(2, "Data B")
        Node.put(4, "Data D")
        Node.put(3, "Data C")

        print("Data at key 1 (Node 1):", var1.get(1))
        print("Data at key 2 (Node 2):", var2.get(2))
        print("Data at key 3 (Node 3):", var4.get(3))
        print("Data at key 4 (Node 4):", var3.get(4))

        var2.leave()
        print("\nAfter the departure of Node 2:")
        print("Node 1 Neighbors: left =", var1.left.id, ", right =", var1.right.id)
        print("Node 4 Neighbors: left =", var3.left.id, ", right =", var3.right.id)

# Run the main method when this script is executed
if __name__ == "__main__":
    DHTSimulation.main()
