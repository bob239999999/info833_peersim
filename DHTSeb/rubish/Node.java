import java.util.HashMap;
import java.util.Map;

public class Node {
    int id; // Unique identifier of the node
    Node left; // Left neighbor
    Node right; // Right neighbor
    
    public static Map<Integer, String> storage = new HashMap<>();

    public Node(int id) {
        this.id = id;
        this.left = this; // Initially, the node points to itself
        this.right = this;
        storage.put(id,"");
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
    public static void put(int key, String value) {
        // Check if the key exists in the storage
        if (storage.containsKey(key)) {
            // Key already exists, replace the existing value
            storage.put(key, value);
        } else {
            // Key does not exist, search for the nearest key
            int nearestKey = findNearestKey(key);
            if (nearestKey != -1) {
                // Nearest key found, store the value with the nearest key
                storage.put(nearestKey, value);
            } else {
                // No key found in the storage, directly store the value with the specified key
                storage.put(key, value);
            }
        }
    }


 // Method to retrieve data from the node's storage
    public String get(int key) {
        // Check if the key exists in the storage
        if (storage.containsKey(key)) {
            return storage.get(key); // If found, return the corresponding value
        } else {
            // If the key is not found, search for the nearest key
            int nearestKey = findNearestKey(key);
            if (nearestKey != -1) {
                return storage.get(nearestKey); // Return the value corresponding to the nearest key
            } else {
                return null; // If no key is found, return null
            }
        }
    }

    // Method to find the nearest key in the storage
    private static int findNearestKey(int key) {
        int minDiff = Integer.MAX_VALUE;
        int nearestKey = -1;
        for (int storedKey : storage.keySet()) {
            int diff = Math.abs(storedKey - key);
            if (diff < minDiff) {
                minDiff = diff;
                nearestKey = storedKey;
            }
        }
        return nearestKey;
    }

}
