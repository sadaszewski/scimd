#
# Copyright (C) 2015, Stanislaw Adaszewski
# s.adaszewski@gmail.com
# http://algoholic.eu
#
# License: 2-clause BSD
#


from markdown import Extension
from markdown.blockprocessors import BlockProcessor
from markdown.util import etree
import numpy as np
from collections import defaultdict


class TableExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.parser.blockprocessors.add('table',
                                      TableProcessor(md.parser),
                                      '<hashheader')


def makeExtension(configs={}):
    return TableExtension(configs=configs)


class TableProcessor(BlockProcessor):
    def test(self, parent, block):
        lines = block.split('\n')
        for l in lines:
            if set(l.strip()) == set(('-', '|')):
                return True
        return False

    def run(self, parent, blocks):
        block = blocks.pop(0)
        lines = map(lambda x: list(x.strip()), block.split('\n'))
        ary = np.array(lines, dtype='|S1')
        cstart = np.zeros(ary.shape, dtype=np.int)
        cend = np.zeros(ary.shape, dtype=np.int)
        for r in xrange(ary.shape[0]):
            for c in xrange(ary.shape[1]):
                if ary[r, c] == '|':
                    if c + 1 < ary.shape[1] and (r == 0 or ary[r - 1, c + 1] == '-'):
                        cstart[r, c] = True
                    if c > 0 and (r + 1 == ary.shape[0] or ary[r + 1, c - 1] == '-'):
                        cend[r, c] = True
        cstart = zip(*np.nonzero(cstart))
        cend = zip(*np.nonzero(cend))
        # print 'cstart:', cstart
        # print 'cend:', cend
        rpos = np.nonzero(np.max(ary == '-', axis=1))
        cpos = np.nonzero(np.max(ary == '|', axis=0))
        # print rpos
        # print cpos
        assert(len(cstart) == len(cend))
        cells = []
        for k in xrange(len(cstart)):
            r, c = cstart[k][0], cstart[k][1] + 1
            while r < ary.shape[0] and c < ary.shape[1]:
                # print r, c
                if ary[r, c] == '|':
                    if (r, c) in cend:
                        rowspan = len(np.nonzero((rpos >= cstart[k][0]) * (rpos <= r))[0]) + 1
                        colspan = len(np.nonzero((cpos >= cstart[k][1]) * (cpos <= c))[0]) - 1
                        # print 'Cell', k, cstart[k], (r, c), 'rowspan:', rowspan, 'colspan:', colspan
                        # print '    %s' % ary[cstart[k][0]:r+1, cstart[k][1]:c-1].tostring()
                        cells.append((cstart[k], (r, c), rowspan, colspan))
                        break
                    else:
                        r += 1
                        c = cstart[k][1]
                c += 1
        # print cells
        table = etree.SubElement(parent, 'table')
        # table.set('style', 'border: solid 1px black;')
        table.set('border', '1')
        rows = defaultdict(lambda: [])
        for k in xrange(len(cells)):
            cell = cells[k]
            r = len(np.nonzero(rpos < cells[k][0][0])[0])
            c = len(np.nonzero(cpos < cells[k][0][1])[0])
            # print 'Cell', k, 'r:', r, 'c:', c, 'rowspan:', cells[k][2], 'colspan:', cells[k][3]
            text = '\n'.join(map(lambda x: x.tostring().strip(), ary[cells[k][0][0]:cells[k][1][0]+1, cells[k][0][1]+1:cells[k][1][1]]))
            # print '    %s' % text
            rows[r].append((text, cells[k][2], cells[k][3]))
        for r in xrange(len(rows)):
            # print 'Row', r
            tr = etree.SubElement(table, 'tr')
            for c in xrange(len(rows[r])):
                td = etree.SubElement(tr, 'td')
                td.text = rows[r][c][0]
                td.set('rowspan', str(rows[r][c][1]))
                td.set('colspan', str(rows[r][c][2]))
        # return table
