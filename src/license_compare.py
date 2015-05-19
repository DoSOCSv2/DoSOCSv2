#!/usr/bin/python

"""
Canonicalizes the licenses found in FOSSology and Ninka, which use different
terminology (for example, GPLv2 is "GPL_v2" in FOSSology and "GPLv2" in Ninka).
Also contains the SPDX 1.19 terminology when applicable.

Terminology sources:
- FOSSology: The old FOSSology dictionary
  U{http://www.fossology.org/attachments/3375/license_list_old.txt}
- Ninka: In Ninka 1.1, the file rules.dict
  U{https://github.com/dmgerman/ninka/blob/master/matcher/rules.dict}
  (Warning: It is somewhat difficult to read.)
- SPDX 1.19: U{http://spdx.org/licenses/}.

Tuple format: (FOSSology_output, Ninka_output, SPDX_name)
Example: ("GPL_v2", "GPLv2", "GPL-2.0")
If any licenses are not covered by a scanner or SPDX, the "blank spot"(s) will
be set to False.

For those wishing to expand upon this dictionary, one important note: The SPDX
term MUST be the last part of the tuple (the program is made to read it as
such). If you intend to add an additional dictionary, put it between Ninka and
SPDX.

@author Doug Richardson
@author Jon von Kampen
@author James Thompson

@license Apache License 2.0

@todo Because of time constraints, this is not a comprehensive comparison
dictionary between FOSSology and Ninka.
"""

Non_Licenses = [
    ("ERROR", "ERROR", False), ("None", "NONE", False),
    ("UnclassifiedLicense", "UNKNOWN", False)
    ]
"""Kept separate for now for sorting purposes"""

License_Approximations = [
    ("BSD-style", "BSD3", False), ("BSD-style", "spdxBSD3", False),
    ("BSD-style", "spdxBSD4", False), ("BSD", "BSD3", False),
    ("BSD", "spdxBSD4", False), ("MIT-style", "MITX11", False),
    (False, "SameAsPerl", False),
    ("Public-domain-claim", "publicDomain", False),
    (False, "DoWhatTheFuckYouWantv2", "WTFPL"),
    ("LGPL_v2.1+", "LesserGPLv2.1+", "LGPL-2.1+"),
    ]
"""
Fossology and Ninka are vague on some license output.
Because these are not explicit matches, we cannot confirm
their meaning.  However I put "approximations" and other
recorded instances here for future development.
"""

