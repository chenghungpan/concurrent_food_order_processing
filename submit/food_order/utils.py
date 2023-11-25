# food_order/utils.py

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

def log_action(action, order_id):
    logger.info(f"Action: {action}, Order ID: {order_id}")


