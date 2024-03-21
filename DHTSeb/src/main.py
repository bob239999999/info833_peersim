import simpy
import random
from dht_ring import DhtRing

def main():
    env = simpy.Environment()
    dht_ring = DhtRing(env, print_ring=True)

    # Planification de l'insertion de nœuds à différents moments.
    for _ in range(4):
        node_id = random.randint(1, 100)
        env.process(dht_ring.initiate_insertion(node_id, env))

    env.run(until=100)

if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()


