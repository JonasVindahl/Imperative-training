/*
 * QUESTION 9 — LECTURE 10: "Exceptions and I/O"
 *
 * Key points: Checked vs unchecked, try-catch-finally, try-with-resources,
 * custom exceptions, throw vs throws, File I/O.
 *
 * Talk about: Checked = compiler forces handling. Unchecked = programmer error.
 * finally = always runs (cleanup). try-with-resources = auto-close.
 * File I/O patterns (Reader/Writer, NIO). Exception propagation.
 */

import java.io.*;
import java.nio.file.*;

public class Q9_ExceptionsIO {
    public static void main(String[] args) {
        // ---- 1. Checked vs Unchecked ----
        try {
            // Checked: compiler forces us to handle this
            Thread.sleep(1000);
        } catch (InterruptedException e) {
            System.out.println("Sleep interrupted");
        }

        // Unchecked: compiler does NOT force handling
        // int x = 5 / 0;  // ArithmeticException — would crash

        // ---- 2. Multiple catch blocks (most specific first) ----
        try {
            int[] arr = new int[3];
            System.out.println(arr[5]);
        } catch (ArrayIndexOutOfBoundsException e) {
            System.out.println("Array index: " + e.getMessage());
        } catch (Exception e) {
            System.out.println("General: " + e.getMessage());
        }

        // ---- 3. Try-with-resources (auto-close) ----
        // No finally block needed! Resources are AutoCloseable.
        File file = new File("test_output.txt");
        try (PrintWriter pw = new PrintWriter(new FileWriter(file))) {
            pw.println("Hello, file!");
            pw.printf("Answer: %d%n", 42);
        } catch (IOException e) {
            System.out.println("Write error: " + e.getMessage());
        }

        // ---- 4. Reading with try-with-resources ----
        try (BufferedReader br = new BufferedReader(new FileReader(file))) {
            String line;
            while ((line = br.readLine()) != null) {
                System.out.println("Read: " + line);
            }
        } catch (IOException e) {
            System.out.println("Read error: " + e.getMessage());
        }

        // ---- 5. NIO (modern) - Java 8+ ----
        try {
            Files.writeString(Path.of("nio_output.txt"),
                "Written with NIO!\nSecond line");
            String content = Files.readString(Path.of("nio_output.txt"));
            System.out.print("NIO reads: " + content);
        } catch (IOException e) {
            System.out.println("NIO error: " + e.getMessage());
        }

        // ---- 6. Custom exception ----
        try {
            validateAge(-5);
        } catch (InvalidAgeException e) {
            System.out.println("Custom: " + e.getMessage());
        }

        // Clean up temp files
        file.delete();
        new File("nio_output.txt").delete();
    }

    // Custom checked exception
    static class InvalidAgeException extends Exception {
        public InvalidAgeException(String message) {
            super(message);
        }
    }

    // Method declaring it MIGHT throw InvalidAgeException
    static void validateAge(int age) throws InvalidAgeException {
        if (age < 0) {
            throw new InvalidAgeException("Age cannot be negative: " + age);
        }
        System.out.println("Age " + age + " is valid");
    }
}
