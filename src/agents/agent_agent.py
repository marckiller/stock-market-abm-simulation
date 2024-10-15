from abc import ABC, abstractmethod
from enum import Enum, auto

class AbstractAgent(ABC):

    next_id = 1 #"agent 0" is simulaiton 

    def __init__(self):

        self.id = AbstractAgent.next_id
        AbstractAgent.next_id += 1
        
    @abstractmethod
    def act(self, time: int, market_data: object, portfolio: object):
        pass