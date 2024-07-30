# Port from MALSync quicklinksBuilder ( https://github.com/MALSync/MALSync/blob/master/src/utils/quicklinksBuilder.ts )

import re
import logging

logger = logging.getLogger(__name__)

def title_search(url: str, title: str):
    return search_syntax(
        url.replace('{searchtermPlus}', '{searchterm(+)}')\
            .replace('{searchtermMinus}', '{searchterm(-)}')\
            .replace('{searchtermUnderscore}', '{searchterm(_)}')\
            .replace('{searchtermRaw}', '{searchterm[noEncode,noLowercase]}'),  # XXX: Check camelCase of this Lowercase
        title
    )


def search_syntax(url, title):
    logger.debug(f"{url} ||| {title}")
    match = re.search(r"{searchterm(?:\((?P<sym>.)\))?(?P<options>\[[^[\]]*\])?}", url)
    if not match:
        return url
    options = (match.group('options') if match.group('options') else str("[]"))[1:-1].split(',')
    space = match.group('sym')
    
    if "noLowerCase" not in options:
        title = title.lower()
    if "noSpecial" in options or "specialReplace" in options:
        title = re.sub(r"[^a-zA-Z\d]", "" if "noSpecial" in options else " ", title)
    if space:
        title = title.replace(" ", space)
    return url.replace(url[match.start():match.end()], title)
