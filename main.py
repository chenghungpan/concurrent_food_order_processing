# main.py
import os
import asyncio 
from dotenv import load_dotenv
from food_order.api import get_new_problem, submit_solution
from food_order.manager import OrderManager 
from food_order.simulator import simulate_order_placement, simulate_order_pickup
import json

# Load environment variables from .env file
load_dotenv()

# Retrieve the AUTH_TOKEN from the environment
AUTH_TOKEN = os.getenv('CHALLENGE_SERVER_AUTH_TOKEN')

# Retrieve simulation options from the environment
placement_rate = int(os.getenv('PLACEMENT_RATE', '2'))  # Providing default value as '2'
inverse_order_rate = int(os.getenv('INVERSE_ORDER_RATE', '500000'))  # Providing default value as '500000'
min_pickup_time = int(os.getenv('MIN_PICKUP_TIME', '4000000'))  # Providing default value as '4000000'
max_pickup_time = int(os.getenv('MAX_PICKUP_TIME', '8000000'))  # Providing default value as '8000000'

from datetime import datetime

def calculate_durations(all_actions):
    # Convert the list of actions to a dictionary keyed by order ID
    # Each order ID will map to another dictionary with 'place' and 'pickup' timestamps
    # Then display the pickup delay for each order ID. 
    order_times = {}

    log_message = 'Summary of Pickup Delays'
    with open("./tests/sim_order.log","a") as logfile:
        logfile.write('\n')
        logfile.write('='*40)
        logfile.write('\n')
        logfile.write(log_message + "\n")
        logfile.write('='*40)
        logfile.write('\n')

    for action in all_actions:
        order_id = action['id']
        if order_id not in order_times:
            order_times[order_id] = {'place': None, 'pickup': None}
        # Convert timestamp from microseconds to seconds
        timestamp = action['timestamp'] / 1e6
        if action['action'] == 'place':
            order_times[order_id]['place'] = timestamp
        elif action['action'] == 'pickup':
            order_times[order_id]['pickup'] = timestamp

    # Calculate the delay for each order
    for order_id, times in order_times.items():
        if times['place'] and times['pickup']:
            placed_time = datetime.fromtimestamp(times['place'])
            picked_up_time = datetime.fromtimestamp(times['pickup'])
            delay = picked_up_time - placed_time

            log_message=f"Order {order_id} delay: {delay.total_seconds()} seconds"
            with open("./tests/sim_order.log","a") as logfile:
                logfile.write(log_message + "\n")

        else:
            log_message=f"Order {order_id} has incomplete actions and cannot have delay calculated."
            with open("./tests/sim_order.log","a") as file:
                logfile.write(log_message + "\n")


async def main():

    
    log_message ='*'*100
    with open("./tests/sim_order.log","w") as logfile:
        logfile.write(log_message + "\n")

    order_manager = OrderManager()

    # Fetch a new test problem from the Challenge Server
    test_id, orders = await get_new_problem(AUTH_TOKEN,4)
    if not test_id or not orders:
        print("Failed to fetch new problem.")
        return

    log_message = f"Fetched new problem with Test ID: {test_id}"
    with open("./tests/sim_order.log","a") as logfile:
        logfile.write(log_message + "\n")
        logfile.write(f"size of placed orders= {len(orders)}\n")
        orders_json = json.dumps(orders, indent=4)
        logfile.write(orders_json)
        logfile.write('\n\n')



    # Start both tasks concurrently
    placement_task = asyncio.create_task(simulate_order_placement(orders, order_manager, placement_rate))
    pickup_task =    asyncio.create_task(simulate_order_pickup   (order_manager, min_pickup_time, max_pickup_time))

    # Wait for both tasks to complete
    placement_actions, pickup_actions = await asyncio.gather(placement_task, pickup_task)

    all_actions = placement_actions + pickup_actions

    calculate_durations(all_actions)

    final_actions =  sorted(all_actions, key=lambda x: x['timestamp'])


    actions_json = json.dumps(final_actions,indent=4)
    file_path = './tests/output_actions.json'
    with open(file_path, 'w') as file:
        file.write(actions_json)

    # Options for the simulation are retrieved from the .env file
    options = {
        "rate": inverse_order_rate,  # Inverse order rate (in microseconds)
        "min": min_pickup_time,      # Min pickup time (in microseconds)
        "max": max_pickup_time       # Max pickup time (in microseconds)
    }

    

    # Submit the list of actions to the Challenge Server to solve the problem
    result = await submit_solution(AUTH_TOKEN, test_id, final_actions, options)

    print(f"Result of submission: {result}")
    print('Please verify detailed log file at ./tests/sim_order.log')

    log_message=f"Result of submission: {result}"
    with open("./tests/sim_order.log","a") as logfile:
        logfile.write('\n')
        logfile.write('='*40)
        logfile.write('\n')
        logfile.write(log_message + "\n")
        logfile.write('='*40)
        logfile.write('\n')

if __name__ == '__main__':
    asyncio.run(main())

