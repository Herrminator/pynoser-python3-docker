#!/usr/bin/env python
#@PydevCodeAnalysisIgnore
__revision__ = "None!"

from runtime import settings  # @UnusedImport
import re
from pynoser.reader.models import Article
from django.db.models import Q

FEEDS    = [ 338 ]

IMG_PATT = re.compile(r'^(!\[[^\]]+\])\(data:.+', re.I)
IMG_FILT = Q(feed__in=FEEDS) & Q(text__iregex=IMG_PATT.pattern)

# ...but delete Article objects do remove alle dependent objects
art = Article.objects.filter(IMG_FILT)

s = 0
for a in art:
  print((a.title))
  s += len(a.text)
  
if art.count() > 0:
  ok = input("Changing {0} articles ({1}k). Continue? ".format(art.count(), s / 1024))
  if ok == 'y':
    s = 0
    for a in art:
      new = IMG_PATT.sub("\\1", a.text)
      a.text = new
      a.save()
      s += len(new)

    print("Modfied ({0}k left). Reorganizing...".format(s / 1024))
    db.reorg()
