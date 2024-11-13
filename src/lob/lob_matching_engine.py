from typing import List
from src.lob.lob_limit_order_book import LimitOrderBook
from src.order.order import Order
from src.order.order_limit import OrderLimit
from src.order.order_market import OrderMarket
from src.order.order import OrderSide

from src.event.event import Event
from src.event.events.event_transaction import EventTransaction
from src.event.events.event_order_executed import EventOrderExecuted
from src.event.events.event_order_modified import EventOrderModified

class MatchingEngine:

    def process_order(self, order: Order, lob: LimitOrderBook, timestamp: int, trigger_event_id: int) -> List[Event]:
        if isinstance(order, OrderMarket):
            if order.side == OrderSide.BUY:
                return self.process_market_buy_order(order, lob, timestamp, trigger_event_id)
            else:
                return self.process_market_sell_order(order, lob, timestamp, trigger_event_id)
        elif isinstance(order, OrderLimit):
            if order.side == OrderSide.BUY:
                return self.process_limit_buy_order(order, lob, timestamp, trigger_event_id)
            else:
                return self.process_limit_sell_order(order, lob, timestamp, trigger_event_id)
        else:
            raise ValueError(f"Unsupported order type: {order}")
    
    def process_market_buy_order(self, order: OrderMarket, lob: LimitOrderBook, timestamp: int, trigger_event_id: int) -> List[Event]:
        events = []
        best_ask = lob.best_ask()

        while order.quantity > 0 and best_ask is not None:
            order_ask, ask_events = lob.pop_top_ask_at_price(best_ask, timestamp, trigger_event_id)
            events += ask_events
            price = order_ask.price
            quantity = min(order.quantity, order_ask.quantity)
            events.append(EventTransaction(timestamp, trigger_event_id, order_ask.ticker, quantity, price, order.agent_id, order_ask.agent_id, order.order_id, order_ask.order_id))
            order.quantity -= quantity
            order_ask.quantity -= quantity

            if order_ask.quantity > 0:
                events.append(EventOrderModified(
                    timestamp, trigger_event_id, order_ask.ticker,
                    order_ask.order_id, order_ask.quantity + quantity, order_ask.quantity
                ))
                events += lob.add_ask(order_ask, timestamp, trigger_event_id)
            else:
                events.append(EventOrderExecuted(
                    timestamp, trigger_event_id, order_ask.ticker, order_ask.order_id, order_ask.agent_id
                ))

            if order.quantity > 0:
                events.append(EventOrderModified(
                    timestamp, trigger_event_id, order.ticker,
                    order.order_id, order.quantity + quantity, order.quantity
                ))
                best_ask = lob.best_ask()
            else:
                events.append(EventOrderExecuted(
                    timestamp, trigger_event_id, order.ticker, order.order_id, order.agent_id
                ))
                break

        return events

    def process_market_sell_order(self, order: OrderMarket, lob: LimitOrderBook, timestamp: int, trigger_event_id: int) -> List[Event]:
        events = []
        best_bid = lob.best_bid()

        while order.quantity > 0 and best_bid is not None:

            order_bid, bid_events = lob.pop_top_bid_at_price(best_bid, timestamp, trigger_event_id)
            events += bid_events
            price = order_bid.price
            quantity = min(order.quantity, order_bid.quantity)
            events.append(EventTransaction(timestamp, trigger_event_id, order_bid.ticker, quantity, price, order.agent_id, order_bid.agent_id, order.order_id, order_bid.order_id))
            order.quantity -= quantity
            order_bid.quantity -= quantity

            if order_bid.quantity > 0:
                events.append(EventOrderModified(
                    timestamp, trigger_event_id, order_bid.ticker,
                    order_bid.order_id, order_bid.quantity + quantity, order_bid.quantity
                ))
                events += lob.add_bid(order_bid, timestamp, trigger_event_id)
            else:
                events.append(EventOrderExecuted(
                    timestamp, trigger_event_id, order_bid.ticker, order_bid.order_id, order_bid.agent_id
                ))

            if order.quantity > 0:
                events.append(EventOrderModified(
                    timestamp, trigger_event_id, order.ticker,
                    order.order_id, order.quantity + quantity, order.quantity
                ))
                best_bid = lob.best_bid()
            else:
                events.append(EventOrderExecuted(
                    timestamp, trigger_event_id, order.ticker, order.order_id, order.agent_id
                ))
                break

        return events

    def process_limit_buy_order(self, order: OrderLimit, lob: LimitOrderBook, timestamp: int, trigger_event_id: int) -> List[Event]:
        events = []
        best_ask = lob.best_ask()

        if best_ask is None or best_ask > order.price:
            events += lob.add_bid(order, timestamp, trigger_event_id)
        else:
            while order.quantity > 0 and best_ask is not None and best_ask <= order.price:
                order_ask, ask_events = lob.pop_top_ask_at_price(best_ask, timestamp, trigger_event_id)
                events += ask_events
                price = order_ask.price
                quantity = min(order.quantity, order_ask.quantity)
                events.append(EventTransaction(timestamp, trigger_event_id, order_ask.ticker, quantity, price, order.agent_id, order_ask.agent_id, order.order_id, order_ask.order_id))
                order.quantity -= quantity
                order_ask.quantity -= quantity

                if order_ask.quantity > 0:
                    events.append(EventOrderModified(
                        timestamp, trigger_event_id, order_ask.ticker,
                        order_ask.order_id, order_ask.quantity + quantity, order_ask.quantity
                    ))
                    events += lob.add_ask(order_ask, timestamp, trigger_event_id)
                else:
                    events.append(EventOrderExecuted(
                        timestamp, trigger_event_id, order_ask.ticker, order_ask.order_id, order_ask.agent_id
                    ))

                if order.quantity > 0:
                    events.append(EventOrderModified(
                        timestamp, trigger_event_id, order.ticker,
                        order.order_id, order.quantity + quantity, order.quantity
                    ))
                    best_ask = lob.best_ask()
                else:
                    events.append(EventOrderExecuted(
                        timestamp, trigger_event_id, order.ticker, order.order_id, order.agent_id
                    ))
                    break

            if order.quantity > 0:
                events += lob.add_bid(order, timestamp, trigger_event_id)

        return events

    def process_limit_sell_order(self, order: OrderLimit, lob: LimitOrderBook, timestamp: int, trigger_event_id: int) -> List[Event]:
        events = []
        best_bid = lob.best_bid()

        if best_bid is None or best_bid < order.price:
            events += lob.add_ask(order, timestamp, trigger_event_id)
        else:
            while order.quantity > 0 and best_bid is not None and best_bid >= order.price:
                order_bid, bid_events = lob.pop_top_bid_at_price(best_bid, timestamp, trigger_event_id)
                events += bid_events
                price = order_bid.price
                quantity = min(order.quantity, order_bid.quantity)
                events.append(EventTransaction(timestamp, trigger_event_id, order.ticker, quantity, price, order.agent_id, order_bid.agent_id, order.order_id, order_bid.order_id))
                order.quantity -= quantity
                order_bid.quantity -= quantity

                if order_bid.quantity > 0:
                    events.append(EventOrderModified(
                        timestamp, trigger_event_id, order_bid.ticker,
                        order_bid.order_id, order_bid.quantity + quantity, order_bid.quantity
                    ))
                    events += lob.add_bid(order_bid, timestamp, trigger_event_id)
                else:
                    events.append(EventOrderExecuted(
                        timestamp, trigger_event_id, order_bid.ticker, order_bid.order_id, order_bid.agent_id
                    ))

                if order.quantity > 0:
                    events.append(EventOrderModified(
                        timestamp, trigger_event_id, order.ticker,
                        order.order_id, order.quantity + quantity, order.quantity
                    ))
                    best_bid = lob.best_bid()
                else:
                    events.append(EventOrderExecuted(
                        timestamp, trigger_event_id, order.ticker, order.order_id, order.agent_id
                    ))
                    break

            if order.quantity > 0:
                events += lob.add_ask(order, timestamp, trigger_event_id)

        return events
