## Scanners

The concept of scanners that provide useful information about software packages
is an important one to `dosocs2`. `dosocs2` comes with four scanners defined:

* `dummy`
* `nomos` (the default)
* `nomos_deep`
* `dependency_check`

During a package scan, after any unknown files are registered and their SHA-1
digests saved, any of these scanners can be run in any combination on the
target packages. This is accomplished using the `-s` option to `dosocs2 scan`,
which takes a comma-separated list of scanner names. The scanners are run
in the order specified on the command line.

Below is an explanation of each scanner's operation and configuration.

### General

All scanners operate at the package level, in that they accept a package as the
smallest object which they can analyze. (Remember that a 'package' can be a
directory or an archive file.)

Tracking of which scanners have already run on a package is performed by
`dosocs2` itself, regardless of how each scanner is implemented. `dosocs2`
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
sub-packages are not registered with `dosocs2`.

#### `dependency_check`

This scanner uses OWASP Dependency-Check to attempt to identify any
[CPE(s)](https://nvd.nist.gov/cpe.cfm) associated with a package. It operates
at the package level only, and any file-level operations are considered
implementation details of Dependency-Check itself.

As of version 0.10.0, this information is stored as a JSON object in the
package comment field (SPDX 2.0 section 3.19). Until a field for this
information is added to SPDX, or an alternative solution arises, the
package comment field **will be overwritten** each time `dependency_check`
runs on a package.

#### `copyright`

This is the `copyright` agent from FOSSology, it identifies strings that look
like copyright declarations. `copyright` stores found copyright strings in
the copyright text field at the file level, overwriting that field if it is
already populated. This agent is a bit heavy-handed--it often produces
false positives, so is output should be subject to extra review by a human.

#### `monk`

Another adapter for a FOSSology agent. `monk` is a license scanner; it is
fast but tends to produce much fewer matches than `nomos`. It otherwise
operates exactly the same as `nomos`, as far as we are concerned. 
