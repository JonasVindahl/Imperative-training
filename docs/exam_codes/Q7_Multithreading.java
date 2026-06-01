/*
 * QUESTION 7 — LECTURES 7-8: "Multi-threading"
 *
 * Key points: Thread/Runnable, race condition, synchronized, wait/notify,
 * deadlock, ExecutorService, AtomicInteger.
 *
 * Talk about: Thread = unit of execution. Race condition = lost update.
 * synchronized = mutual exclusion (intrinsic lock). Deadlock = circular wait.
 * Prefer ExecutorService over raw threads.
 */

import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

class Counter {
    private int count = 0;

    // Without synchronized: RACE CONDITION
    // count++ is: read → increment → write (3 steps!)
    public synchronized void increment() {
        count++;
    }

    public int getCount() { return count; }
}

public class Q7_Multithreading {
    public static void main(String[] args) throws Exception {
        // ---- 1. Manual thread with Runnable ----
        Thread t = new Thread(() -> {
            System.out.println("Hello from: " + Thread.currentThread().getName());
        });
        t.setName("Worker-1");
        t.start();
        t.join();  // main waits for t to finish

        // ---- 2. Race condition demo ----
        Counter counter = new Counter();
        Thread t1 = new Thread(() -> {
            for (int i = 0; i < 10000; i++) counter.increment();
        });
        Thread t2 = new Thread(() -> {
            for (int i = 0; i < 10000; i++) counter.increment();
        });
        t1.start(); t2.start();
        t1.join(); t2.join();
        System.out.println("Synchronized counter: " + counter.getCount());
        // Always 20000 — synchronized prevents race condition

        // ---- 3. AtomicInteger (no explicit sync needed) ----
        AtomicInteger atomic = new AtomicInteger(0);
        Thread t3 = new Thread(() -> {
            for (int i = 0; i < 10000; i++) atomic.incrementAndGet();
        });
        Thread t4 = new Thread(() -> {
            for (int i = 0; i < 10000; i++) atomic.incrementAndGet();
        });
        t3.start(); t4.start();
        t3.join(); t4.join();
        System.out.println("Atomic counter: " + atomic.get());
        // Also 20000 — CAS instructions, often faster than synchronized

        // ---- 4. ExecutorService (preferred over raw threads) ----
        ExecutorService pool = Executors.newFixedThreadPool(4);
        Future<Integer> future = pool.submit(() -> {
            Thread.sleep(500);
            return 42;
        });
        System.out.println("Future result: " + future.get());  // 42
        pool.shutdown();

        // Deadlock example (don't run — it hangs):
        // Thread A locks resource1, waits for resource2
        // Thread B locks resource2, waits for resource1
        // Solution: always acquire locks in the same order
    }
}
