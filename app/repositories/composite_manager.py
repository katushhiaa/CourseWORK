from app.repositories.interfaces import IOrderService, IPrinterService

class CompositeManager:
    """Керуючий компонент, який використовує ін'єкцію залежностей (DI)."""
    def __init__(self, order_service: IOrderService, printer_service: IPrinterService):
        self.order_service = order_service
        self.printer_service = printer_service

    def execute_workflow(self, order_data: dict, printer_id: str):
        res = self.order_service.process_order(order_data)
        self.printer_service.send_to_printer(printer_id, res)
        return {"status": "workflow_success"}