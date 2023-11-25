# Food Order System

##### Download & Unzip the Project File
1. `cd <your working directory>`
2. Download `food_order_system_James_Pan.zip`
3. `unzip food_order_system_James_Pan.zip`
4. `ls food_order_system`
##### Build this Project
1. `cd food_order_system/`
2. `python -m venv venv`
3. `source venv/bin/activate`
4. `pip install -r requirements.tx`

##### Run this Project
1. `cd food_order_system/`
2. `source venv/bin/activate`
3. `python main.py`

##### Verify the Simulation Log Files
<p style="margin-left: 20px;">
After simulation, check the log files under ./test/<br><br>
<b>sim_order.log</b>: detail simulation log.<br>
<b>input_orders.json</b>: orders placed<br>
<b>output_actions.json</b>: actions generated.
</p>



## Concept of Architecture
<p style="margin-left: 40px;">
This food order system project is an I/O-bound project because each food order involves waiting for a client response or action (such as waiting for a pickup).  In this case, Python's asyncio module is a very suitable choice because Asyncio is designed to handle I/O-bound and high-level structured network code.
</p>

### Why Asyncio is Suitable for I/O-Bound Project
<b>1. Non-blocking I/O Operations </b>
<p style="margin-left: 40px;">
asyncio allows us to write non-blocking code that can handle other tasks while waiting for I/O operations to complete. This is perfect for scenarios where we have to wait for client responses.
</p>

<b>2. Efficient Use of Time</b>
<p style="margin-left: 40px;">
While an order is in its idle/waiting period, the asyncio event loop can handle other tasks, such as processing new orders or managing other orders' pick-ups.
</p>

<b>3. Scalability</b>
<p style="margin-left: 40px;">
Handling multiple I/O-bound tasks concurrently can scale much better with asyncio than using a multi-threaded approach, especially when the number of concurrent tasks is high.
</p>

<b>4. Structured Concurrency</b>
<p style="margin-left: 40px;">
With asyncio, you can structure your code in a way that is readable and maintainable, using async functions and await statements.
</p>

### Why Asyncio is better than Multi-threaded

<b>1. Single-Threaded Event Loop </b>
<p style="margin-left: 40px;">
asyncio uses a single-threaded event loop to manage I/O-bound tasks, which can be more efficient than multi-threading for I/O-bound operations. This is because the event loop can switch between tasks at await points without the overhead of thread context switching. In I/O-bound operations where tasks spend most of their time waiting for external I/O operations (like network or file I/O), the event loop can easily switch to another task that is ready to do work, thus utilizing the CPU more effectively.
</p>

<b>2. Avoiding GIL Limitations</b>
<p style="margin-left: 40px;">
 Python's Global Interpreter Lock (GIL) prevents multiple native threads from executing Python bytecodes at once. This means that, in a mu
lti-threaded Python program, even if you have multiple threads, only one thread can execute Python code at a time. However, asyncio being single-threaded doesn't have
 this limitation. It can be more efficient in utilizing a single CPU core for I/O-bound tasks.
 </p>

<b>3. Scalability with High Number of Tasks</b> 
<p style="margin-left: 40px;">
Threads consume system resources like memory and add overhead due to context switching. When the number of concurrent tasks 
is very high, using threads can become inefficient and can lead to resource exhaustion. Asynchronous I/O, on the other hand, can handle thousands of connections concu
rrently with less overhead, as it doesn’t require a separate thread for each connection.
</p>

<b>
4. Better Control Over Concurrency
</b>
<p style="margin-left: 40px;">
asyncio provides more granular control over how tasks are executed and how I/O is handled. This can lead to more efficient utiliza
tion of resources, as the developer can determine when a task yields control back to the event loop and can fine-tune how I/O operations are managed.
</p>

<b>
5. Non-Blocking I/O
</b> 
<p style="margin-left: 40px;">
asyncio allows for non-blocking I/O operations. This means that when a task is waiting for an I/O operation to complete (like waiting for pickup time), it can yield control so that other tasks can run. In contrast, in a traditional multi-threaded approach, a thread would block while waiting for the I/O operation to complete, which is less efficient.
</p>


