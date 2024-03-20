import org.w3c.dom.Node;

public class DHTSimulation {

    public static void main(String[] args) {
        // Create and add nodes to the ring
        Node node1 = new Node(1);
        Node node2 = new Node(2);
        node1.join(node2);
        
        Node node4 = new Node(4);
        node1.join(node4);
        
        Node node3 = new Node(3);
        node1.join(node3);

        // Display neighbors to verify insertion
        System.out.println("After insertion :");
        System.out.println("Node 1 Neighbors: left = " + node1.left.id + ", right = " + node1.right.id);
        System.out.println("Node 2 Neighbors: left = " + node2.left.id + ", right = " + node2.right.id);
        System.out.println("Node 0 Neighbors: left = " + node4.left.id + ", right = " + node4.right.id);
        System.out.println("Node 3 Neighbors: left = " + node3.left.id + ", right = " + node3.right.id);

        // Test message routing
        System.out.println("\nTest message routing :");
        node1.sendMessage(3, "Hello, Node 3!");
        
        // Array of Data 
        System.out.println();
        
        // Test data storage and retrieval
        System.out.println("\nTest data storage :");
        Node.put(1, "Data A");
        Node.put(2, "Data B");
        Node.put(4, "Data D");
        Node.put(3, "Data C");
        
        System.out.println("Data at key 1 (Node 1): " + node1.get(1));
        System.out.println("Data at key 2 (Node 2): " + node2.get(2));
        System.out.println("Data at key 3 (Node 3): " + node3.get(3));
        System.out.println("Data at key 4 (Node 4): " + node4.get(4));
        
        // Remove a node and verify neighbors
        node2.leave();
        System.out.println("\nAfter the departure of Node 2 :");
        System.out.println("Node 1 Neighbors: left = " + node1.left.id + ", right = " + node1.right.id);
        System.out.println("Node 4 Neighbors: left = " + node4.left.id + ", right = " + node4.right.id);
    
    }
}
  
