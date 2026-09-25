from billing import charge_card, refund
from notifications import send_email

def complete_order(order_id):
    charge_card("bob", 200)
    send_email("bob")

def cancel_order(order_id):
    refund("bob", 200)
    send_email("bob")
