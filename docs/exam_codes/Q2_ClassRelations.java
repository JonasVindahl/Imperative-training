/*
 * QUESTION 2 — LECTURES 2-3: "Classes and How They Relate"
 *
 * Key points: Inheritance (extends), super, method overriding, @Override,
 * is-a vs has-a (composition/aggregation).
 *
 * Talk about: What does 'extends' mean? How does super() work in constructors?
 * Why prefer composition over inheritance? Show the UML relationship.
 */

class Animal {
    protected String name;

    public Animal(String name) { this.name = name; }

    public String speak() { return "..."; }

    public void describe() {
        System.out.println(name + " says: " + speak());
    }
}

class Dog extends Animal {
    public Dog(String name) { super(name); }

    @Override
    public String speak() { return "Woof"; }

    // Dog-specific behaviour (not in Animal)
    public void fetch() { System.out.println(name + " fetches the ball"); }
}

class Cat extends Animal {
    public Cat(String name) { super(name); }

    @Override
    public String speak() { return "Meow"; }
}

public class Q2_ClassRelations {
    public static void main(String[] args) {
        // Polymorphism: Animal reference, Dog object
        Animal a = new Dog("Rex");
        a.describe();  // "Rex says: Woof"

        // Can't call a.fetch() here — a is declared as Animal

        Cat c = new Cat("Whiskers");
        c.describe();  // "Whiskers says: Meow"

        // instanceof check before downcasting
        if (a instanceof Dog) {
            Dog d = (Dog) a;
            d.fetch();  // "Rex fetches the ball"
        }
    }
}
