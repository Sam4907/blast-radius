from billing import process_payment

def initiate_payment(user, amount):
    print("Initiating payment...")
    process_payment(user, amount)
