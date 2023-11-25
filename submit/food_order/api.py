# api.py
import aiohttp
from .config import CHALLENGE_SERVER_BASE_URL, AUTH_TOKEN
import json

def calculate_durations(all_actions):
    from datetime import datetime
    # Convert the list of actions to a dictionary keyed by order ID
    # Each order ID will map to another dictionary with 'place' and 'pickup' timestamps
    order_times = {}
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
            print(f"Order {order_id} delay: {delay.total_seconds()} seconds")
        else:
            print(f"Order {order_id} has incomplete actions and cannot have delay calculated.")



async def get_new_problem(token=None, seed=None, name=None):
    url = f"{CHALLENGE_SERVER_BASE_URL}/interview/challenge/new"
    params = {'auth': token}
    if seed:
        params['seed'] = seed
    if name:
        params['name'] = name

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                test_id = response.headers.get('x-test-id')
                orders = await response.json()
                return test_id, orders
            else:
                # Handle error response
                text = await response.text()
                print(f"Error {response.status}: {text}")
                return None, None


async def submit_solution(token, test_id, actions, options):
    url = f"{CHALLENGE_SERVER_BASE_URL}/interview/challenge/solve"
    headers = {
        'Content-Type': 'application/json',
        'x-test-id': test_id
    }
    params = {'auth': token}
    data = {
        'options': options,
        'actions': actions
    }
    
  
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data, headers=headers, params=params) as response:
            if response.status == 200:
                return await response.text()
            else:
                # Handle error responses
                text = await response.text()
                print(f"Error {response.status}: {text}")
                return None
                
