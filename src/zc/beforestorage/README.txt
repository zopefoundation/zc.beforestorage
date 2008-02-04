==============
Before Storage
==============

ZODB storages typically store multiple object revisions to support
features such as multi-version concurrency control and undo.  In the
case of the mod popular storage implementation, old revisions aren't
discarded until a pack.  This feature has often been exploited to
perform time travel, allowing one to look at a database as it existed
in at some point in time.  In the past, this has been possible with
file storage by specifying a time at which to open the file
storage. This works fairly well, but is very slow for large databases
because existing index files can't easily be used.  Time travel is
also supported for individual objects through the ZODB history
mechanism.

The introduction of multi-version concurrency control provided new
opertunities for time travel.  Using the storage loadBefore method,
one can load transaction records written before a given time.  ZODB
3.9 will provide an option to the database open method for opening
connections as of a point in time.

Demo storage can be quite useful for testing, and especially staging
applications. In a common configuration, they allow for storing
changes to a base database without changing the underlying database.
Zope functional testing frameworks leverage demo storages to easily
roll-back database state after a test to a non-empty state before a
test.  A significant limitation of demo storages is that they can't be
used with base storages that change.  This means that they generaly
can't be used with ZEO.  It isn't enough to have a read-only
connecttions, if the underlying database is still being changed by
other clients.

The "before" storage provides another way to leverage the loadBefore
method to support time travel and a means to provide an unchanging
view into a ZEO server.  A before storage is a database adapter that
provides a read-only view of an underlying storage as of a particular
point in time.

Change history
==============

0.1 (2008-01-??)
----------------

Initial release.

Using ZConfig to configure Before storages
==========================================

To use before storages from ZConfig configuration files, you need to
import zc.beforestorage and then use a before storage section.

    >>> import ZODB.config
    >>> storage = ZODB.config.storageFromString("""
    ...
    ... %import zc.beforestorage
    ...
    ... <before>
    ...     before 2008-01-21
    ...     <filestorage>
    ...         path my.fs
    ...     </filestorage>
    ... </before>
    ... """)

    >>> storage
    <Before: my.fs before 2008-01-21 00:00:00.000000>

    >>> storage.close()

If we leave off the before option, we'll use the current time:

    >>> storage = ZODB.config.storageFromString("""
    ...
    ... %import zc.beforestorage
    ...
    ... <before>
    ...     <filestorage>
    ...         path my.fs
    ...     </filestorage>
    ... </before>
    ... """)

    >>> storage
    <Before: my.fs before 2008-01-21 18:22:48.000000>

    >>> storage.close()

Demonstration (doctest)
=======================

Note that most people will configure the storage through ZConfig.  If
you are one of those people, you may want to stop here. :)  The
examples below show you how to use the storage from Python, but they
also exercise lots of details you might not be interested in.

To see how this works at the Python level, we'll create a file
storage, and use a before storage to provide views on it.

    >>> import ZODB.FileStorage
    >>> fs = ZODB.FileStorage.FileStorage('Data.fs')
    >>> from ZODB.DB import DB
    >>> db = DB(fs)
    >>> conn = db.open()
    >>> root = conn.root()
    >>> import persistent.mapping
    
We'll record transaction identifiers, which we'll use to when opening
the before storage.

    >>> import transaction
    >>> transactions = [root._p_serial]
    >>> for i in range(1, 11):
    ...     root[i] = persistent.mapping.PersistentMapping()
    ...     transaction.get().note("trans %s" % i)
    ...     transaction.commit()
    ...     transactions.append(root._p_serial)

We create a before storage by calling the Before constructer
with an existing storage and a timestamp:

    >>> import zc.beforestorage
    >>> b5 = zc.beforestorage.Before(fs, transactions[5])
    >>> db5 = DB(b5)
    >>> conn5 = db5.open()
    >>> root5 = conn5.root()
    >>> len(root5)
    4

here we see the database as it was before the 5th transaction was
committed.  If we try to access a later object, we'll get a
POSKeyError:

    >>> conn5.get(root[5]._p_oid)
    Traceback (most recent call last):
    ...
    POSKeyError: 0x05

