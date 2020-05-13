Using ZConfig to configure Before storages
==========================================

"before" option
---------------

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
    <Before: my.fs before 2008-01-21 18:22:49.000000>

    >>> storage.close()

We can also give the option 'now' and get the current time.

    >>> import ZODB.config
    >>> storage = ZODB.config.storageFromString("""
    ...
    ... %import zc.beforestorage
    ...
    ... <before>
    ...     before now
    ...     <filestorage>
    ...         path my.fs
    ...     </filestorage>
    ... </before>
    ... """)

    >>> storage
    <Before: my.fs before 2008-01-21 18:22:53.000000>

    >>> storage.close()

We can give the option 'startup' and get the time at startup.

    >>> import ZODB.config
    >>> storage = ZODB.config.storageFromString("""
    ...
    ... %import zc.beforestorage
    ...
    ... <before>
    ...     before startup
    ...     <filestorage>
    ...         path my.fs
    ...     </filestorage>
    ... </before>
    ... """)

    >>> storage
    <Before: my.fs before 2008-01-21 18:22:43.000000>
    >>> import zc.beforestorage
    >>> import ZODB.TimeStamp
    >>> print(
    ...     str(zc.beforestorage.startup_time_stamp))
    2008-01-21 18:22:43.000000
    >>> storage.close()


"before-from-file" option
-------------------------

The "before-from-file" option can be used to preserve the changes file between
restarts. It's value is the absolute path to a file. If the file exists, the
"before" time will be read from that file. If the file does not exist,
it will be created and the current UTC time will be written to it

When used with a Changes file that does NOT have the "create=true"
option set, the database will be preserved between restarts.

    >>> import os.path
    >>> import tempfile

    >>> tempdir = tempfile.mkdtemp()
    >>> before_file = os.path.join(tempdir, 'before-file')

Currently the file does not exist. So it'll be created and written with the
current time. In order to make this repeatable, we "monkeypatch" the "get_now"
function in the module to return a fixed value:

    >>> import datetime
    >>> import zc.beforestorage

    >>> def fake_get_utcnow():
    ...     return datetime.datetime(2008, 1, 1, 15, 0)
    >>> orig_get_utcnow = zc.beforestorage.get_utcnow
    >>> zc.beforestorage.get_utcnow = fake_get_utcnow

    >>> os.path.exists(before_file)
    False

    >>> storage = ZODB.config.storageFromString("""
    ...
    ... %%import zc.beforestorage
    ...
    ... <before>
    ...     before-from-file %s
    ...     <filestorage>
    ...         path my.fs
    ...     </filestorage>
    ... </before>
    ... """ % before_file)

    >>> storage
    <Before: my.fs before 2008-01-01 15:00:00.000000>

    >>> storage.close()

The file will now have been created:

    >>> os.path.exists(before_file)
    True

    >>> f = open(before_file)
    >>> f.read() == fake_get_utcnow().replace(microsecond=0).isoformat()
    True

If we now write a new value to the file, the storage will be started with that
time.

    >>> f = open(before_file, 'w')
    >>> _ = f.write('1990-01-01T11:11')
    >>> f.close()

    >>> storage = ZODB.config.storageFromString("""
    ...
    ... %%import zc.beforestorage
    ...
    ... <before>
    ...     before-from-file %s
    ...     <filestorage>
    ...         path my.fs
    ...     </filestorage>
    ... </before>
    ... """ % before_file)

    >>> storage
    <Before: my.fs before 1990-01-01 11:11:00.000000>

    >>> storage.close()

If we restart the storage, the value from the file will be used.

    >>> storage = ZODB.config.storageFromString("""
    ...
    ... %%import zc.beforestorage
    ...
    ... <before>
    ...     before-from-file %s
    ...     <filestorage>
    ...         path my.fs
    ...     </filestorage>
    ... </before>
    ... """ % before_file)

    >>> storage
    <Before: my.fs before 1990-01-01 11:11:00.000000>

    >>> storage.close()

This will continue to happen until we remove the file. The "before_from_file"
path is stored on the storage itself, so applications that use it have access
to it.

    >>> os.remove(storage.before_from_file)

    >>> os.path.exists(before_file)
    False

If we restart the storage again, a new file will be created.

    >>> storage = ZODB.config.storageFromString("""
    ...
    ... %%import zc.beforestorage
    ...
    ... <before>
    ...     before-from-file %s
    ...     <filestorage>
    ...         path my.fs
    ...     </filestorage>
    ... </before>
    ... """ % before_file)

    >>> storage
    <Before: my.fs before 2008-01-01 15:00:00.000000>

    >>> storage.close()

Note that unlike the "before" option, the "before-from-file" file cannot
contain special values such as "now" or "startup".

    >>> f = open(before_file, 'w')
    >>> _ = f.write('now')
    >>> f.close()

    >>> storage = ZODB.config.storageFromString("""
    ...
    ... %%import zc.beforestorage
    ...
    ... <before>
    ...     before-from-file %s
    ...     <filestorage>
    ...         path my.fs
    ...     </filestorage>
    ... </before>
    ... """ % before_file)
    Traceback (most recent call last):
    ...
    ValueError: 8-byte array expected

