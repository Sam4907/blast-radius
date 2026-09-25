from notifications import send_email

def ship_order(order_id, user):
    print(f"Shipping order {order_id}")
    send_email(user)
