import unittest
from src.market.responses import (LimitOrderStoredResponse, OrderExecutedResponse,
                         OrderCancelledResponse, Transaction)

class TestLimitOrderStoredResponse(unittest.TestCase):
    def test_initialization(self):
        response = LimitOrderStoredResponse(order_id=1, agent_id=100, quantity=50)
        self.assertEqual(response.order_id, 1)
        self.assertEqual(response.agent_id, 100)
        self.assertEqual(response.quantity, 50)

    def test_str_representation(self):
        response = LimitOrderStoredResponse(order_id=1, agent_id=100, quantity=50)
        self.assertEqual(str(response), "Order 1 stored for agent 100")


class TestOrderExecutedResponse(unittest.TestCase):
    def test_initialization(self):
        response = OrderExecutedResponse(order_id=2, agent_id=101, remaining_quantity=20)
        self.assertEqual(response.order_id, 2)
        self.assertEqual(response.agent_id, 101)
        self.assertEqual(response.remaining_quantity, 20)

    def test_str_representation(self):
        response = OrderExecutedResponse(order_id=2, agent_id=101, remaining_quantity=20)
        self.assertEqual(str(response), "Order 2 executed for agent 101")


class TestOrderCancelledResponse(unittest.TestCase):
    def test_initialization(self):
        response = OrderCancelledResponse(order_id=3, agent_id=102)
        self.assertEqual(response.order_id, 3)
        self.assertEqual(response.agent_id, 102)

    def test_str_representation(self):
        response = OrderCancelledResponse(order_id=3, agent_id=102)
        self.assertEqual(str(response), "Order 3 cancelled for agent 102")


class TestTransaction(unittest.TestCase):
    def test_initialization(self):
        transaction = Transaction(order_buy_id=1, order_sell_id=2, buyer_id=100, seller_id=101,
                                   price=50.5, quantity=10, timestamp=1633058000.0)
        self.assertEqual(transaction.order_buy_id, 1)
        self.assertEqual(transaction.order_sell_id, 2)
        self.assertEqual(transaction.buyer_id, 100)
        self.assertEqual(transaction.seller_id, 101)
        self.assertEqual(transaction.price, 50.5)
        self.assertEqual(transaction.quantity, 10)
        self.assertEqual(transaction.timestamp, 1633058000.0)

    def test_str_representation(self):
        transaction = Transaction(order_buy_id=1, order_sell_id=2, buyer_id=100, seller_id=101,
                                   price=50.5, quantity=10, timestamp=1633058000.0)
        self.assertEqual(
            str(transaction),
            "Transaction: 10 units at 50.5. Buyer: 100, Seller: 101"
        )