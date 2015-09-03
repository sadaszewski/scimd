#
# Copyright (C) 2015, Stanislaw Adaszewski
# s.adaszewski@gmail.com
# http://algoholic.eu
#
# License: 2-clause BSD
#


from markdown import Extension
from markdown.blockprocessors import BlockProcessor
from markdown.treeprocessors import Treeprocessor
from markdown.util import etree, AtomicString
import numpy as np
from collections import defaultdict
import re
from markdown.inlinepatterns import Pattern


class FigureExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns.add('figref', FigRefPattern(r'\[([A-Za-z]+ [0-9]+)\]', md), '<emphasis')
        md.parser.blockprocessors.add('figure',
                                      FigureProcessor(md.parser),
                                      '<hashheader')
        md.treeprocessors.add('figure', FigureTreeProcessor(md), '<prettify')


def makeExtension(configs={}):
    return FigureExtension(configs=configs)


class FigRefPattern(Pattern):
    def handleMatch(self, m):
        hash = m.group(2).lower().replace(' ', '_')
        a = etree.Element('a')
        a.set('href', '#figref_%s' % hash)
        a.text = AtomicString('[%s]' % m.group(2))
        return a


class FigureProcessor(BlockProcessor):
    def test(self, parent, block):
        return re.match(r'^[A-Za-z]+ [0-9]+\.', block) is not None

    def run(self, parent, blocks):
        block = blocks.pop(0)
        m = re.match(r'[A-Za-z]+ [0-9]+\.', block)
        caption = block[m.span()[1]:].strip()
        p = etree.SubElement(parent, 'p')
        a = etree.SubElement(p, 'a')
        hash = m.group(0).lower().replace('.','').replace(' ', '_')
        a.set('name', 'figref_%s' % hash)
        a.text = '%s %s' % (m.group(0), caption)


class FigureTreeProcessor(Treeprocessor):
    def run(self, root):
        # print 'Running...', dir(self)
        cnt = defaultdict(lambda: 0)
        M = {}

        Q = [root]
        while len(Q) > 0:
            el = Q.pop(0)
            for ch in el: Q.append(ch)
            name = el.get('name')
            if el.tag == 'a' and name is not None and name.startswith('figref_'):
                type_ = name.split('_')[1]
                title = '.'.join(el.text.split('.')[1:])
                if name not in M:
                    cnt[type_] += 1
                    M[name] = str(cnt[type_])

                el.text = type_[0].upper() + type_[1:] + ' ' + M[name] + '. ' + title

        Q = [root]
        while len(Q) > 0:
            el = Q.pop(0)
            # print 'Here', el
            for ch in el:
                Q.append(ch)

            href = el.get('href')
            if el.tag == 'a' and href is not None and href.startswith('#figref_'):
                type_ = href.split('_')[1]
                #if href in M:
                #    pass
                #else:
                #    cnt[type_] += 1
                #    M[href] = str(cnt[type_])

                el.text = '[%s %s]' % (type_[0].upper() + type_[1:], M[href[1:]])


