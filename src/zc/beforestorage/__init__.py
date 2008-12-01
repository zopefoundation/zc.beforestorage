##############################################################################
#
# Copyright (c) Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import time

import ZODB.POSException
import ZODB.TimeStamp
import ZODB.utils
import ZODB.interfaces
import zope.interface

def time_stamp():
    t = time.time()
    g = time.gmtime(t)
    before = repr(ZODB.TimeStamp.TimeStamp(*(g[:5] + (g[5]+(t%1), ))))
    return before

startup_time_stamp = time_stamp()

class Before:

    def __init__(self, storage, before=None):
        if before is None:
            before = time_stamp()
        else:
            assert isinstance(before, basestring)
            if len(before) > 8:
                if 'T' in before:
                    d, t = before.split('T')
                else:
                    d, t = before, ''

                d = map(int, d.split('-'))
                if t:
                    t = t.split(':')
                    assert len(t) <= 3
                    d += map(int, t[:2]) + map(float, t[2:3])
                before = repr(ZODB.TimeStamp.TimeStamp(*d))
        self.storage = storage
        self.before = before
        if ZODB.interfaces.IBlobStorage.providedBy(storage):
            self.loadBlob = storage.loadBlob
            self.temporaryDirectory = storage.temporaryDirectory
            zope.interface.alsoProvides(self, ZODB.interfaces.IBlobStorage)
            

    def close(self):
        self.storage.close()

    def getName(self):
        return "%s before %s" % (self.storage.getName(),
                                 ZODB.TimeStamp.TimeStamp(self.before),
                                 )

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.getName())

    def getSize(self):
        return self.storage.getSize()

    def history(self, oid, version='', size=1):
        assert version == ''
        
        # This is awkward.  We don't know how much history to ask for.
        # We'll have to keep trying until we heve enough or until there isn't
        # any more to chose from. :(

        s = size
        while 1:
            base_history = self.storage.history(oid, version='', size=s)
            result = [d for d in base_history
                      if d['tid'] < self.before
                      ]
            if ((len(base_history) < s)
                or
                (len(result) >= size)
                ):
                if len(result) > size:
                    result = result[:size]
                return result
            s *= 2

    def isReadOnly(self):
        return True

    def lastTid(self, oid):
        return self.load(oid)[1]

    def lastTransaction(self):
        return ZODB.utils.p64(ZODB.utils.u64(self.before)-1)

    def __len__(self):
        return len(self.storage)

    def load(self, oid, version=''):
        assert version == ''
        result = self.storage.loadBefore(oid, self.before)
        if result:
            return result[:2]
        raise ZODB.POSException.POSKeyError(oid)

    def loadBefore(self, oid, tid):
        if self.before < tid:
            tid = self.before
        p, s1, s2 = self.storage.loadBefore(oid, tid)
        if (s2 is not None) and (s2 >= self.before):
            s2 = None
        return p, s1, s2

    def loadSerial(self, oid, serial):
        if serial >= self.before:
            raise ZODB.POSException.POSKeyError(oid)
        return self.storage.loadSerial(oid, serial)

    def new_oid(self):
        raise ZODB.POSException.ReadOnlyError()

    def pack(self, pack_time, referencesf):
        raise ZODB.POSException.ReadOnlyError()

    def registerDB(self, db):
        pass
    
    def sortKey(self):
        return self.storage.sortKey()

    def store(self, oid, serial, data, version, transaction):
        raise ZODB.POSException.StorageTransactionError(self, transaction)

    def storeBlob(self, oid, oldserial, data, blobfilename, version,
                  transaction):
        raise ZODB.POSException.StorageTransactionError(self, transaction)

    def tpc_abort(self, transaction):
        pass

    def tpc_begin(self, transaction):
        raise ZODB.POSException.ReadOnlyError()

    def tpc_finish(self, transaction, func = lambda: None):
        raise ZODB.POSException.StorageTransactionError(self, transaction)

    def tpc_transaction(self):
        return None

    def tpc_vote(self, transaction):
        raise ZODB.POSException.StorageTransactionError(self, transaction)

class ZConfig:

    def __init__(self, config):
        self.config = config
        self.name = config.getSectionName()

    def open(self):
        base = self.config.base.open()
        before = self.config.before
        if isinstance(before, basestring):
            if before.lower() == 'now':
                self.config.before = None
            elif before.lower() == 'startup':
                self.config.before = startup_time_stamp
        return Before(base, self.config.before)
    
