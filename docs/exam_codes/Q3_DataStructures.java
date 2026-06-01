/*
 * QUESTION 3 — LECTURES 2 & 4: "Objects and Data Structures"
 *
 * Key points: Arrays vs ArrayList vs LinkedList vs HashMap vs Stack vs Queue,
 * generics, iteration, choosing the right structure.
 *
 * Talk about: When to use each data structure (time complexity trade-offs).
 * Show how objects interact with collections.
 */

import java.util.*;

class Bicycle {
    String name;
    double speed;

    Bicycle(String name, double speed) {
        this.name = name;
        this.speed = speed;
    }

    @Override
    public String toString() {
        return name + " (" + speed + " km/h)";
    }
}

public class Q3_DataStructures {
    public static void main(String[] args) {
        // 1. ArrayList — fast random access
        ArrayList<Bicycle> list = new ArrayList<>();
        list.add(new Bicycle("Racer", 35));
        list.add(new Bicycle("Mountain", 20));
        list.add(new Bicycle("City", 15));
        System.out.println("ArrayList: " + list);
        System.out.println("Index 1: " + list.get(1));  // O(1)

        // 2. LinkedList — fast insertions at front/back
        LinkedList<String> ll = new LinkedList<>();
        ll.addFirst("first");    // O(1)
        ll.addLast("last");      // O(1)
        System.out.println("LinkedList: " + ll);

        // 3. HashMap — key-value lookup O(1) average
        HashMap<Integer, String> map = new HashMap<>();
        map.put(1, "Alice");
        map.put(2, "Bob");
        System.out.println("HashMap get(1): " + map.get(1));  // O(1)

        // 4. Stack — LIFO (undo feature)
        Stack<String> stack = new Stack<>();
        stack.push("A");
        stack.push("B");
        System.out.println("Stack pop: " + stack.pop());  // "B"

        // 5. Queue — FIFO (printer queue)
        Queue<String> queue = new LinkedList<>();
        queue.add("doc1");
        queue.add("doc2");
        System.out.println("Queue poll: " + queue.poll());  // "doc1"

        // 6. PriorityQueue — ordered by priority
        PriorityQueue<Integer> pq = new PriorityQueue<>();
        pq.add(30); pq.add(10); pq.add(20);
        System.out.println("PriorityQueue poll: " + pq.poll());  // 10

        // Key time complexities:
        //               ArrayList  LinkedList
        // get(i)        O(1)        O(n)
        // add at end    O(1)*       O(1)
        // add at front  O(n)        O(1)
        // remove(i)     O(n)        O(n)
    }
}
