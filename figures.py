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
from markdown.preprocessors import Preprocessor


class FigureExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns.add('figref', FigRefPattern(r'\[([A-Za-z]+ [0-9]+)\]', md), '<emphasis')
        # md.inlinePatterns.add('fig', FigPattern(r'^((Figure|Table|Listing) ([0-9]+))\. (.+)', md), '<emphasis')
        md.parser.blockprocessors.add('figure',
                                      FigureProcessor(md.parser),
                                      '<hashheader')
        md.treeprocessors.add('figure', FigureTreeProcessor(md), '<prettify')
        # raise ValueError(md.preprocessors)
        # md.preprocessors.add('figure', FigPreproc(md), '<html_block')


def makeExtension(configs={}):
    return FigureExtension(configs=configs)


class FigPreproc(Preprocessor):
    def run(self, lines):
        new_lines = []
        in_caption = False
        for line in lines:
            m = re.match(r'((Table|Figure|Listing) ([0-9]+))\.', line)
            if m is not None:
                new_lines.append(u'<div class="figcaption">')
                new_lines.append(u'')
                in_caption = True
            if line == '' and in_caption:
                # raise ValueError('Here')
                new_lines.append('')
                new_lines.append(u'</div>')
                in_caption = False
            new_lines.append(line)
        # raise ValueError(new_lines)
        return new_lines


class FigRefPattern(Pattern):
    def handleMatch(self, m):
        hash = m.group(2).lower().replace(' ', '_')
        a = etree.Element('a')
        a.set('href', '#figref_%s' % hash)
        a.text = AtomicString('[%s]' % m.group(2))
        return a


class FigPattern(Pattern):
    def handleMatch(self, m):
        caption = m.group(5).strip() # block[m.span()[1]:].strip()
        # raise ValueError(caption)
        # p = etree.Element('p')
        a = etree.Element('a')
        # raise ValueError(m.group(0))
        hash = m.group(2).lower().replace('.','').replace(' ', '_')
        a.set('name', 'figref_%s' % hash)
        a.set('class', 'figcaption')
        a.text = '%s. %s' % (m.group(2), caption)
        # raise ValueError(a.text)
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
        # a.set('class', 'figcaption')
        # bold = etree.SubElement(a, 'b')
        # bold.text = m.group(0)
        # regular = etree.SubElement(a, 'span')
        # regular.text = caption
        a.text = '%s %s' % (m.group(0), caption)


# import sys

class FigureTreeProcessor(Treeprocessor):
    def run(self, root):
        # print 'Running...', dir(self)
        cnt = defaultdict(lambda: 0)
        M = {}

        Q = [root]
        while len(Q) > 0:
            el = Q.pop(0)
            for ch in el: Q.append(ch)
            # name = el.get('name')
            name = None
            if el.tag == 'p' and len(el)>0 and el[0].tag == 'a':
                name = el[0].get('name')

                # raise ValueError(name)
            if name is not None and name.startswith('figref_'):

                # raise ValueError(dir(el))
                # raise ValueError(name)
                type_ = name.split('_')[1]

                if type_ == 'figure':
                    el.set('class', 'figcaption_img')
                else:
                    el.set('class', 'figcaption')

                title = '.'.join(el[0].text.split('.')[1:])
                # raise ValueError(title)
                if name not in M:
                    cnt[type_] += 1
                    M[name] = str(cnt[type_])

                # raise ValueError(len(type_))
                el[0].text = type_[0].upper() + type_[1:] + ' ' + M[name] + '. ' + title

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


