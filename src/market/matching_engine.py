from src.market.events import OrderExecutedEvent, TransactionEvent, OrderCancelledEvent, LimitOrderStoredEvent
from src.market.transaction import Transaction
from src.market.event_bus import EventBus

class MatchingEngine:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus

    def execute_order(self, order, order_book, timestamp):
        if order.order_type == 'market':
            self.match_order(order, order_book, is_market_order=True, timestamp=timestamp)

        elif order.order_type == 'limit':
            self.match_order(order, order_book, is_market_order=False, timestamp=timestamp)

            if order.quantity > 0:
                if order_book.add_order(order):
                    self.event_bus.publish(LimitOrderStoredEvent(timestamp=timestamp, order=order))

        else:
            raise ValueError(f"Unknown order type: {order.order_type}")

    def match_order(self, order, order_book, is_market_order, timestamp):

        while order.quantity > 0:

            best_order = order_book.top_ask() if order.side == 'buy' else order_book.top_bid()

            if best_order is None:
                break

            if not is_market_order:
                if order.side == 'buy' and order.price < best_order.price:
                    break
                if order.side == 'sell' and order.price > best_order.price:
                    break
 
            traded_quantity = min(order.quantity, best_order.quantity)
            trade_price = best_order.price

            transaction = Transaction(
                order_buy_id=order.order_id if order.side == 'buy' else best_order.order_id,
                order_sell_id=best_order.order_id if order.side == 'buy' else order.order_id,
                buyer_id=order.agent_id if order.side == 'buy' else best_order.agent_id,
                seller_id=best_order.agent_id if order.side == 'buy' else order.agent_id,
                price=trade_price,
                quantity=traded_quantity,
                timestamp=order.timestamp
            )

            self.event_bus.publish(TransactionEvent(timestamp=transaction.timestamp, transaction=transaction))

            if order_book.modify_order(best_order.order_id, best_order.quantity - traded_quantity):
                self.event_bus.publish(OrderExecutedEvent(timestamp=timestamp, order=best_order, executed_quantity=traded_quantity)) 
            else:
                raise ValueError(f"Order {best_order.order_id} not found in order book")
            
            #manually modify the order quantity (is't not stored in the order book at this stage)
            order.modify_quantity(order.quantity - traded_quantity)
            self.event_bus.publish(OrderExecutedEvent(timestamp=timestamp, order=order, executed_quantity=traded_quantity))

    def cancel_order(self, order_id, order_book, timestamp):
        order = order_book.remove_order(order_id)
        if order:
            self.event_bus.publish(OrderCancelledEvent(timestamp=timestamp, order = order))
