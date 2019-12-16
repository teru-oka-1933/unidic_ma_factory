#! /bin/python
# coding: utf-8

####################################################################
# 大納言からdumpしたlex.csvは改行が\r\nかつ，
# posが「-」でつなげて1フィールドになっているので修正するスクリプト
####################################################################

import codecs
from toolbox import *
import re

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def main(input_file, rewrite_def, output_file):

    ########################################################
    # rewrite.defを読み込み (この列名で並び替えを実施)
    ########################################################

    # 列名をコメントした行を読むためのパターン(stripした行に対して適用)
    pattern_comment_node = re.compile(u'^# *node *:$')
    pattern_comment_unk = re.compile(u'^# *unk *:$')
    pattern_node = re.compile(u'^# *\$(?P<NUM>\d+) *: *(?P<NAME>.+)$')

    rewrite_map = {}
    __ADD__ = False
    with codecs.open(rewrite_def, 'r', 'utf-8') as fin:
        for line in fin:
            line = line.strip()
            if line:
                if pattern_comment_node.match(line):
                    __ADD__ = True
                elif pattern_comment_unk.match(line):
                    break
                else:
                    match_node = pattern_node.match(line)
                    if __ADD__ and match_node:
                        num = int(match_node.group(u'NUM').strip())
                        name = match_node.group(u'NAME').strip()
                        rewrite_map[num] = name

    ########################################################
    # named_tsvを読み込みながら適宜列を書き換えて書き出し
    ########################################################

    with codecs.open(output_file, 'w', 'utf-8') as fout:
        with codecs.open(input_file, 'r', 'utf-8') as fin:
            for line in fin:
                line = line.lstrip(u'\ufeff')
                line = line.rstrip(u'\r\n')
                # 1行を辞書化
                if line:
                    line = line.split(u'\t')
                    field_map = {u'pos1':u'*', u'pos2':u'*', u'pos3':u'*', u'pos4':u'*'}
                    for field in line:
                        f_name = field.split(u':')[0].strip()
                        f_val = u':'.join(field.split(u':')[1:])#.strip(u' ') # 全角スペースまで消されるので
                        if f_name == u'pos':
                            pos1_4 = f_val.split(u'-')
                            for (i, val) in enumerate(pos1_4):
                                field_map[u'pos'+unicode(i+1)] = val
                        else:
                            field_map[f_name] = f_val
                    # デフレスパイラル削除
                    if field_map[u'orth'] in [u'デフレスパイラル', u'インフレリスク', u'アルミサッシ',
                                              u'アルミホイル', u'アルミパネル', u'アルミチューブ']:
                        continue
                    # rewriteの列順に従って出力
                    output_line = []
                    for num in sorted(rewrite_map.keys()):
                        f_name = rewrite_map[num]
                        if field_map[f_name]:
                            output_line.append(field_map[f_name])
                        else:
                            output_line.append(u'*')
                        # output_line.append(field_map[f_name])
                    output_line = csv_joinner([field_map[u'orth'], u'0', u'0', u'0'] + output_line)
                    lemma_id = unicode(long(field_map[u'lid']) >> 38)
                    output_line += u',%s,%s\n' % (field_map[u'lid'], lemma_id)
                    if not output_line.startswith(u','):
                        fout.write(output_line)


if __name__ == '__main__':

    argvs = sys.argv
    argc = len(argvs)

    if argc != 4:

        print ''
        print 'python ntsv_lex2csv.py inputfile(named_tsv) rewrite.def outputfile(.csv)'
        print ''

    else:

        main(argvs[1], argvs[2], argvs[3])


