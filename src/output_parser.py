#!/usr/bin/python
"""
Parses the output of FOSSology and Ninka scans. This file is for internal use
only and is called by dual_scan.py.

@author Doug Richardson
@author Jon von Kampen
@author James Thompson

@license Apache License 2.0
"""

import license_compare


def foss_parser(foss_in):
    """Default format is File myfile.c containes licence(s) L1, L2"""
    foss_tokens = foss_in.split(" ")
    license = "F_ERROR"  # If the file cannot be parsed
    file_name = "ERROR"
    #If it doesn't start with file, then nomos threw an error
    #The first license is on the 5th token
    if foss_tokens[0].strip() == 'File' and len(foss_tokens) > 4:
        for i in range(4, len(foss_tokens)):
            if license == "F_ERROR":
                license = foss_tokens[i]
            else:
                license += foss_tokens[i]
        file_name = foss_tokens[1]

    elif foss_tokens[0] == 'nomos:' and len(foss_tokens) > 2:
        temp = foss_tokens[2].split("/")
        file_name = temp[len(temp) - 1].replace("\"", "")
        """
        On non-files, nomos throws an error message with the path in quotes.
        """
        license = "ERROR"

    return (file_name, license)


def ninka_parser(ninka_in):
    """
    Default format is file_name;license(s);[other stuff we don't need]
    For our purposes we only need two things from Ninka's output:
    The file name and the confirmed license. The other components are ignored.
    """
    ninka_tokens = ninka_in.split(";")
    license = "F_ERROR"
    file_name = "ERROR"

    """
    The file is the first token and the license(s) are the second. The file is
    the absolute directory from the archive on downward. To compare it to
    FOSSology's output, we need to strip it down to the file name only.
    """
    if len(ninka_tokens) > 1:
        license = ninka_tokens[1]
        temp = ninka_tokens[0].split("/")
        file_name = temp[len(temp) - 1]

    return (file_name, license)


def lic_compare(foss_out, ninka_out):
    """Compares the licenses using a comparison dictionary."""
    foss_out = foss_out.upper().strip()
    ninka_out = ninka_out.upper().strip()

    if foss_out == ninka_out:
        return True

    #Pre-declaring some booleans to make later code more readable
    ninka_lic_found = ninka_out != "UNKNOWN" or ninka_out != "NONE"
    foss_lic_found = foss_out != "NONE" or foss_out != "UNKNOWN"

    # If both fossology and ninka have valid output
    if(ninka_lic_found and ninka_lic_found):
            for relation in license_compare.Licenses:
                    final = len(relation) - 1
                    #The SPDX license name is ALWAYS last
                    if foss_out == str(relation[0]).upper():
                        if ninka_out.rstrip() == str(relation[1]).upper():
                            return True
    else:
        return False

    return False

def lic_join(lic_list):
    """
    Takes multiple conjunctive licenses and concatenates them with AND (the
    SPDX standard). The default input is separated by commas.

    Currently, there is no way to handle disjunctive licenses (that would be
    separated by OR in the SPDX 1.2 spec).
    """
    result = "ERROR"  # Should never come up (famous last words).
    if len(lic_list) > 1:
        result = " AND ".join(lic_list)
    else:
        result = lic_list[0]
    return result
