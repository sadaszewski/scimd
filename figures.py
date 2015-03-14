#
# Copyright (C) 2015, Stanislaw Adaszewski
# s.adaszewski@gmail.com
# http://algoholic.eu
#
# License: 2-clause BSD
#


from markdown import Extension
from markdown.blockprocessors import BlockProcessor
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


def makeExtension(configs={}):
    return FigureExtension(configs=configs)


class FigRefPattern(Pattern):
    def handleMatch(self, m):
        hash = m.group(2).lower().replace(' ', '_')
        a = etree.Element('a')
        a.set('href', '#%s' % hash)
        a.text = AtomicString('[%s]' % m.group(2))
        return a


class FigureProcessor(BlockProcessor):
    def test(self, parent, block):
        return re.match(r'^[A-Za-z]+ [0-9]+\.', block) is not None

    def run(self, parent, blocks):
        block = blocks.pop(0)
        m = re.match(r'[A-Za-z]+ [0-9]+\.', block)
        caption = block[m.span()[1]:].strip()
        a = etree.SubElement(parent, 'a')
        hash = m.group(0).lower().replace('.','').replace(' ', '_')
        a.set('name', '%s' % hash)
        a.text = caption
