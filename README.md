DoSOCS
======

System Overview
---------------
<div>
  <p>
  The Software Package Data Exchange (SPDX) specification is a formatting standard for communicating the licenses and copyrights associated with a software package. Being able to explicate this information is a required function for operations support system management within an organization.
  </p>
  
  <p>
  DoSOCS is aimed at processing software packages into SPDX documents. This utility will scan, store, and print spdx documents. DoSOCS Stores SPDX docs in a MySQL database, the same that is documented <a href="https://github.com/socs-dev-env/SOCSDatabase">here</a>.
  </p>
</div>

Current Version
---------------
<a href="https://github.com/socs-dev-env/DoSOCS/blob/master/ChangeLog.md">Version 1.0</a>

License
-------
<ul>
  <li>Source Code: <a href="https://github.com/socs-dev-env/DoSOCS/blob/master/src/ApacheLicense.txt">Apache 2.0</a></li>
  <li>Documentation: <a href="https://github.com/socs-dev-env/DoSOCS/blob/master/CCLicense.txt">Creative Commmons BY-SA-3.0</a></li>
</ul>

Copyright
---------
Copyright © 2014 University of Nebraska at Omaha

System Requirements
-------------------
In general, your system should meet <a href="http://www.fossology.org/projects/fossology/wiki/SysConfig">FOSSology's performance recommendations</a>, which depend on the maximum file or package size you intend to scan.

Prerequisites
-----------------
- Python 2.7
- MySQL
- A php environment
- <a href="http://www.fossology.org/">FOSSology</a>
- <a href="http://ninka.turingmachine.org/#sec-3">Ninka</a>

Installation
------------
- Install Prerequisites
- Download and run <a href="https://github.com/socs-dev-env/DoSOCS/blob/master/install.sh">install.sh</a> to the directory you want DoSOCS installed (Note: you may need to change the user name and password fields in install.sh)
- Update settings.py with database connection information, and install locations of ninka and fossology.

This will install <a href="https://github.com/socs-dev-env/DoSOCS">DoSOCS</a>, <a href="https://github.com/socs-dev-env/SOCSDashboard">SOCSDashboard</a>, and <a href="https://github.com/socs-dev-env/SOCSDatabase">SOCSDatabase</a>. Also ensure you have execute rights on ninka and fossology.

Usage
-----
`./DoSPDX.py [options]`

#####Options

- `--packagePath [Path to archive]` Allows user to specify which package to run DoSPDX against.
  - Conditonaly optional, Required if used with `-s` or `--scan`
  - ***Example:*** `./DoSPDX.py -p archive.tar.bz2`
- `-s` or `--scan` Runs a scan on the package specified in package path argument.
  - Conditonaly optional, Required if used with `-s` or `--scan`
  - ***Example:*** `./DoSPDX.py -p archive.tar.bz2 -s`
- `--print [format]` Prints out SPDX document in specified format.
  - Optional
  - ***Example:*** `./DoSPDX.py --print TAG` or `./DoSPDX.py --print RDF`
- `--documentComment [Document Comment]` Specifies SPDX document Comment section.
  - Optional 
  - ***Example:*** `./DoSPDX.py --documentComment "Scanned as part of the Yocto build process."`
- `--spdxDocId [SPDX Doc Id]` Used to generate the spdx document object from the MySql Database.
  - Conditonaly optional, Required if `-s` or `--scan` is not used.
  - ***Example:*** `./DoSPDX.py --spdxDocId 37` 
- `--creator [Creator]` Specifies who is creating the SPDX document.
  - Optional
  - ***Example:*** `./DoSPDX.py --creator "Zachary McFarland"` 
- `--creatorComment [Creator Comment]` Specifies creator comment for the SPDX document.
  - Optional
  - ***Example:*** `./DoSPDX.py --creatorComment "Inital scan of pacakge."`
- `--packageVersion [Package Version]` Specifies version of the package being scanned.
  - Optional
  - ***Example:*** `./DoSPDX.py --packageVersion 1.2`
- `--packageSupplier [Package Supplier]` Specifies creator comment for the SPDX document.
  - Optional
  - ***Example:*** `./DoSPDX.py --packageSupplier "Apache Software Foundation"`
- `--packageDownloadLocation [Download Location]` URL of where the pacakge was downloaded from.
  - Optional 
  - ***Example:*** `./DoSPDX.py --packageDownloadLocation "http://www.apache.org/"`
- `--pacakgeOriginator [Originator]` Specifies the originating source of pacakge.
  - Optional
  - ***Example:*** `./DoSPDX.py --pacakgeOriginator "IBM"` 
- `--packageHomePage [HomePage]` Specifies URL for software pacakge homepage.
  - Optional
  - ***Example:*** `./DoSPDX.py --packageHomePage "http://www.apache.org/"`
- `--pacakgeSourceInfo [Package Source Info]` Specifies source information of the pacakge.
  - Optional
  - ***Example:*** `./DoSPDX.py --pacakgeSourceInfo "Package that is part of Yocto Build process."`
- `--packageLicenseComments [Comments]` Allows for comments to be made about the license of a pacakge.
  - Optional
  - ***Example:*** `./DoSPDX.py --packageLicenseComments "Apache"`
- `--packageDescription [Description]` Allows user to enter a description of the package.
  - Optional
  - ***Example:*** `./DoSPDX.py --packageDescription "This package allows for hosting local content to the web."`
 


Code Contributions
------------------
All contributions to DoSOCS will be subject to review by the owner of the repo before being merged.