Similarly, while we can access earlier object revisions, we can't
access revisions at the before time or later:

    >>> _ = b5.loadSerial(root._p_oid, transactions[2])

    >>> b5.loadSerial(root._p_oid, transactions[5])
    Traceback (most recent call last):
    ...
    POSKeyError: 0x00
    
    >>> conn5.get(root[5]._p_oid)
    Traceback (most recent call last):
    ...
    POSKeyError: 0x05

Let's run through the storage methods:

    >>> b5.getName()
    'Data.fs before 2008-01-21 18:22:56.000000'

    >>> b5.getSize() == fs.getSize()
    True

    >>> for hd in b5.history(root._p_oid, size=3):
    ...     print hd['description']
    trans 4
    trans 3
    trans 2

    >>> b5.isReadOnly()
    True

    >>> transactions[4] <= b5.lastTransaction() < transactions[5]
    True

    >>> len(b5) == len(fs)
    True

    >>> p, s1, s2 = b5.loadBefore(root._p_oid, transactions[5])
    >>> p == fs.loadSerial(root._p_oid, transactions[4])
    True
    >>> s1 == transactions[4]
    True
    >>> s2 is None
    True

    >>> p, s1, s2 = b5.loadBefore(root._p_oid, transactions[4])
    >>> p == fs.loadSerial(root._p_oid, transactions[3])
    True
    >>> s1 == transactions[3]
    True
    >>> s2 == transactions[4]
    True

    >>> b5.lastTid(root._p_oid) == transactions[4]
    True

    >>> b5.new_oid()
    Traceback (most recent call last):
    ...
    ReadOnlyError

    >>> from ZODB.TimeStamp import TimeStamp
    >>> b5.pack(TimeStamp(transactions[3]).timeTime(), lambda p: [])
    Traceback (most recent call last):
    ...
    ReadOnlyError
    
    >>> b5.registerDB(db5)

    >>> b5.sortKey() == fs.sortKey()
    True

    >>> b5.tpc_begin(transaction.get())
    Traceback (most recent call last):
    ...
    ReadOnlyError

    >>> b5.store(root._p_oid, transactions[4], b5.load(root._p_oid)[0], '',
    ...          transaction.get())
    ... # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    StorageTransactionError: ...

    >>> b5.tpc_vote(transaction.get())
    ... # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    StorageTransactionError: ...

    >>> b5.tpc_finish(transaction)
    ... # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    StorageTransactionError: ...

    >>> b5.tpc_transaction()
    >>> b5.tpc_abort(transaction)

Before storages don't support undo:

    >>> b5.supportsUndo
    Traceback (most recent call last):
    ...
    AttributeError: Before instance has no attribute 'supportsUndo'

(Don't even ask about versions. :)

Closing a before storage closes the underlying storage:

    >>> b5.close()
    >>> fs.load(root._p_oid, '')
    Traceback (most recent call last):
    ...
    ValueError: I/O operation on closed file

If we ommit a timestamp when creating a before storage, the current
time will be used:

    >>> fs = ZODB.FileStorage.FileStorage('Data.fs')
    >>> from ZODB.DB import DB
    >>> db = DB(fs)
    >>> conn = db.open()
    >>> root = conn.root()

    >>> bnow = zc.beforestorage.Before(fs)
    >>> dbnow = DB(bnow)
    >>> connnow = dbnow.open()
    >>> rootnow = connnow.root()
    
    >>> for i in range(1, 11):
    ...     root[i] = persistent.mapping.PersistentMapping()
    ...     transaction.get().note("trans %s" % i)
    ...     transaction.commit()
    ...     transactions.append(root._p_serial)
    
    >>> len(rootnow)
    10

The timestamp may be passed directory, or as an ISO time.  For
example:

    >>> b5 = zc.beforestorage.Before(fs, '2008-01-21T18:22:56')
    >>> db5 = DB(b5)
    >>> conn5 = db5.open()
    >>> root5 = conn5.root()
    >>> len(root5)
    4
