"""

"""
from .database.models import Transfer


class EventAnalyzer:
    def __init__(self, event_name):
        self.event_name = event_name

    def get_events(self, events_list):
        events = list(filter((lambda event: event is not None), map(self._analyze, events_list)))
        return events

    def _analyze(self, event_dict):
        return None


class TransferEventAnalyzer(EventAnalyzer):
    def __init__(self):
        EventAnalyzer.__init__(self, 'Transfer')

    def _analyze(self, event_dict):
        if event_dict['event'] == self.event_name:
            return Transfer(
                block_time=event_dict['blockNumber'],
                amount=event_dict['args']['_value'],
                to_address=event_dict['args']['_to'],
                from_address=event_dict['args']['_from'],
            )
        else:
            return None
