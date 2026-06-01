/*
 * QUESTION 8 — LECTURES 8-9: "Asynchronous Communication"
 *
 * Key points: wait()/notify(), producer-consumer pattern, BlockingQueue,
 * CompletableFuture (Java 8+), callback chaining.
 *
 * Talk about: Synchronous = blocking, async = non-blocking.
 * Producer-consumer = classic coordination problem.
 * BlockingQueue handles all the wait/notify complexity automatically.
 * CompletableFuture chains callbacks without blocking.
 */

import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

public class Q8_AsyncCommunication {
    public static void main(String[] args) throws Exception {
        // ---- 1. BlockingQueue = Producer-Consumer (no wait/notify needed) ----
        BlockingQueue<String> queue = new ArrayBlockingQueue<>(5);

        // Producer
        Thread producer = new Thread(() -> {
            try {
                for (int i = 1; i <= 5; i++) {
                    String item = "Item-" + i;
                    queue.put(item);  // blocks if queue is full
                    System.out.println("Produced: " + item);
                    Thread.sleep(200);
                }
            } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
        });

        // Consumer
        Thread consumer = new Thread(() -> {
            try {
                for (int i = 1; i <= 5; i++) {
                    String item = queue.take();  // blocks if queue is empty
                    System.out.println("Consumed: " + item);
                    Thread.sleep(400);
                }
            } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
        });

        producer.start();
        consumer.start();
        producer.join();
        consumer.join();
        // Producer runs faster (200ms) than consumer (400ms)
        // → queue buffers the items, consumer catches up

        System.out.println("---");

        // ---- 2. CompletableFuture (non-blocking async) ----
        // Run async task, then chain callback
        CompletableFuture.supplyAsync(() -> {
            try { Thread.sleep(300); } catch (Exception e) {}
            return 42;
        }).thenApply(result -> result * 2)
          .thenAccept(result -> System.out.println("Async result: " + result))
          .join();  // wait for completion

        // ---- 3. Wait/Notify (low-level, BlockingQueue is preferred) ----
        // Classic pattern:
        // synchronized(obj) {
        //     while (!condition) obj.wait();  // releases lock, waits
        //     // condition is true now
        // }
        // In another thread:
        // synchronized(obj) {
        //     condition = true;
        //     obj.notify();  // wakes one waiting thread
        // }
        // Always use while(), not if() — guards against spurious wakeups
    }
}
