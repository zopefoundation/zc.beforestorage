CHANGES
=======

1.0 (2023-02-09)
----------------

- Add support for Python 3.9, 3.10, 3.11.

- Drop support for Python 2.7, 3.5, 3.6.


0.6 (2020-05-14)
----------------

- Add support for Python 3.5 through 3.8.

- Drop support for Python 3.3 and 3.4.

- Fix a long-standing bug in loadBefore´. The bug was revealed by
  testing against ZODB 5, for which loadBefore plays a bigger role.


0.5.1 (2013-10-25)
------------------

- Fix broken release


0.5.0 (2013-10-25)
------------------

Added ZODB4 and Python 3 support.


0.4.0 (2010-12-09)
------------------

Added a "before-from-file" option that can be used if the application wants to
preserve beforestorage state between application restarts.

0.3.2 (2008-12-05)
------------------

Updated to work with both ZODB 3.8 and 3.9.

0.3.1 (2008-12-01)
------------------

Renamed lastTid to getTid to conform to the ZEO.interfaces.IServeable
interface.


0.3.0 (2008-12-01)
------------------

Added Blob support.

0.2.0 (2008-03-05)
------------------

Added support for "now" and "startup" values to the before option when
using ZConfig.  The "now" value indicates that the before storage should
provide a view of the base storage as of the time the storage is created.
The "startup" value indicates that the before storage should provide a
view of the base stoage as of process startup time. The later is
especially useful when setting up more than once before storage in a
single application, as it allows you to arrange that all of the
storages provide consistent views without having to specify a time.

0.1.1 (2008-02-07)
------------------

Fixed a packaging bug that caused some files to be omitted.

0.1 (2008-01-??)
----------------

Initial release.
