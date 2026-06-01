/*
 * QUESTION 4 — LECTURES 4-5: "Polymorphic Data"
 *
 * Key points: Polymorphism, dynamic dispatch, abstract classes,
 * template method pattern, when to use abstract class vs interface.
 *
 * Talk about: Polymorphism = "many forms", one interface many implementations.
 * Abstract class can have state + partial implementation.
 * Why you CANNOT instantiate abstract classes.
 */

abstract class Shape {
    protected String color;

    public Shape(String color) { this.color = color; }

    // Abstract = subclasses MUST implement
    public abstract double area();

    // Concrete = shared behaviour
    public String getColor() { return color; }

    // Template method pattern
    public void printInfo() {
        System.out.println(color + " " + getClass().getSimpleName()
            + " with area " + area());
    }
}

class Circle extends Shape {
    private double radius;

    public Circle(String color, double radius) {
        super(color);
        this.radius = radius;
    }

    @Override
    public double area() { return Math.PI * radius * radius; }
}

class Rectangle extends Shape {
    private double w, h;

    public Rectangle(String color, double w, double h) {
        super(color);
        this.w = w;
        this.h = h;
    }

    @Override
    public double area() { return w * h; }
}

public class Q4_PolymorphicData {
    public static void main(String[] args) {
        // Polymorphic array — all Shapes treated uniformly
        Shape[] shapes = {
            new Circle("Red", 2),
            new Rectangle("Blue", 3, 4)
        };

        for (Shape s : shapes) {
            s.printInfo();  // Dynamic dispatch calls the right area()
        }

        // Output:
        // Red Circle with area 12.566...
        // Blue Rectangle with area 12.0

        // Cannot do: new Shape("Green") — abstract!

        // Key: the reference type is Shape, but the object type
        // determines which area() is called at runtime.
    }
}
