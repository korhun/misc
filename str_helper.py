import re
import sys
from fnmatch import fnmatch
from typing import Iterator


def is_url_valid(url) -> bool:
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return re.match(regex, url) is not None


def wildcard(txt, pattern, case_insensitive=True):
    if txt == pattern:
        return True
    else:
        return fnmatch(txt.lower(), pattern.lower()) if case_insensitive else fnmatch(txt, pattern)


def wildcard_match_count(list_txt, pattern, case_insensitive=True):
    count = 0
    for txt in list_txt:
        if wildcard(txt, pattern, case_insensitive):
            count += 1
    return count


def wildcard_has_match(list_txt, pattern, case_insensitive=True):
    for txt in list_txt:
        if wildcard(txt, pattern, case_insensitive):
            return True
    return False
