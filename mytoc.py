#
# Copyright (C) 2015, Stanislaw Adaszewski
# s.adaszewski@gmail.com
# http://algoholic.eu
#
# License: 2-clause BSD
#


from markdown import Extension
from markdown.blockprocessors import BlockProcessor
from markdown.inlinepatterns import Pattern
from markdown.treeprocessors import Treeprocessor
from markdown.util import etree, AtomicString
from collections import defaultdict
import re
import sys
from StringIO import StringIO


class MyTocExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        # raise ValueError(md.treeprocessors)
        md.treeprocessors.add('mytoc', MyTocTreeProcessor(md), '<prettify')


def makeExtension(configs={}):
    return MyTocExtension(configs=configs)


class MyTocTreeProcessor(Treeprocessor):
    def run(self, root):
        # print 'Running...', dir(self)
        hdrtags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']

        Q = [[None, 0, root]]
        cnt = []
        active = False
        toc = ''
        while len(Q) > 0:
            [parent, idx, el] = Q.pop(0)
            for i in xrange(len(el)): # .iteritems():
                ch = el[i]
                Q.append([el, i, ch])

            # print el.tag
            if el.tag == 'p' and el.text == 'CONTENT-START':
                #print el.get('name')
                #sys.stderr.write(el.tag)
                #raise ValueError('content-start')
                root.remove(el) # .remove()
                active = True
            elif el.tag == 'p' and el.text == 'CONTENT-END':
                active = False
                root.remove(el)
            elif active and el.tag in hdrtags:


                lvl = int(el.tag[1])
                # lvl = min(lvl, 3)
                if lvl > 3: continue

                cnt2 = cnt[0:lvl]
                if len(cnt2) == lvl:
                    cnt2[-1] += 1
                else:
                    cnt2 += [1]

                nmbrs = '.'.join(map(str, cnt2)) + '. '

                tgt = etree.Element('a')
                tgt.set('name', 'hdr' + nmbrs[:-2].replace('.', '_'))
                for idx in xrange(len(parent)):
                    if parent[idx] == el:
                        break
                parent.insert(idx, tgt)
                #el.setparent(tgt)
                parent.remove(el)
                tgt.append(el)
                #el.insert(0, tgt)
                #el.set('name', 'hdr' + nmbrs[:-2])

                entry = '<li><a href="#hdr' + nmbrs[:-2].replace('.', '_') + '">' + nmbrs + el.text + '</a><a class="pagenum" href="#hdr' + nmbrs[:-2].replace('.', '_') + '"></a><span class="tocline"></span>'
                if lvl == len(cnt):
                    toc += '</li>' + entry
                elif lvl == len(cnt) + 1:
                    toc += '<ol style="list-style-type: none;">' + entry
                elif lvl < len(cnt):
                    toc += '</li></ol>' * (len(cnt) - lvl)
                    toc += '</li>' + entry
                else:
                    raise ValueError('Improper nesting: %d %d' % (lvl, len(cnt)))

                cnt = cnt2

                el.text = '.'.join(map(str, cnt)) + '. ' + el.text

        toc += '</li></ol>'
        #raise ValueError(toc)
        #toc = '<ol></ol>'
        # import xml.etree.cElementTree
        toc = etree.parse(StringIO(str(toc)))
        # toc = etree.parse(StringIO(toc))

        Q = [root]
        while len(Q) > 0:
            el = Q.pop(0)
            for ch in el:
                Q.append(ch)

            if el.tag == 'p' and el.text == 'TABLE-OF-CONTENT':
                el.text = ''
                el.append(toc.getroot())