Note that only one of "before" or "before-from-file" options can be specified,
not both:

    >>> storage = ZODB.config.storageFromString("""
    ...
    ... %%import zc.beforestorage
    ...
    ... <before>
    ...     before 2008-01-01
    ...     before-from-file %s
    ...     <filestorage>
    ...         path my.fs
    ...     </filestorage>
    ... </before>
    ... """ % before_file)
    Traceback (most recent call last):
      ...
    ValueError: Only one of "before" or "before-from-file" options can be specified, not both


Cleanup...

    >>> import shutil
    >>> shutil.rmtree(tempdir)

    >>> zc.beforestorage.get_utcnow = orig_get_utcnow


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
ReadConflictError:

    >>> conn5.get(root[5]._p_oid)
    Traceback (most recent call last):
    ...
    ZODB.POSException.ReadConflictError: b'\x00\x00\x00\x00\x00\x00\x00\x05'

Similarly, while we can access earlier object revisions, we can't
access revisions at the before time or later:

    >>> _ = b5.loadSerial(root._p_oid, transactions[2])

    >>> b5.loadSerial(root._p_oid, transactions[5])
    Traceback (most recent call last):
    ...
    POSKeyError: 0x00

Let's run through the storage methods:

    >>> (b5.getName() ==
    ...  'Data.fs before %s' % ZODB.TimeStamp.TimeStamp(transactions[5]))
    True

    >>> b5.getSize() == fs.getSize()
    True

    >>> for hd in b5.history(root._p_oid, size=3):
    ...     print(hd['description'].decode('utf-8'))
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

    >>> b5.getTid(root._p_oid) == transactions[4]
    True

    >>> b5.tpc_transaction()

    >>> try:
    ...     b5.new_oid()
    ... except Exception as e: # Workaround http://bugs.python.org/issue19138
    ...     print(e.__class__.__name__)
    ReadOnlyError

    >>> from ZODB.TimeStamp import TimeStamp
    >>> try:
    ...     b5.pack(TimeStamp(transactions[3]).timeTime(), lambda p: [])
    ... except Exception as e:
    ...     print(e.__class__.__name__)
    ReadOnlyError

    >>> b5.registerDB(db5)

    >>> b5.sortKey() == fs.sortKey()
    True

    >>> try:
    ...     b5.tpc_begin(transaction.get())
    ... except Exception as e:
    ...     print(e.__class__.__name__)
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
    ZODB.POSException.StorageTransactionError: ...

    >>> b5.tpc_finish(transaction)
    ... # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ZODB.POSException.StorageTransactionError: ...

    >>> b5.tpc_transaction()
    >>> b5.tpc_abort(transaction)

Before storages don't support undo:

    >>> b5.supportsUndo
    Traceback (most recent call last):
    ...
    AttributeError: 'Before' object has no attribute 'supportsUndo'

(Don't even ask about versions. :)

Closing a before storage closes the underlying storage:

    >>> b5.close()
    >>> fs.load(root._p_oid, '') # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: ...

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

    >>> dbnow.close()

The timestamp may be passed directory, or as an ISO time.  For
example:

    >>> fs = ZODB.FileStorage.FileStorage('Data.fs')
    >>> iso = 'T'.join(str(ZODB.TimeStamp.TimeStamp(transactions[5])).split()
    ...                )[:19]
    >>> b5 = zc.beforestorage.Before(fs, iso)
    >>> db5 = DB(b5)
    >>> conn5 = db5.open()
    >>> root5 = conn5.root()
    >>> len(root5)
    4

    >>> b5.close()

Blob Support
------------

Before storage supports blobs if the storage it wraps supports blobs,
and, in fact, it simply exposes the underlying storages loadBlob and
temporaryDirectory methods.

    >>> fs = ZODB.FileStorage.FileStorage('Data.fs')
    >>> import ZODB.blob
    >>> bs = ZODB.blob.BlobStorage('blobs', fs)
    >>> db = ZODB.DB(bs)
    >>> conn = db.open()
    >>> conn.root()['blob'] = ZODB.blob.Blob()
    >>> _ = conn.root()['blob'].open('w').write(b'data1')
    >>> transaction.commit()

    >>> bnow = zc.beforestorage.Before(bs)
    >>> dbnow = DB(bnow)
    >>> connnow = dbnow.open()
    >>> rootnow = connnow.root()

    >>> _ = conn.root()['blob'].open('w').write(b'data2')
    >>> transaction.commit()

    >>> print(rootnow['blob'].open().read().decode('utf-8'))
    data1

    >>> bnow.temporaryDirectory() == bs.temporaryDirectory()
    True

    >>> import ZODB.interfaces, zope.interface.verify
    >>> zope.interface.verify.verifyObject(
    ...     ZODB.interfaces.IBlobStorage, bnow)
    True

    >>> bnow.close()
