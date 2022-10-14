public class Utils {

	/**
	 *  Display the splash screen
	 */
	public static void splashScreen() {
		System.out.println(printSeparator("-",80));
	    System.out.println("Welcome to Gell-Mann DataBase"); // Display the string.
		System.out.println("Gell-Mann DataBase Version " + Settings.getVersion());
		System.out.println("All commands below are case insensitive\n");
		//System.out.println(Settings.getCopyright());
		System.out.println("\nType \"help;\" to display supported commands.");
		System.out.println(printSeparator("-",80));
	}

	public static String printSeparator(String s, int len) {
		String bar = "";
		for(int i = 0; i < len; i++) {
			bar += s;
		}
		return bar;
	}

}