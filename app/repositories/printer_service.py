from app.repositories.interfaces import IPrinterService

class PrinterService(IPrinterService):
    """Сервіс, що відповідає виключно за комунікацію з обладнанням друку."""
    def send_to_printer(self, printer_id: str, payload: dict) -> bool:
        print(f"Sending payload to printer {printer_id}")
        return True