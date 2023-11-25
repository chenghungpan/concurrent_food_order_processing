# manager.py
from .storage import StorageUnit
from .models import Order
import time

MAX_REQUEUE_ATEMPTS = 3

class OrderManager:
    def __init__(self):
        self.cooler = StorageUnit(6, 'cold')
        self.heater = StorageUnit(6, 'hot')
        self.shelf = StorageUnit(12, 'room')

    async def place_order(self, order):
        actions = []
        # Try to place the order and append the action
        placed = await self.try_place_order_in_unit(order)
        if placed:
            actions.append(self.create_action(order.id, "place", additional_info=order.temperature))
            with open("./tests/sim_order.log","a") as logfile:
                logfile.write(f"action={actions[-1]}\n")
        else:
            # if heater/cooler is full, place at shelf
            if await self.shelf.has_space():
                await self.shelf.add_order(order)
                actions.append(self.create_action(order.id, "place", additional_info=order.temperature))
                with open("./tests/sim_order.log","a") as logfile:
                    logfile.write(f"action={actions[-1]}\n")
            else:
                # shelf is also full, discard some old order
                discard_action = await self.discard_order_from_shelf()
                if discard_action:
                        actions.append(discard_action)
                        
                        with open("./tests/sim_order.log","a") as logfile:
                            logfile.write(f"action={actions[-1]}\n")
                            logfile.write(f"# shelf order ={len(self.shelf.orders)}\n")
                            logfile.write(f"# heater order ={len(self.heater.orders)}\n")
                            logfile.write(f"# cooler order ={len(self.cooler.orders)}\n")

                        await self.shelf.add_order(order)
                        actions.append(self.create_action(order.id, "place", additional_info=order.temperature))  # Re-attempt to place order
                        with open("./tests/sim_order.log","a") as logfile:
                            logfile.write(f"action={actions[-1]}\n")
                        

        with open("./tests/sim_order.log","a") as logfile:
            logfile.write(f"# shelf order ={len(self.shelf.orders)}\n")
            logfile.write(f"# heater order ={len(self.heater.orders)}\n")
            logfile.write(f"# cooler order ={len(self.cooler.orders)}\n")
        return actions

    # Create an action dictionary
    def create_action(self, order_id, action_type, additional_info=""):
        return {
            "timestamp": int(time.time() * 1e6),
            "id": order_id,
            "action": action_type,
            "additional_info": additional_info
        }
    

    async def try_place_order_in_unit(self, order):
        # Try to place the order in the correct storage unit based on temperature
        target_unit = self._get_target_unit(order.temperature)
        if await target_unit.add_order(order):
            return True
        else:
            return False
    

    async def move_order_to_shelf(self, target_temperature):
        # Try to move an order from the target unit (cooler/heater) to the shelf
        target_unit = self._get_target_unit(target_temperature)
        for order in target_unit.orders:
            if await self.shelf.has_space():
                await target_unit.remove_order(order.id)
                await self.shelf.add_order(order)
                return {
                    "timestamp": int(time.time() * 1e6),  # Timestamp in microseconds
                    "id": order.id,
                    "action": "move",
                    "additional_info": f"Moved from {target_temperature} unit to shelf"
                }
        return False  # No suitable order to move or shelf is full

    
    async def move_order_from_shelf(self, target_temperature):
        target_unit = self._get_target_unit(target_temperature)
        for order in self.shelf.orders:
            if order.temperature == target_temperature and await target_unit.has_space():
                await self.shelf.remove_order(order.id)
                await target_unit.add_order(order)
                return {
                    "timestamp": int(time.time() * 1e6),  # Timestamp in microseconds
                    "id": order.id,
                    "action": "move",
                    "additional_info": f"Moved from shelf to {target_temperature} unit"
                }
        return None  # Return None if no order was moved

    def _get_target_unit(self, temperature):
        if temperature == 'cold':
            return self.cooler
        elif temperature == 'hot':
            return self.heater
        return self.shelf
    

    async def discard_order_from_shelf(self):
        if self.shelf.orders:
            # DEBUG----
            for order in self.shelf.orders:
                print(order.id, order.name, order.temperature, order.freshness)
            # /DEBUG ---
            
            least_fresh_order = min(self.shelf.orders, key=lambda o: o.freshness)
            await self.shelf.remove_order(least_fresh_order.id)
            return {
                "timestamp": int(time.time() * 1e6),
                "id": least_fresh_order.id,
                "action": "discard",
                "freshness": least_fresh_order.freshness
            }
        return None  # Return None if no order was discarded


    async def pickup_order(self, order):
        with open("./tests/sim_order.log","a") as logfile:
            logfile.write(f"order_id={order.id}\n")
        actions = []
        # Logic to remove orders from storage units


        if await self.cooler.remove_order(order.id):
            # with open("./tests/sim_order.log","a") as logfile:
            #     logfile.write('*** pickup from cooler\n')
            actions.append(self.create_action(order.id, "pickup", additional_info=f"from cooler: {order.temperature}\n"))
  
        elif await self.heater.remove_order(order.id):
            # with open("./tests/sim_order.log","a") as logfile:
            #     logfile.write('*** pickup from heater\n')
            actions.append(self.create_action(order.id, "pickup", additional_info=f"from heater: {order.temperature}\n"))

        elif await self.shelf.remove_order(order.id):
            # with open("./tests/sim_order.log","a") as logfile:
            #     logfile.write('*** pickup from shelf\n')
            actions.append(self.create_action(order.id, "pickup", additional_info=f"from shelf: {order.temperature}\n"))

        with open("./tests/sim_order.log","a") as logfile:
            logfile.write(f"action={actions}\n")
            logfile.write(f"# shelf order ={len(self.shelf.orders)}\n")
            logfile.write(f"# heater order ={len(self.heater.orders)}\n")
            logfile.write(f"# cooler order ={len(self.cooler.orders)}\n")


        return actions
    

    async def optimize_shelf_usage(self, actions):
        # Move orders from shelf to heater or cooler if space is available
    
        for order in self.shelf.orders[:]:  # Iterate over a copy of the list
            target_unit = self._get_target_unit(order.temperature)
            if ((target_unit.temperature=='hot') or (target_unit.temperature=='cold')) and await target_unit.has_space():
                await self.shelf.remove_order(order.id)
                await target_unit.add_order(order)
                # Record the 'move' action
                move_action = self.create_action(order.id, "move", f"Moved to {target_unit.temperature} unit")
                print('OPTIMIZE actions:', move_action)
                actions.append(move_action)
        return actions

    async def get_all_orders(self):
        # Combine all orders from cooler, heater, and shelf into one list
        all_orders = []
        all_orders.extend(self.cooler.orders)
        all_orders.extend(self.heater.orders)
        all_orders.extend(self.shelf.orders)
        return all_orders

  