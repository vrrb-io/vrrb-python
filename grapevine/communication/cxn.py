import uuid
import time
import logging
import random
from socket import SHUT_RDWR
from multiprocessing import Manager, Lock
from config.network_config import TESTNET_PORT
from util.crypto_hash import crypto_hash

class CxnPool:
    CXN = 'cxn'
    SERVER_ID = 'server_id'

    def __init__(self, cxn_pool_id=None, cache_size=30, _cxns=Manager().dict(), _pool_lock=Lock()):
        """
        Constructor for the GrapeVine CxnPool

        param cxn_pool_id: An id to derive the concrete functionality of this cxn pool
        param cache_size: (optional): the max number of cxns in the csn pool.
        """

        self.cxn_pool_id = cxn_pool_id or crypto_hash(str(uuid.uuid4()), time.time_ns())
        self._cxns = _cxns
        self._cache_size = cache_size
        self._pool_lock = _pool_lock

    
    def add_cxn(self, _id, cxn, server_id=None):
        """
        Adds a new identifier and it's cxn.
        Also, if available, adds the cxn server_id
        to share with other peers so that the new
        peer can be discovered.

        param _id: A unique id for the cxn.
        param cxn: a cxn object
        param server_id: (optional) the server id of the peer
        """

        if not server_id:
            server_ip = _id
            server_id = f'{server_ip}:{TESTNET_PORT}'
        self._pool_lock.acquire()
        if _id not in self._cxns:
            self._cxns[_id] = {
                CxnPool.CXN: cxn,
                CxnPool.SERVER_ID: server_id
            }

            logging.debug(f"{self.cxn_pool_id} | Added new cxn {_id} (pool: {self}")
            self._pool_lock.release()
            # self._maintain_cxn()
        else:
            self._pool_lock.release()
            logging.debug(f"{self.cxn_pool_id} | Updating information about cxn {_id} failed because it no longer exists")


    def del_cxn(self, _id):
        """
        Removes an existing cxn from the cxn_pool.

        param _id: Unique id to find the affected cxn
        """

        self._pool_lock.acquire()
        cxn = self._cxns.get(_id, None)
        if cxn:
            self._pool_lock.release()
            return cxn[CxnPool.CXN]
        else:
            self._pool_lock.release()
            raise Exception(f'Cannot find id {_id}')
    
    def get_server_id(self, _id):
        """
        Gets the server id for one cxn.

        param _id: unique id to find the affected cxn
        """

        self._pool_lock.acquire()
        cxn = self._cxns.get(_id, None)
        if cxn:
            self._pool_lock.release()
            return cxn[CxnPool.SERVER_ID]
        else:
            self._pool_lock.release()
            raise Exception(f"Cannot find id {_id}")
    
    def get_ids(self) -> list:
        """
        Get a list of all ids

        returns: list of all id_strings
        """

        self._pool_lock.acquire()
        _ids = self._cxns.keys()
        self._pool_lock.release()
        return _ids

    def get_server_ids(self, _ids_to_exclude=None) -> list:
        """
        Collects server ids
        returns: list of all server ids
        """
        if not _ids_to_exclude:
            _ids_to_exclude = []
        
        server_ids = []
        self._pool_lock.acquire()
        for _, cxn in self._cxns.items():
            server_address = cxn[CxnPool.SERVER_ID]
            if server_address:
                if server_address not in _ids_to_exclude:
                    server_ids.append(server_address)
        self._pool_lock.release()
        return server_ids
    
    def __str__(self):
        """
        String representation of CxnPool
        """
        return self.__str__
    
    def __repr__(self):
        """
        representation of CxnPool
        """
        return self.__repr__
    
    def to_json(self):
        """
        json serialized representation of cxn pool
        """
        return self.__dict__
    
    def _maintain_cxns(self):
        """
        Maintain the list of cxns. If number of current cxns
        exceeds the max cache size, a random cxn is killed.

        """

        if len(self._cxns) > self._cache_size:
            self._pool_lock.acquire()
            cxn_to_remove = list(self._cxns.keys())[random.randint(0, len(self._cxns)) - 1]
            self._pool_lock.release()
            killed_cxn = self.remove_cxn(cxn_to_remove)
            killed_cxn.shutdown(SHUT_RDWR)
            killed_cxn.close()
        
    def get_capacity(self):
        """
        Provides the left capacity of the current cxn pool.

        returns: Remaining capacity
        """

        return self._cache_size - len(self._cxns)
    
    def filter_new_server_ids(self, server_ids, id_to_exclude=None):
        """
        Provides all given ids which are not known until now

        param server_ids: Server ids to check against known ones.
        param ids_to_exclude: (optional) Server ids to exclude.
        returns: ids which are not known as server ids in the cxn pool until now.
        """
        known_server_ids = self.get_server_ids(id_to_exclude=id_to_exclude)
        new_ids = []
        for server_id in server_ids:
            if server_id not in known_server_ids:
                new_ids.append(server_id)
        
        return new_ids
    
    def get_random_id(self, id_to_exclude):
        """
        provides a random id which represents an active cxn in the pool at the moment

        param id_to_exclude: an id to exclude
        returns: Random id
        """

        self._pool_lock.acquire()
        ids = [_id for _id in self._cxns.keys() if id != id_to_exclude]
        self._pool_lock.release()
        if len(ids) > 1:
            return ids[random.randint(0, len(ids) - 1)]
        elif len(ids) == 1:
            return ids[0]
        else:
            return None
    
