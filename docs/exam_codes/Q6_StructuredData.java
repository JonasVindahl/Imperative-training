/*
 * QUESTION 6 — LECTURES 4 & 6: "Structured Data"
 *
 * Key points: Enums (with fields, methods, abstract methods, switch),
 * Records (Java 16+, auto-generated methods, immutability),
 * Nested classes (static nested, inner, local, anonymous).
 *
 * Talk about: Enum is more than constants — it's a full class.
 * Record eliminates boilerplate for immutable data carriers.
 * When to use each type of nested class.
 */

// Enum with fields and abstract method
enum Operation {
    ADD { int apply(int a, int b) { return a + b; } },
    SUBTRACT { int apply(int a, int b) { return a - b; } },
    MULTIPLY { int apply(int a, int b) { return a * b; } };

    abstract int apply(int a, int b);
}

// Record = immutable data carrier (Java 16+)
// Auto-generates: constructor, accessors (x(), y()), equals, hashCode, toString
record Point(int x, int y) { }

// Static nested class — grouped under outer, no outer instance needed
class Library {
    static class Book {
        String title;
        Book(String title) { this.title = title; }
    }
}

public class Q6_StructuredData {
    public static void main(String[] args) {
        // --- ENUMS ---
        System.out.println("ADD 5+3=" + Operation.ADD.apply(5, 3));       // 8
        System.out.println("SUBTRACT 5-3=" + Operation.SUBTRACT.apply(5, 3)); // 2

        // Enum in switch
        Operation op = Operation.MULTIPLY;
        switch (op) {
            case ADD:    System.out.println("Adding"); break;
            case MULTIPLY: System.out.println("Multiplying"); break;
            default:     System.out.println("Other");
        }

        // values() — iterate all constants
        for (Operation o : Operation.values()) {
            System.out.println(o + " applies: " + o.apply(10, 4));
        }

        // --- RECORDS ---
        Point p1 = new Point(3, 5);
        Point p2 = new Point(3, 5);
        System.out.println("Record: " + p1);           // Point[x=3, y=5]
        System.out.println("Equals: " + p1.equals(p2)); // true (auto-generated)
        System.out.println("Accessor: " + p1.x());      // 3 (not getX()!)

        // Records are immutable — no setters
        // p1.x = 10;  // COMPILATION ERROR

        // --- NESTED CLASSES ---
        // Static nested: no outer instance needed
        Library.Book book = new Library.Book("OOP Design");
        System.out.println("Book: " + book.title);

        // Anonymous class (e.g. for event handlers, quick overrides)
        Runnable task = new Runnable() {
            @Override
            public void run() {
                System.out.println("Anonymous task running");
            }
        };
        task.run();

        // Modern equivalent with lambda:
        Runnable task2 = () -> System.out.println("Lambda task running");
        task2.run();
    }
}
