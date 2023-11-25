# simulator.py
import random
import asyncio
import time
from .models import Order
from .manager import OrderManager

import random
import asyncio
from .models import Order

async def simulate_order_placement(orders_data, order_manager, placement_rate):
    actions = []
    for order in orders_data:
        order = Order(
            id=order["id"],
            name=order["name"],
            temperature=order["temp"],
            freshness=order["freshness"]
        )
        try:
            # place_order now returns a list of actions (place, move, discard)
            order_actions = await order_manager.place_order(order)
            actions.extend(order_actions)  # Add all actions related to this order
            await asyncio.sleep(1 / placement_rate)
        except Exception as e:
            print(f"Error in placing order {order.id}: {e}")
            # Handle or log the error appropriately

    return actions



async def pickup_order(order_manager, order, pickup_time, actions):
    
    try:
        await asyncio.sleep(pickup_time / 1000000)
        with open("./tests/sim_order.log","a") as logfile:
            logfile.write(f"order={order.id}")
        order_actions = await order_manager.pickup_order(order)
        actions.extend(order_actions)
    except Exception as e:
        print(f"Error in picking up order {order.id}: {e}")


async def simulate_order_pickup(order_manager, pickup_min, pickup_max):
    import time
    actions = []
    pickup_tasks = {}
    processed_orders = set()
    last_non_empty_time = time.time()  # Initialize time tracker

    all_orders = await order_manager.get_all_orders()

    # for order in all_orders:
    while True:
        
        all_orders = await order_manager.get_all_orders()

        if len(all_orders) > 0: 
            last_non_empty_time = time.time()
            for order in all_orders:
                if order.id not in processed_orders:
                    new_orders = True
                    # with open("./tests/sim_order.log","a") as logfile:
                    #     logfile.write(f"size of all_orders={len(all_orders)}")
                    # await order_manager.optimize_shelf_usage(actions)   #DEBUG
                    pickup_time = random.uniform(pickup_min, pickup_max)
                    # with open("./tests/sim_order.log","a") as logfile:
                    #     logfile.write(f"pickup_order{order.id}, {order.temperature}, {round(pickup_time/1000000,2)}")
                    task = asyncio.create_task(pickup_order(order_manager, order, pickup_time, actions))
                    pickup_tasks[order.id] = task
                    processed_orders.add(order.id)
        else:
            if time.time() - last_non_empty_time > 5:
                break   # Break if it's been 5 seconds since last non-empty all_orders

        await asyncio.sleep(0.01)

    # Wait for all pickup tasks to complete and handle exceptions
    results = await asyncio.gather(*pickup_tasks.values(), return_exceptions=True)
    for result in results:
        if isinstance(result, Exception):
            print(f"A pickup task failed with an exception: {result}")
            # Handle the exception as needed

    return actions



