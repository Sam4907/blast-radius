from billing import charge_card, refund
from notifications import log_transaction
from shipping import ship_order

def complete_order(order_id):
    charge_card("carol", 300)
    ship_order(order_id, "carol")
    log_transaction(order_id)

def cancel_order(order_id):
    refund("carol", 300)
    log_transaction(order_id)

from payment_gateway import initiate_payment

def complete_order(order_id):
    print(f"Completing order {order_id}")
    initiate_payment("dave", 400)
