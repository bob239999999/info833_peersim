import java.util.HashMap;
import java.util.Map;

public class Node {
    int id; // Identifiant unique du nœud
    Node left; // Voisin de gauche
    Node right; // Voisin de droite

    public Node(int id) {
        this.id = id;
        this.left = this; // Au début, le nœud pointe sur lui-même
        this.right = this;
    }

    // Méthode pour insérer un nouveau nœud dans l'anneau
    public void join(Node newNode) {
        Node current = this;
        while (!(newNode.id > current.id && newNode.id < current.right.id)) {
            current = current.right;
            if (current == this) break; // Si on fait un tour complet sans trouver, on s'arrête
        }
        newNode.right = current.right;
        newNode.left = current;
        current.right.left = newNode;
        current.right = newNode;
    }

    // Méthode pour retirer un nœud de l'anneau
    public void leave() {
        this.left.right = this.right;
        this.right.left = this.left;
    }
    //Méthode pour envoyer un message 
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
    
    
    Map<Integer, String> storage = new HashMap<>();

    public void put(int key, String value) {
        // Ici, nous simplifions en stockant directement la valeur sans réplication
        this.storage.put(key, value);
    }

    public String get(int key) {
        return this.storage.get(key);
    }
}
