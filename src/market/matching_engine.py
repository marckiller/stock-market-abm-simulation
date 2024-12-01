from src.market.responses import OrderExecutedResponse, LimitOrderStoredResponse, Transaction

class MatchingEngine:
    """
    Handles the matching of orders (both market and limit) with the opposite side of the order book.
    Responsible for executing trades and maintaining the integrity of the order book.
    """
    def __init__(self):
        pass

    def execute_order(self, order, order_book):
        """
        Processes an order (market or limit) and attempts to match it with the opposite side of the book.

        Args:
            order (Order): The incoming order to be processed.
            order_book (LimitOrderBook): The order book to match the order against.

        Returns:
            tuple: A pair containing:
                - A list of Transaction objects for completed trades.
                - A list of responses indicating the results of the operation.
        """
        transactions = []
        responses = []

        if order.order_type == 'market':
            # Market orders are executed immediately at the best available price
            matched_transactions, matched_responses = self.match_order(order, order_book, is_market_order=True)
            transactions.extend(matched_transactions)
            responses.extend(matched_responses)
        elif order.order_type == 'limit':
            # Limit orders try to match first; any remaining part is added to the book
            matched_transactions, matched_responses = self.match_order(order, order_book, is_market_order=False)
            transactions.extend(matched_transactions)
            responses.extend(matched_responses)

            # If there is still unfilled quantity, add it to the book
            if order.quantity > 0:
                add_response = order_book.add_order(order)
                responses.append(add_response)
        else:
            raise ValueError(f"Unknown order type: {order.order_type}")

        return transactions, responses

    def match_order(self, order, order_book, is_market_order):
        """
        Matches an incoming order with orders on the opposite side of the order book.

        Args:
            order (Order): The incoming order to be matched.
            order_book (LimitOrderBook): The order book containing orders to match against.
            is_market_order (bool): Whether the incoming order is a market order.

        Returns:
            tuple: A pair containing:
                - A list of Transaction objects for completed trades.
                - A list of responses indicating the results of the operation.
        """
        transactions = []
        responses = []

        while order.quantity > 0:
            # Retrieve the best order on the opposite side of the book
            best_order = order_book.top_ask() if order.side == 'buy' else order_book.top_bid()

            # Stop matching if there are no orders to match against
            if best_order is None:
                break

            # Price validation for limit orders
            if not is_market_order:
                if order.side == 'buy' and order.price < best_order.price:
                    break  # Buy order cannot afford the ask price
                if order.side == 'sell' and order.price > best_order.price:
                    break  # Sell order cannot match the bid price

            # Determine the trade details
            traded_quantity = min(order.quantity, best_order.quantity)
            trade_price = best_order.price

            # Record the transaction
            transaction = Transaction(
                order_buy_id=order.order_id if order.side == 'buy' else best_order.order_id,
                order_sell_id=best_order.order_id if order.side == 'buy' else order.order_id,
                buyer_id=order.agent_id if order.side == 'buy' else best_order.agent_id,
                seller_id=best_order.agent_id if order.side == 'buy' else order.agent_id,
                price=trade_price,
                quantity=traded_quantity,
                timestamp=order.timestamp
            )
            transactions.append(transaction)

            # Update quantities using order_book methods
            # For the best_order in the book
            if best_order.quantity == traded_quantity:
                order_book.remove_order(best_order.order_id)
            else:
                order_book.modify_order(best_order.order_id, best_order.quantity - traded_quantity)

            # For the incoming order, adjust the quantity directly
            # Since it's not in the order_book yet
            order.quantity -= traded_quantity

            # Add responses for the executed orders
            responses.append(OrderExecutedResponse(order.order_id, order.agent_id, order.quantity))
            responses.append(OrderExecutedResponse(best_order.order_id, best_order.agent_id,
                                                best_order.quantity if best_order.quantity != traded_quantity else 0))

        return transactions, responses