Licenses = [
    ("None", "NONE", "NONE"),  # This is confirmation of no license
    ("None", "NO_LICENSE_FOUND", "NONE"),
    ("GPL_v2", "GPLv2", "GPL-2.0"),
    ("GPL_v2+", "GPLv2+", "GPL-2.0+"),
    (False, "LesserGPLv2.1+", "LGPL-2.1+"),
    #Not sure if fossology LGPL is "Lesser" or "Library"
    ("RSA-Security", False, False),
    (False, "BeerWareVer42", False),
    ("GPL", "GPLnoVersion", False),
    ("Free-SW", False, False),
    ("Affero_v3+", "AGPLv3+", False),
    ("GPL_v3", "GPLv3", "GPL-3.0"),
    ("GPL_v3+", "GPLv3+", "GPL-3.0+"),
    ("GPLV3+", "GPL-3.0+", "GPL-3.0+"),
    (False, False, "BSD-2-Clause"),
    (False, False, "BSD-2-Clause-FreeBSD"),
    (False, False, "BSD-2-Clause-NetBSD"),
    (False, False, "BSD-3-Clause"),
    (False, False, "BSD-3-Clause-Clear"),
    (False, False, "BSD-4-Clause"),
    (False, False, "BSD-4-Clause-UC"),
    #Fossology only has BSD, BSD-Style, and BSD(non-commercial)
    #Ninka has many BSD variants, but I don't know which maps to what
    ("AFL_v1.1", False, "AFL-1.1"),
    ("AFL_v1.2", False, "AFL-1.2"),
    ("AFL_v2.0", False, "AFL-2.0"),
    ("AFL_v2.1", False, "AFL-2.1"),
    ("AFL_v3.0", False, "AFL-3.0"),
    ("AFL_v3.0", False, "AFL-3.0"),
    (False, False, "Aladdin"),
    (False, False, "ANTLR-PD"),
    ("Apache_v1.0", "Apachev1.0", "Apache-1.0"),
    ("Apache_v1.1", "Apachev1.1", "Apache-1.1"),
    ("Apache_v2.0", "APACHEV2", "Apache-2.0"),
    ("APSL_v1.0", False, "APSL-1.0"),
    ("APSL_v1.1", False, "APSL-1.1"),
    ("APSL_v1.2", False, "APSL-1.2"),
    ("APSL_v2.0", False, "APSL-2.0"),
    ("Artistic", "ArtisticLicensev1", "Artistic-1.0"),
    ("Artistic_v2.0", False, "Artistic-2.0"),
    ("Attribution-Assurance", False, "AAL"),
    ("BitTorrent_v1.0", False, "BitTorrent-1.0"),
    ("BitTorrent_v1.1", False, "BitTorrent-1.1"),
    ("Boost_v1.0", "boostV1", "BSL-1.0"),
    ("CeCILL_v1", False, "CECILL-1.0"),
    ("CeCILL_v1.1", False, "CECILL-1.1"),
    ("CeCILL_v2.0", False, "CECILL-2.0"),
    ("CeCILL-B", False, "CECILL-B"),
    ("CeCILL-C", False, "CECILL-C"),
    (False, False, "ClArtistic"),
    (False, False, "CNRI-Python"),
    (False, False, "CNRI-Python-GPL-Compatible"),
    (False, False, "CPOL-1.02"),
    ("CDDL_v1.0", "CDDLicV1", "CDDL-1.0"),
    (False, False, "CDDL-1.1"),
    ("CPAL_v1.0", False, "CPAL-1.0"),
    ("CPL_v1.0", "CPLv1", "CPL-1.0"),
    (False, False, "CATSOL-1.1"),
    (False, False, "Condor-1.1"),  # Fossology has condor, but no version
    ("CCA_v1.0", False, "CC-BY-1.0"),
    (False, False, "CC-BY-2.0"),
    ("CCA_v2.5", False, "CC-BY-2.5"),
    ("CCA_v3.0", False, "CC-BY-3.0"),
    (False, False, "CC-BY-ND-1.0"),
    (False, False, "CC-BY-ND-2.0"),
    (False, False, "CC-BY-ND-2.5"),
    (False, False, "CC-BY-ND-3.0"),
    (False, False, "CC-BY-NC-1.0"),
    (False, False, "CC-BY-NC-2.0"),
    (False, False, "CC-BY-NC-2.5"),
    (False, False, "CC-BY-NC-3.0"),
    (False, False, "CC-BY-NC-ND-1.0"),
    (False, False, "CC-BY-NC-ND-2.0"),
    (False, False, "CC-BY-NC-ND-2.5"),
    (False, False, "CC-BY-NC-ND-3.0"),
    (False, False, "CC-BY-NC-SA-1.0"),
    (False, False, "CC-BY-NC-SA-2.0"),
    (False, False, "CC-BY-NC-SA-2.5"),
    (False, False, "CC-BY-NC-SA-3.0"),
    ("CCA-SA_v1.0", False, "CC-BY-SA-1.0"),
    (False, False, "CC-BY-SA-2.0"),
    ("CCA-SA_v2.5", False, "CC-BY-SA-2.5"),
    ("CCA-SA_v3.0", False, "CC-BY-SA-3.0"),
    (False, False, "CC0-1.0"),
    ("CUA_v1.0", False, "CUA-OPL-1.0"),
    (False, False, "D-FSL-1.0"),
    (False, False, "WTFPL"),  # Ninka has a "v2" verison of this
    ("Eclipse_v1.0", False, "EPL-1.0"),
    #Ninka has an EPLv1, but I don't know if it's Eclipse or Erlang
    (False, False, "eCos-2.0"),
    (False, False, "ECL-1.0"),  # Fossolgoy has ECL, but no version
    (False, False, "ECL-2.0"),
    ("Eiffel_v1", False, "EFL-1.0"),
    ("Entessa", False, "Entessa"),
    (False, False, "ErlPL-1.1"),
    (False, False, "EUPL-1.0"),
    (False, False, "EUPL-1.1"),
    ("Fair", False, "Fair"),
    ("Frameworx_v1.0", False, "Frameworx-1.0"),
    ("Affero_v1", False, "AGPL-1.0"),
    ("Affero_v3", False, "AGPL-3.0"),  # Ninka can only detect AGPLv3+
    ("Freetype", "FreeType", "FTL"),
    ("GFDL_v1.1", False, "GFDL-1.1"),
    ("GFDL_v1.2", False, "GFDL-1.2"),
    (False, False, "GFDL-1.3"),
    (False, False, "GPL-2.0-with-autoconf-exception"),
    (False, False, "GPL-2.0-with-bison-exception"),
    #ninka has "BisonException", but doesn't specify the license
    #Fossology has GPL-Bison Exception, but no version is specified
    (False, "ClassPathExceptionGPLv2", "GPL-2.0-with-classpath-exception"),
    #Fossology has GPL-classpath-exception, but no version is specified
    (False, False, "GPL-2.0-with-font-exception"),
    (False, False, "GPL-2.0-with-GCC-exception"),
    (False, False, "GPL-3.0-with-autoconf-exception"),
    (False, False, "GPL-3.0-with-GCC-exception"),
    (False, "LesserGPLv2.1", "LGPL-2.1"),
    (False, "LesserGPLv3", "LGPL-3.0"),
    (False, "LesserGPLv3+", "LGPL-3.0+"),
    (False, "LibraryGPLv2", "LGPL-2.0"),
    (False, False, "gSOAP-1.3b"),
    #fossology had a gSOAP_v1.3 license, but I don't know if it was 'b'
    (False, False, "HPND"),
    (False, False, "IBM-pibs"),
    ("IBM-PL_v1.0", False, "IPL-1.0"),
    #Ninka had IBMv1, but I didn't know if it was this one
    (False, False, "Imlib2"),
    (False, False, "IJG"),
    #fossology had JPEG/netpbm, but I don't know if its "independent JPEG"
    ("Intel", False, "Intel"),
    #Ninka had IntelACPILic, not sure if it is Intel Open Source License
    ("IPA", False, "IPA"),
    ("ISC", False, "ISC"),
    (False, False, "JSON"),
    ("LPPL_v1.3a", False, "LPPL-1.3a"),
    ("LPPL_v1.1", False, "LPPL-1.1"),
    ("LPPL_v1.2", False, "LPPL-1.2"),
    ("LPPL_v1.3c", False, "LPPL-1.3c"),
    (False, False, "Libpng"),
    ("Lucent_v1.02", False, "LPL-1.02"),
    ("Lucent_v1.0", False, "LPL-1.0"),
    ("Ms-PL", False, "MS-PL"),
    ("Ms-RL", False, "MS-RL"),
    (False, False, "MirOS"),
    ("MIT", False, "MIT"),
    #Ninka has many MIT variants, I assume MITModern is the closest
    (False, False, "Motosoto"),
    ("MPL_v1.0", "MPLv1_0", "MPL-1.0"),
    ("MPL_v1.1", "MPLv1_1", "MPL-1.1"),
    ("MPL_v2.0", "MPLv2", "MPL-2.0"),
    (False, False, "MPL-2.0-no-copyleft-exception"),
    (False, False, "Multics"),
    ("NASA_v1.3", False, "NASA-1.3"),
    ("Naumen", False, "Naumen"),
    (False, False, "NBPL-1.0"),
    ("Nethack", False, "NGPL"),
    ("Netizen", False, "NOSL"),
    ("NPL_v1.0", "NPLv1_0", "NPL-1.0"),
    ("NPL_v1.1", "NPLv1_1", "NPL-1.1"),
    ("Nokia_v1.0a", False, "Nokia"),
    #fossoloy had "Nokia" as well, but this is more precise
    (False, False, "NPOSL-3.0"),
    (False, False, "NTP"),
    ("OCLC_v2.0", False, "OCLC-2.0"),
    (False, False, "ODbL-1.0"),
    (False, False, "PDDL-1.0"),
    ("OpenGroupTest", False, "OGTSL"),
    (False, False, "OLDAP-2.2.2"),
    (False, False, "OLDAP-1.1"),
    ("OpenLDAP_v1.2", False, "OLDAP-1.2"),
    (False, False, "OLDAP-1.3"),
    ("OpenLDAP_v1.4", False, "OLDAP-1.4"),
    (False, False, "OLDAP-2.0"),
    (False, False, "OLDAP-2.0.1"),
    (False, False, "OLDAP-2.1"),
    (False, False, "OLDAP-2.2"),
    (False, False, "OLDAP-2.2.1"),
    (False, False, "OLDAP-2.3"),
    (False, False, "OLDAP-2.4"),
    ("OpenLDAP_v2.5", False, "OLDAP-2.5"),
    ("OpenLDAP_v2.6", False, "OLDAP-2.6"),
    ("OpenLDAP_v2.7", False, "OLDAP-2.7"),
    ("Open-PL_v1.0", False, "OPL-1.0"),
    ("OSL_v1.0", False, "OSL-1.0"),
    ("OSL_v2.0", False, "OSL-2.0"),
    ("OSL_v2.1", False, "OSL-2.1"),
    ("OSL_v3.0", False, "OSL-3.0"),
    ("OpenLDAP_v2.8", False, "OLDAP-2.8"),
    ("OpenSSL", "openSSL", "OpenSSL"),
    #Ninka has oppenSSLvar1, var3, and LinkExceptionOpenSSL as well
    ("PHP_v3.0", False, "PHP-3.0"),
    ("PHP_v3.01", "phpLicV3.01", "PHP-3.01"),
    (False, "postgresql", "PostgreSQL"),
    ("Python_v2", False, "Python-2.0"),
    ("QPL_v1.0", False, "QPL-1.0"),
    ("RPSL_v1.0", False, "RPSL-1.0"),
    ("RPL_v1.1", False, "RPL-1.1"),
    ("RPL_v1.5", False, "RPL-1.5"),
    (False, False, "RHeCos-1.1"),
    #Several Redhat options were in Fossology, but not specifically eCos
    ("Ricoh_v1.0", False, "RSCPL"),
    #Fossology had "Ricoh" as well, but this is more precise
    ("Ruby", False, "Ruby"),
    (False, False, "SAX-PD"),
    (False, False, "SGI-B-1.0"),
    (False, False, "SGI-B-1.1"),
    (False, False, "SGI-B-2.0"),
    #Fossology had several SGI things, but none of them specified licesne B
    (False, False, "OFL-1.0"),
    (False, False, "OFL-1.1"),
    (False, False, "SimPL-2.0"),
    #Ninka had SimpleLic, but it didn't specify a version
    ("Sleepycat", "SleepyCat", "Sleepycat"),
    #Fossology and Ninka had several derivatives of Sleepycat
    (False, False, "SMLNJ"),
    (False, False, "SugarCRM-1.1.3"),
    #Fossology has SugarCRM(attribution)
    ("SISSL_v1.1", False, "SISSL"),
    (False, False, "SISSL-1.2"),
    ("Sun-PL_v1.0", False, "SPL-1.0"),
    (False, False, "Watcom-1.0"),
    #Fossology had a licesne called Sybase, not sure if it's the same
    (False, False, "NCSA"),
    (False, False, "VSL-1.0"),
    #Fossology has Vovida, but I don't know if it's 1.0
    ("W3C", "W3CLic", "W3C"),
    ("wxWindows-LGPL", False, "WXwindows"),
    (False, False, "Xnet"),
    ("X11", "X11", "X11"),
    #Ninka also has many X11 derivatives (mostly MIT based)
    (False, False, "XFree86-1.1"),
    (False, False, "YPL-1.0"),
    (False, False, "YPL-1.1"),
    #Fossology had Yahoo, but no version number
    (False, False, "Zimbra-1.3"),
    ("zlib/libpng", False, "Zlib"),
    (False, False, "ZPL-1.1"),
    ("Zope-PL_v2.0", False, "ZPL-2.0"),
    (False, False, "ZPL-2.1"),
    (False, False, "Unlicense")
    ]
