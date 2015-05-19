'''Parse the output of the nomos license scanner.'''
import re

pattern = re.compile('File (.+?) contains license\(s\) (.+)')

def parser(iterable):
    m = None
    for item in iterable:
        m = re.match(pattern, item)
        if m is None:
            continue
        yield [m.group(1), m.group(2)]

def parse_one(s):
    p = parser([s])
    for single_item in p:
        return single_item
