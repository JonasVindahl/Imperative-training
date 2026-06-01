/*
 * QUESTION 1 — LECTURES 1-2: "Classes, Fundamentally"
 *
 * Key points: class structure, constructor, encapsulation (private fields +
 * getters/setters), this keyword, static vs instance, toString(), main method.
 *
 * Talk about: What OOP is, class as blueprint, object as instance,
 * why encapsulation matters, constructor overloading.
 */

class Student {
    private String name;
    private int id;
    private static int nextId = 1;

    public Student(String name) {
        this.name = name;
        this.id = nextId++;
    }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public int getId() { return id; }

    public static int getTotalStudents() { return nextId - 1; }

    @Override
    public String toString() {
        return "Student #" + id + ": " + name;
    }
}

public class Q1_Classes {
    public static void main(String[] args) {
        Student s1 = new Student("Alice");
        Student s2 = new Student("Bob");

        System.out.println(s1);
        System.out.println(s2);
        System.out.println("Total: " + Student.getTotalStudents());
        // Output:
        // Student #1: Alice
        // Student #2: Bob
        // Total: 2
    }
}
