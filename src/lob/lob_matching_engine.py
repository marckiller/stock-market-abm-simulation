from typing import List
from src.lob.lob_limit_order_book import LimitOrderBook
from src.order.order import Order
from src.order.order_limit import OrderLimit
from src.order.order_market import OrderMarket
from src.order.order import OrderSide

class MatchingEngine:
    def __init__(self):
        self.transactions = [] #TODO: No need of keeping transaciton history here
                               # Simulation will keep track of transactions by recieveing and saving Event objects
                               # Now this structure is just for testing purposes

    def process_order(self, order: Order, limit_order_book: LimitOrderBook):
        if isinstance(order, OrderLimit):
            self.process_limit_order(order, limit_order_book)
        elif isinstance(order, OrderMarket):
            self.process_market_order(order, limit_order_book)
        else:
            raise ValueError("Unknown order type")

    def process_limit_order(self, order: OrderLimit, limit_order_book: LimitOrderBook):
        opposite_side = OrderSide.SELL if order.side == OrderSide.BUY else OrderSide.BUY
        best_price = limit_order_book.best_ask() if order.side == OrderSide.BUY else limit_order_book.best_bid()

        while order.quantity > 0 and best_price is not None:

            if (order.side == OrderSide.BUY and order.price >= best_price) or \
               (order.side == OrderSide.SELL and order.price <= best_price):

                orders_to_match = limit_order_book.pop_orders_from_given_price_level_to_meet_demand(
                    price=best_price,
                    side=opposite_side,
                    demand=order.quantity
                )

                for matched_order, matched_quantity in orders_to_match:

                    self.transactions.append({
                        'buy_order_id': order.order_id if order.side == OrderSide.BUY else matched_order.order_id,
                        'sell_order_id': matched_order.order_id if order.side == OrderSide.BUY else order.order_id,
                        'price': best_price,
                        'quantity': matched_quantity,
                        'time': order.timestamp 
                    })
                    print(f"Matched {matched_quantity} of Order {matched_order.order_id} with Order {order.order_id} at price {best_price}")

                    order.quantity -= matched_quantity

                    if matched_quantity < matched_order.quantity:
                        remaining_quantity = matched_order.quantity - matched_quantity
                        matched_order.quantity = remaining_quantity
                        limit_order_book.add(matched_order)
                        print(f"Updated Order {matched_order.order_id} with remaining quantity {matched_order.quantity} to the book.")

                best_price = limit_order_book.best_ask() if order.side == OrderSide.BUY else limit_order_book.best_bid()

            else:
                break  

        if order.quantity > 0:
            limit_order_book.add(order)
            print(f"Added remaining Order {order.order_id} with quantity {order.quantity} to the book.")

    def process_market_order(self, order: OrderMarket, limit_order_book: LimitOrderBook):
        opposite_side = OrderSide.SELL if order.side == OrderSide.BUY else OrderSide.BUY
        best_price = limit_order_book.best_ask() if order.side == OrderSide.BUY else limit_order_book.best_bid()

        while order.quantity > 0 and best_price is not None:

            orders_to_match = limit_order_book.pop_orders_from_given_price_level_to_meet_demand(
                price=best_price,
                side=opposite_side,
                demand=order.quantity
            )

            for matched_order, matched_quantity in orders_to_match:
                self.transactions.append({
                    'buy_order_id': matched_order.order_id if order.side == OrderSide.BUY else order.order_id,
                    'sell_order_id': order.order_id if order.side == OrderSide.BUY else matched_order.order_id,
                    'price': best_price,
                    'quantity': matched_quantity,
                    'time': order.timestamp
                })
                print(f"Matched {matched_quantity} of Order {matched_order.order_id} with Market Order {order.order_id} at price {best_price}")

                order.quantity -= matched_quantity

                if matched_quantity < matched_order.quantity:
                    remaining_quantity = matched_order.quantity - matched_quantity
                    matched_order.quantity = remaining_quantity
                    limit_order_book.add(matched_order)
                    print(f"Updated Order {matched_order.order_id} with remaining quantity {matched_order.quantity} to the book.")

            best_price = limit_order_book.best_ask() if order.side == OrderSide.BUY else limit_order_book.best_bid()

        if order.quantity > 0:
            print(f"Market Order {order.order_id} partially filled. Remaining quantity: {order.quantity} not fulfilled.")
