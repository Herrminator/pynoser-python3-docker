#!/usr/bin/env python

import sys, argparse
import http.cookiejar
import urllib.request, urllib.error, urllib.parse
from   runtime import settings

# TODO: The problems seem come from the parallel execution in batchupd_mt.py
# So, the *REAL* solution would be, to serialize access to the cookie jar
# in reader/feed.py with a semaphore! This wouldn't be a big problem either,
# because the cookie jar is already a process wide singleton.

def main(argv=sys.argv[1:]):
    ap = argparse.ArgumentParser()
    ap.add_argument(      "cookiejar",       default=settings.COOKIE_JAR_FILE, nargs="?")
    ap.add_argument("-f", "--remove-failed", default=False, action="store_true")
    ap.add_argument("-v", "--verbose",       default=0, action="count")
    args = ap.parse_args(argv)

    if not args.cookiejar:
        if args.verbose: print("No cookiejar file defined. Done.")
        return 0

    if args.verbose > 1:
        import logging
        logging.basicConfig(level=logging.DEBUG if args.verbose > 2 else logging.INFO)
        http.cookiejar.debug = True

    try:
        cookiejar = http.cookiejar.LWPCookieJar(args.cookiejar)
        cookiejar.load()
    except Exception as exc:
        print("Error opening cookie jar {0}: {1}. Please check!".format(args.cookiejar, exc))
        return 8

    mod = False

    for cookie in cookiejar:
        if args.verbose: print(cookie.domain)

        req = urllib.request.Request("https://{0}/not/root".format(cookie.domain))
        try:
            cookiejar.add_cookie_header(req)
        except Exception as exc:
            print("ERROR: Cookie for domain {0.domain}, path {0.path}, {0.name}='{0.value}' failed: {1}".format(cookie, exc))
            if args.remove_failed:
                path, name = ( cookie.path, # one of the problems is, that "path;" results in path==None
                               cookie.name if cookie.path is not None else None, # so we have to clear *all* cookies for that domain :()
                )
                cookiejar.clear(domain=cookie.domain, path=path, name=name)
                print("Removed {0}, path {1}, name {2}.{3}"
                        .format(cookie.domain, path, name, " All cookies for domain removed." if path is None and name is None else ""))
                mod = True

    if mod:
        cookiejar.save()

    return 0

if __name__ == "__main__":
    sys.exit(main())
