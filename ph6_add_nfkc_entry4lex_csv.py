#! /bin/python
# coding: utf-8

import codecs
import unicodedata as ud
from toolbox import *

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def main(input_file, output_file):

    # 読み込み
    surface_set = set()
    line_list = []
    with codecs.open(input_file, 'r', 'utf-8') as fin:
        for line in fin:
            line = line.lstrip(u'\ufeff\ufffe')
            line = line.rstrip(u'\r\n')
            if line and (line[0] != u','):
                line_list.append(line)
                line = csv_splitter(line)
                surface = line[0]
                surface_set.add(surface)

    # NFKCエントリ追加
    output_line_list = []
    for line in line_list:
        output_line_list.append(line)
        line = csv_splitter(line)
        surface = line[0]
        nfkc_surface = ud.normalize('NFKC', surface)
        if (surface != nfkc_surface) and (len(surface) == len(nfkc_surface)) and (nfkc_surface not in surface_set):
            print surface, nfkc_surface
            line[0] = nfkc_surface
            line = csv_joinner(line)
            print line
            output_line_list.append(line)

    # 書き出し
    with codecs.open(output_file, 'w', 'utf-8') as fout:
        for line in output_line_list:
            if line and (line[0] not in [u',', u' ']):
                fout.write(line + u'\n')


if __name__ == '__main__':

    argvs = sys.argv
    argc = len(argvs)

    if argc != 3:

        print ''
        print 'python add_nfkc_entry4lex_csv.py inputfile(src_lex.csv) outputfile(nfkc_added_lex.csv)'
        print ''

    else:

        main(argvs[1], argvs[2])

