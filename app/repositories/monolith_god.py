from app.db import db

class MonolithGodObject:
    def __init__(self):
        self.db = db

    def process_order_and_print_and_user(self, order_data, printer_id, user_data):
        print("Processing order...")
        print(f"Sending to printer {printer_id}...")
        print(f"Registering user {user_data.get('name')}...")
        return {"status": "monolith_success", "data": (order_data, printer_id, user_data)}