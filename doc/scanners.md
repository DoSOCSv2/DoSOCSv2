## Scanners

Scanners are the modules that gather raw data (such as license information)
from software packages.  DoSOCS comes with three scanners defined:

* `dummy`
* `nomos` (the default)
* `nomos_deep`

During a package scan, after any unknown files are registered and their SHA-1
digests saved, any of these scanners can be run in any combination on the
target packages by using `dosocs2 scan` with the `-s` option. Example:

    $ dosocs2 scan -s nomos_deep,dummy package.tar.gz

Runs the `nomos_deep` scanner, then the `dummy` scanner (in that order) on the
file `package.tar.gz`.

Below is an explanation of each scanner's operation and configuration.

### General

All scanners operate at the package level, in that they accept a package as the
smallest object which they can analyze. (Remember that a 'package' can be a
directory or an archive file.)

Tracking of which scanners have already run on a package is performed by
DoSOCS itself, regardless of how each scanner is implemented. DoSOCS
will not run the same scanner multiple times on a package, unless the contents
of the package change, or if `--rescan` is specified on the command line.

A scanner may insert or update any number of rows in the database depending on
its function.

### Specific scanners

#### `dummy`

This scanner effectively does nothing. It creates rows in the database to mark
packages and files as processed, but does not actually collect or store any
information.

#### `nomos`

This tool is a part of FOSSology; it scans individual files for license
information. To enable it, the `path` variable in the `nomos` section of
`dosocs2.conf` must point to the `nomos` executable.

`nomos` reads every file in a package and tries to identify the license(s)
applicable to that file. It stores this information in the database at the
file level.

The `nomos` scanner also does file-level scan logging--if a particular file
in a package has already been scanned by `nomos`, `nomos` will ignore that
file, regardless of what package it's in. Again, one can specify the `--rescan`
command line option to disable this behavior.

#### `nomos_deep`

`nomos_deep` is the same as `nomos` in all respects, except it will unpack
any archives (tarballs, zip archives) found in the package, and scan those
files also. Any license information found in these 'sub-packages' is treated as
if it applies to that entire sub-package as if it were a regular file. Files in
sub-packages are not registered with DoSOCS.
