
public class DHTSimulation {

    public static void main(String[] args) {
        // Create and add nodes to the ring
        Node node1 = new Node(1);
        Node node2 = new Node(2);
        node1.join(node2);
        
        Node node0 = new Node(0);
        node1.join(node0);
        
        Node node3 = new Node(4);
        node1.join(node3);

        // Display neighbors to verify insertion
        System.out.println("After insertion :");
        System.out.println("Node 1 Neighbors: left = " + node1.left.id + ", right = " + node1.right.id);
        System.out.println("Node 2 Neighbors: left = " + node2.left.id + ", right = " + node2.right.id);
        System.out.println("Node 0 Neighbors: left = " + node0.left.id + ", right = " + node0.right.id);
        System.out.println("Node 3 Neighbors: left = " + node3.left.id + ", right = " + node3.right.id);

        // Test message routing
        System.out.println("\nTest message routing :");
        node1.sendMessage(3, "Hello, Node 3!");
        
        // Test data storage and retrieval
        System.out.println("\nTest data storage :");
        node1.put(101, "Data A");
        node2.put(202, "Data B");
        node0.put(303, "Data C");

        System.out.println("Data at key 101 (Node 1): " + node1.get(101));
        System.out.println("Data at key 202 (Node 2): " + node2.get(202));
        System.out.println("Data at key 303 (Node 3): " + node0.get(303));

        // Remove a node and verify neighbors
        node2.leave();
        System.out.println("\nAfter the departure of Node 2 :");
        System.out.println("Node 1 Neighbors: left = " + node1.left.id + ", right = " + node1.right.id);
        System.out.println("Node 3 Neighbors: left = " + node0.left.id + ", right = " + node0.right.id);
    }
}
  
