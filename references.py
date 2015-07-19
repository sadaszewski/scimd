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


class ReferencesExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        # print md.inlinePatterns
        md.sciref = {}
        md.inlinePatterns.add('references', ReferencePattern(r'\[([0-9]+)\]', md), '<emphasis')
        md.parser.blockprocessors.add('references',
                                      ReferencesBlockProcessor(md.parser),
                                      '<hashheader')
        # print md.treeprocessors
        md.treeprocessors.add('references', ReferencesTreeProcessor(md), '<prettify')


def makeExtension(configs={}):
    return ReferencesExtension(configs=configs)


class ReferencePattern(Pattern):
    def handleMatch(self, m):
        # print 'here'
        # print dir(self.markdown)
        a = etree.Element('a')
        a.set('href', '#ref_%s' % m.group(2))
        a.text = AtomicString('[%s]' % m.group(2))
        return a


class ReferencesTreeProcessor(Treeprocessor):
    def run(self, root):
        # print 'Running...', dir(self)
        Q = [root]
        cnt = 0
        M = {}
        sciref = self.markdown.sciref
        O = []
        while len(Q) > 0:
            el = Q.pop(0)
            # print 'Here', el
            for ch in el:
                Q.append(ch)

            if el.tag == 'a' and el.get('href') != None and el.get('href').startswith('#ref_'):
                # print 'Here'
                href = el.get('href')
                if href in M:
                    el.text = M[href]
                else:
                    cnt += 1
                    O.append(re.match(r'#ref_([0-9]+)', href).group(1))
                    el.text = M[href] = '[%d]' % cnt
        # print sciref

        Q = [root]
        while len(Q) > 0:
            el = Q.pop(0)
            for ch in el:
                Q.append(ch)
            if el.tag == 'div' and el.get('class') == 'sciref':
                ol = etree.SubElement(el, 'ol')
                for o in O:
                    li = etree.SubElement(ol, 'li')
                    a = etree.SubElement(li, 'a')
                    a.set('name', 'ref_%s' % o)
                    span = etree.SubElement(li, 'span')
                    span.text = sciref[o]
                    # print sciref[o]


class ReferencesBlockProcessor(BlockProcessor):
    def test(self, parent, block):
        # print 'Testing', block, self.lastChild(parent), self.lastChild(parent).text if self.lastChild(parent) is not None else None
        # return False
        ch = self.lastChild(parent)
        if ch is None or ch.text is None or ch.text.lower() != 'references':
            # print 'Early return'
            return False
        if all(map(lambda x: re.match('^[0-9]+\.', x.strip()) is not None, block.split('\n'))):
            return True
        return False


    def run(self, parent, blocks):
        block = blocks.pop(0)
        lines = map(lambda x: x.strip(), block.split('\n'))
        R = self.parser.markdown.sciref
        for l in lines:
            m = re.match(r'([0-9]+)\. (.+)', l)
            R[m.group(1)] = m.group(2)
        # print R
        # S = dir(self.parser.markdown)
        # print S
        sciref = etree.SubElement(parent, 'div')
        sciref.set('class', 'sciref')
