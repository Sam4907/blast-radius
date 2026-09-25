def charge_card(user, amount):
    print("Charging card")
    return True

def refund(user, amount):
    print("Refunding")
    return True
from stripe_api import process

def process_payment(user, amount):
    print("Processing payment in billing...")
    process(user, amount)
