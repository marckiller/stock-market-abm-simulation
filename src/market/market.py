# Market class
from src.market.event_bus import EventBus
from src.market.order import Order
from src.market.order_book import LimitOrderBook
from src.market.matching_engine import MatchingEngine
from src.market.events import OrderCancelledEvent, OrderExecutedEvent, LimitOrderStoredEvent, TransactionEvent

# Managers
from managers.agent_manager import AgentManager
from managers.indicator_manager import IndicatorManager
from managers.market_data_manager import MarketDataManager

class Market:
    def __init__(self, config):
        self.event_bus = EventBus()
        self.order_book = LimitOrderBook()
        self.matching_engine = MatchingEngine(self.event_bus)
        self.market_data = MarketDataManager(
            ohlcv_periods=config.get("ohlcv_periods", []),
            store_tick_data=config.get("store_tick_data", False),
            max_ticks=config.get("max_ticks", 100000)
        )
        self.indicator_manager = IndicatorManager(self.market_data)
        self.agent_manager = AgentManager(self, self.market_data, self.indicator_manager)

        self.event_bus.subscribe('transaction', self.handle_transaction)
        self.event_bus.subscribe('limit_order_stored', self.handle_order_stored)
        self.event_bus.subscribe('order_executed', self.handle_order_executed)
        self.event_bus.subscribe('order_cancelled', self.handle_order_cancelled)

    def register_agent(self, agent):
        self.agent_manager.register_agent(agent)

    def submit_order(self, order: Order):
        timestamp = self.get_current_time()
        self.matching_engine.execute_order(order, self.order_book, timestamp)

    def cancel_order(self, order_id: str):
        timestamp = self.get_current_time()
        self.matching_engine.cancel_order(order_id, self.order_book, timestamp)

    def handle_transaction(self, event: TransactionEvent):
        transaction = event.transaction
        self.agent_manager.handle_transaction(transaction)
        self.market_data.add_tick(
            time=event.timestamp,
            transaction_price=transaction.price,
            best_bid=self.order_book.get_best_bid(),
            best_ask=self.order_book.get_best_ask(),
            transaction_volume=transaction.quantity,
            bid_volume=self.order_book.get_total_bid_volume(),
            ask_volume=self.order_book.get_total_ask_volume()
        )

    def handle_order_stored(self, event: LimitOrderStoredEvent):
        order = event.order
        self.agent_manager.handle_order_stored(order)
        self.market_data.add_tick(
            time=event.timestamp,
            transaction_price=None,  # Brak transakcji
            best_bid=self.order_book.get_best_bid(),
            best_ask=self.order_book.get_best_ask(),
            transaction_volume=0,
            bid_volume=self.order_book.get_total_bid_volume(),
            ask_volume=self.order_book.get_total_ask_volume()
        )

    def handle_order_executed(self, event: OrderExecutedEvent):
        order = event.order
        executed_quantity = event.executed_quantity
        self.agent_manager.handle_order_executed(order.order_id, order.order_type, executed_quantity)

    def handle_order_cancelled(self, event: OrderCancelledEvent):
        order = event.order
        self.agent_manager.handle_order_cancelled(order.order_id)
        self.market_data.add_tick(
            time=event.timestamp,
            transaction_price=None,  # Brak transakcji
            best_bid=self.order_book.get_best_bid(),
            best_ask=self.order_book.get_best_ask(),
            transaction_volume=0,
            bid_volume=self.order_book.get_total_bid_volume(),
            ask_volume=self.order_book.get_total_ask_volume()
        )

    def step(self, current_time: int):
        self.agent_manager.step(current_time)

    def get_current_time(self) -> int:
        return 0
