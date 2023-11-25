import asyncio

class StorageUnit:
    def __init__(self, capacity, temperature):
        self.capacity = capacity
        self.temperature = temperature
        self.orders = []
        self.lock = asyncio.Lock()

    async def add_order(self, order):
        try:
            async with self.lock:
                if len(self.orders) < self.capacity:
                    self.orders.append(order)
                    return True
            return False
        except Exception as e:
            # Handle specific exceptions or a general exception
            print(f"Error adding order: {e}")
            # Optionally re-raise the exception if you want it to be handled further up the call stack
            raise

    async def remove_order(self, order_id):
        try:
            async with self.lock:
                order_to_remove = next((order for order in self.orders if order.id == order_id), None)
                if order_to_remove:
                    self.orders.remove(order_to_remove)
                    return True
            return False
        except Exception as e:
            print(f"Error removing order: {e}")
            raise
    
    async def has_space(self):
        return len(self.orders) < self.capacity

    async def is_full(self):
        try:
            return len(self.orders) >= self.capacity
        except Exception as e:
            print(f"Error checking if storage is full: {e}")
            raise


