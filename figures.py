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

_captions = {}

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
        _captions[a.get('name')] = caption


# import sys

def stringify(el):
    Q = [el]
    ret = ''
    # raise ValueError(el[0][0].text)
    while len(Q) > 0:
        el = Q.pop(0)
        for ch in el:
            Q.append(ch)
        if el.text is not None: ret += el.text
        if el.tail is not None: ret += el.tail

    return ret

class FigureTreeProcessor(Treeprocessor):
    def run(self, root, M={}):
        # print 'Running...', dir(self)
        hdrtags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']

        cnt = defaultdict(lambda: 0)
        # M = {}

        '''Q = [root]
        test = u''
        while len(Q) > 0:
            el = Q.pop(0)
            for ch in el: Q.append(ch)
            #if el.tail is not None:
             #   dummy = etree.Element('dummy')
              #  dummy.text = el.tail
               # Q.append(dummy)
            if el.text is not None: test += el.text
            if el.tail is not None: test += el.tail

            # print (el)
        print test.encode('utf-8')
        # raise ValueError(test[:50])'''

        Q = [root]
        hdrcnt = []
        active = False
        nmbrs = ''
        L = defaultdict(lambda: [])
        while len(Q) > 0:
            el = Q.pop(0)
            for ch in el: Q.append(ch)

            if el.tag == 'p' and el.text == 'CONTENT-START':
                active = True
            elif el.tag == 'p' and el.text == 'CONTENT-END':
                active = False
                nmbrs = ''
            elif active and el.tag in hdrtags:
                lvl = int(el.tag[1])
                # lvl = min(lvl, 3)
                if lvl <= 3:
                    hdrcnt = hdrcnt[0:lvl]
                    if len(hdrcnt) == lvl:
                        hdrcnt[-1] += 1
                    else:
                        hdrcnt += [1]
                    nmbrs = '.'.join(map(str, hdrcnt)) + '.'


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
                    cnt[nmbrs + type_] += 1
                    M[name] = nmbrs + str(cnt[nmbrs + type_])
                    L[type_].append({'href': '#' + name, 'el': el, 'text': type_[0].upper() + type_[1:] + ' ' + M[name] + '.' + ''.join(stringify(el).split('.')[1]) + '.'}) #  + _captions[name]})

                # raise ValueError(len(type_))
                el[0].text = type_[0].upper() + type_[1:] + ' ' + M[name] + '. ' + title

        md = self.markdown
        this = self
        def rewrite_self_references(txt):
            fr = md.inlinePatterns['figref']
            rx = fr.getCompiledRegExp()
            # matches = rx.findall(txt)

            while True:
                match = rx.match(txt)
                if match is not None:
                    pos = match.start(2)
                    endpos = match.end(2)
                    # raise ValueError(match.end(2))
                    a = fr.handleMatch(match)
                    this.run(a, M)
                    txt = txt[0:pos] + a.text[1:-1] + txt[endpos:]
                else:
                    break
            return txt


        Q = [(-1, None, root)]
        insert_cnt = defaultdict(lambda : 0)
        while len(Q) > 0:
            (idx, parent, el) = Q.pop(0)
            # print 'Here', el
            cnt = 0
            for ch in el:
                Q.append((cnt, el, ch))
                cnt += 1

            href = el.get('href')
            if el.tag == 'a' and href is not None and href.startswith('#figref_'):
                type_ = href.split('_')[1]
                #if href in M:
                #    pass
                #else:
                #    cnt[type_] += 1
                #    M[href] = str(cnt[type_])

                el.text = '[%s %s]' % (type_[0].upper() + type_[1:], M[href[1:]])
            elif el.tag == 'p' and el.text is not None and el.text.startswith('LIST-OF-'):
                type_ = el.text[8:-1].lower()
                # raise ValueError(L['figure'])
                for fig in L[type_]:
                    p = etree.Element('p')
                    p.set('style', 'width: 75%;')
                    # p.text = fig['text']
                    a = etree.SubElement(p, 'a')
                    a.set('href', fig['href'])
                    # a.set('style', 'color: white; font-size: 1px; height: 1el; display: block-inline;')
                    a.text = rewrite_self_references(fig['text']) #  ' + fig['text'][:20]
                    self.markdown.treeprocessors['myreferences'].run(p)
                    parent.insert(insert_cnt[parent] + idx, p)
                    insert_cnt[parent] += 1
                    # Q.append((-1, parent, p))

                parent.remove(el)

