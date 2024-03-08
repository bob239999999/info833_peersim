package peersim;

import peersim.cdsim.CDSimulator;
import peersim.config.Configuration;
import peersim.config.IllegalParameterException;
import peersim.config.MissingParameterException;
import peersim.config.ParsedProperties;
import peersim.core.CommonState;
import peersim.core.Network;
import peersim.edsim.EDSimulator;

import java.io.PrintStream;


public class Simulator {

	// Static constants
	public static final int CDSIM = 0;
	public static final int EDSIM = 1;
	public static final int UNKNOWN = -1;
	protected static final String[] simName = {
			"peersim.cdsim.CDSimulator",
			"peersim.edsim.EDSimulator",
	};
	public static final String PAR_EXPS = "simulation.experiments";
	public static final String PAR_REDIRECT = "simulation.stdout";

	// Static fields
	private static int simID = UNKNOWN;

	// Methods

	public static int getSimID() {
		if (simID == UNKNOWN) {
			if (CDSimulator.isConfigurationCycleDriven()) {
				simID = CDSIM;
			} else if (EDSimulator.isConfigurationEventDriven()) {
				simID = EDSIM;
			}
		}
		return simID;
	}

	public static void main(String[] args) {
		long time = System.currentTimeMillis();

		System.err.println("Simulator: loading configuration");
		Configuration.setConfig(new ParsedProperties(args));

		PrintStream newout =
				(PrintStream) Configuration.getInstance(PAR_REDIRECT, System.out);
		if (newout != System.out) System.setOut(newout);

		int exps = Configuration.getInt(PAR_EXPS, 1);

		final int SIMID = getSimID();
		if (SIMID == UNKNOWN) {
			System.err.println(
					"Simulator: unable to determine simulation engine type");
			return;
		}

		// Conserver la graine aléatoire pour la reproductibilité
		long seed = System.currentTimeMillis();
		if (Configuration.contains("random.seed")) {
			seed = Configuration.getLong("random.seed");
		}

		try {

			for (int k = 0; k < exps; ++k) {
				CommonState.initializeRandom(seed); // Initialiser le générateur de nombres aléatoires

				System.err.print("Simulator: starting experiment " + k);
				System.err.println(" invoking " + simName[SIMID]);
				System.err.println("Rando seed: " + CommonState.r.getLastSeed());
				System.out.println("\n\n");

				// Envoi du message dans un anneau
				int currentNode = 0;
				String message = "Hello from node 0";
				while (true) {
					System.out.println("Node " + currentNode + " received message: " + message);
					if (currentNode == 0) {
						break; // Le message a complété l'anneau
					}
					currentNode = (currentNode + 1) % Network.size();
				}
			}

		} catch (MissingParameterException e) {
			System.err.println(e + "");
			System.exit(1);
		} catch (IllegalParameterException e) {
			System.err.println(e + "");
			System.exit(1);
		}

		// Capacités de test non documentées
		if (Configuration.contains("__t"))
			System.out.println(System.currentTimeMillis() - time);
		if (Configuration.contains("__x")) Network.test();
	}
}

}
