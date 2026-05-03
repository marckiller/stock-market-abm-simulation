import json


class EventLogger:
    def __init__(self, event_bus):
        self.records = []
        self._sequence = 0

        event_bus.subscribe('transaction', self.log_event)
        event_bus.subscribe('limit_order_stored', self.log_event)
        event_bus.subscribe('order_executed', self.log_event)
        event_bus.subscribe('order_cancelled', self.log_event)

    def log_event(self, event):
        self.records.append(self._serialize_event(event))
        self._sequence += 1

    def to_records(self):
        return [record.copy() for record in self.records]

    def clear(self):
        self.records.clear()
        self._sequence = 0

    def to_jsonl(self, path):
        with open(path, 'w') as file:
            for record in self.records:
                file.write(json.dumps(record) + '\n')

    def _serialize_event(self, event):
        record = {
            'sequence': self._sequence,
            'event_type': event.event_type,
            'timestamp': event.timestamp,
        }

        if event.event_type == 'transaction':
            record.update(self._serialize_transaction(event.transaction))
            return record

        if hasattr(event, 'order'):
            record.update(self._serialize_order(event.order))

        if hasattr(event, 'executed_quantity'):
            record['executed_quantity'] = event.executed_quantity

        return record

    def _serialize_order(self, order):
        return {
            'order_id': order.order_id,
            'agent_id': order.agent_id,
            'order_timestamp': order.timestamp,
            'side': order.side,
            'order_type': order.order_type,
            'quantity': order.quantity,
            'price': order.price,
        }

    def _serialize_transaction(self, transaction):
        return {
            'order_buy_id': transaction.order_buy_id,
            'order_sell_id': transaction.order_sell_id,
            'buyer_id': transaction.buyer_id,
            'seller_id': transaction.seller_id,
            'transaction_timestamp': transaction.timestamp,
            'price': transaction.price,
            'quantity': transaction.quantity,
        }
