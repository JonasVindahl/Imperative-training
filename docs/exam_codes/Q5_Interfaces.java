/*
 * QUESTION 5 — LECTURE 5: "Interfaces and Their Uses"
 *
 * Key points: interface keyword, implements, multiple interface inheritance,
 * default methods, functional interfaces + lambda, Comparable/Comparator,
 * marker interfaces.
 *
 * Talk about: Interface = contract (what to do), Abstract class = partial impl
 * (how to do it). Java 8 added default/static methods. Comparable vs Comparator.
 */

import java.util.*;

// Interface = 100% abstract contract (before Java 8)
interface Flyable {
    void fly();  // implicitly public abstract
}

interface Swimmable {
    void swim();
}

// Default method = optional implementation (Java 8+)
interface Honkable {
    default void honk() { System.out.println("Generic honk!"); }
}

// Class implementing MULTIPLE interfaces
class Duck implements Flyable, Swimmable, Honkable {
    @Override
    public void fly() { System.out.println("Duck flies"); }

    @Override
    public void swim() { System.out.println("Duck swims"); }

    // honk() inherited via default — Duck can use it as-is
}

// Functional interface = exactly ONE abstract method → usable as lambda
@FunctionalInterface
interface Checker {
    boolean check(int value);
}

public class Q5_Interfaces {
    public static void main(String[] args) {
        // Polymorphism through interface
        Duck d = new Duck();
        d.fly();
        d.swim();
        d.honk();

        // Store different implementations in same collection
        List<Flyable> flyers = new ArrayList<>();
        // flyers.add(d); — Duck is Flyable, Swimmable, Honkable

        // Lambda with functional interface
        Checker isPositive = (int n) -> n > 0;
        System.out.println("Is 5 positive? " + isPositive.check(5));  // true

        // Comparator — external ordering (vs Comparable = natural ordering)
        List<String> words = Arrays.asList("cat", "elephant", "dog");
        words.sort((a, b) -> a.length() - b.length());  // sort by length
        System.out.println("Sorted by length: " + words);
        // [cat, dog, elephant]

        // Interface vs Abstract class decision:
        // Interface: unrelated classes sharing capability (Duck IS Flyable)
        // Abstract class: related classes sharing STATE + behaviour
    }
}
