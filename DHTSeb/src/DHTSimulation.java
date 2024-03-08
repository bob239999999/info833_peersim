public class DHTSimulation {

    public static void main(String[] args) {
        // Création et ajout de nœuds dans l'anneau
        Node node1 = new Node(1);
        Node node2 = new Node(2);
        node1.join(node2);
        
        Node node3 = new Node(3);
        node1.join(node3);

        // Affichage des voisins pour vérifier l'insertion
        System.out.println("Après insertion :");
        System.out.println("Node 1 Voisins: gauche = " + node1.left.id + ", droite = " + node1.right.id);
        System.out.println("Node 2 Voisins: gauche = " + node2.left.id + ", droite = " + node2.right.id);
        System.out.println("Node 3 Voisins: gauche = " + node3.left.id + ", droite = " + node3.right.id);

        // Test de l'envoi de messages
        System.out.println("\nTest de routage de messages :");
        node1.sendMessage(3, "Hello, Node 3!");
        
        // Test du stockage et de la récupération de données
        System.out.println("\nTest de stockage :");
        node1.put(101, "Data A");
        node2.put(202, "Data B");
        node3.put(303, "Data C");

        System.out.println("Donnée à la clé 101 (Node 1): " + node1.get(101));
        System.out.println("Donnée à la clé 202 (Node 2): " + node2.get(202));
        System.out.println("Donnée à la clé 303 (Node 3): " + node3.get(303));

        // Retrait d'un nœud et vérification des voisins
        node2.leave();
        System.out.println("\nAprès le départ du Node 2 :");
        System.out.println("Node 1 Voisins: gauche = " + node1.left.id + ", droite = " + node1.right.id);
        System.out.println("Node 3 Voisins: gauche = " + node3.left.id + ", droite = " + node3.right.id);
    	
    
    
    }
    
   
}
