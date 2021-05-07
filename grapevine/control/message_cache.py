import logging
import random
from multiprocessing import Manager
from datetime import datetime


class GrapeVineMessageCache:

    """
    Thread-safe implementation of a message cache
    which maintains all currently known messages
    """

    DATE_ADDED = 'DateAdded'

    def __init__(self, _label, cache_size=30):
        """
        """

        self._message_cache = Manager().dict()
        self._label = _label
        self.cache_size = cache_size
    
    def add_message(self, message, valid=False):
        """
        """

        for message_id in self._message_cache.keys():
            if message == self._message_cache[message_id]['message']:
                return None
        
        message_id = message['message_id']
        self._message_cache[message_id] = {
            'message': message, 'valid': valid,
            GrapeVineMessageCache.DATE_ADDED: datetime.now()
        }
        self.__maintain_cache()
        logging.debug(f"{self._label} | Added new message, current message cache: {self._message_cache.keys()}")
    
    def get_message(self, message_id):
        """
        """
        if message_id in self._message_cache:
            return self._message_cache[message_id]['message']
        else:
            return False
    
    def set_validity(self, message_id, valid):
        if message_id in self._message_cache:
            old_cache_item = self._message_cache[message_id]
            old_cache_item['valid'] = valid
            self._message_cache[message_id] = old_cache_item
    
    def remove_messages(self, message_id):
        """
        """
        return self._message_cache.pop(message_id, None)
    
    def __maintain_cache(self):
        """
        """
        if len(self._message_cache) > self.cache_size:
            sorted_messages = sorted(self._message_cache.items(),
            key = lambda x: self._message_cache[x[0]][GrapeVineMessageCache.DATE_ADDED])
            message_to_remove = sorted_messages[0][0]
            self.remove_messages(message_to_remove)
    
    def iterator(self, exclude_id=True):
        """
        """

        sorted_messages = sorted(self._message_cache.items(), key=lambda x: self._message_cache[x[0]][GrapeVineMessageCache.DATE_ADDED])
        return (message[1] if exclude_id else message for message in sorted_messages)
    

if __name__ == '__main__':
    print("running message cache outside of grapevine main")