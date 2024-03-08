import java.util.HashMap;
import java.util.Map;

public class Node {
    int id; // Unique identifier of the node
    Node left; // Left neighbor
    Node right; // Right neighbor
    
    Map<Integer, String> storage = new HashMap<>();

    public Node(int id) {
        this.id = id;
        this.left = this; // Initially, the node points to itself
        this.right = this;
    }

    // Method to insert a new node into the ring
    public void join(Node newNode) {
        Node current = this;
        while (!(newNode.id > current.id && newNode.id < current.right.id)) {
            current = current.right;
            if (current == this) break; // If we make a complete loop without finding, we stop
        }
        newNode.right = current.right;
        newNode.left = current;
        current.right.left = newNode;
        current.right = newNode;
    }

    // Method to remove a node from the ring
    public void leave() {
        this.left.right = this.right;
        this.right.left = this.left;
    }
    
    // Method to send a message to a destination node
    public void sendMessage(int destinationId, String message) {
        Node target = this;
        while (target.id != destinationId) {
            System.out.println("Routing through node: " + target.id);
            target = target.right;
            if (target == this) {
                System.out.println("Destination not found.");
                return;
            }
        }
        System.out.println("Delivered to node " + destinationId + ": " + message);
    }

    // Method to store data in the node's storage
    public void put(int key, String value) {
        // Here, we simplify by directly storing the value without replication
        this.storage.put(key, value);
    }

    // Method to retrieve data from the node's storage
    public String get(int key) {
        return this.storage.get(key);
    }
}
