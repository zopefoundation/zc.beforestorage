.. image:: https://github.com/zopefoundation/zc.beforestorage/workflows/tests/badge.svg
        :target: https://github.com/zopefoundation/zc.beforestorage/actions?query=workflow%3Atests


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
connections, if the underlying database is still being changed by
other clients.

The "before" storage provides another way to leverage the loadBefore
method to support time travel and a means to provide an unchanging
view into a ZEO server.  A before storage is a database adapter that
provides a read-only view of an underlying storage as of a particular
point in time.
