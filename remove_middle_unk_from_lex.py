#! /bin/python
# coding: utf-8

####################################################################
# dicrcのeval-sizeを基に，testでしか出てこない語彙素idの単語を
# lex.csvから除去したファイルを作成するスクリプト
####################################################################

import argparse
import codecs
import sys
from collections import defaultdict

from remove_shallow_unk_from_lex import get_eval_size
from toolbox import *

reload(sys)
sys.setdefaultencoding('utf-8')


def main(trainfile, testfile, lexfile, outputfile, dicrc, lid_field_num):

    # フィールド中の語一意識別キーの範囲を設定
    eval_size = get_eval_size(dicrc)

    print u'discriminative key = fields[:%s]' % eval_size
    print u'lid field: fields[%s]' % lid_field_num

    # lidを得るために，lexをまず読み込み
    key2lid = defaultdict(lambda: -(len(key2lid)+1))
    with codecs.open(lexfile, 'r', 'utf-8') as fin:
        for line in fin:
            line = line.rstrip(u'\r\n')
            if line:
                fields = csv_splitter(line)[4:]
                key = tuple(fields[:eval_size])
                lid = long(fields[lid_field_num - 1]) >> 33
                key2lid[key] = lid

    # trainの読み込み
    train_set = set()
    with codecs.open(trainfile, 'r', 'utf-8') as fin:
        for line in fin:
            line = line.rstrip(u'\r\n')
            if line and (line != u'EOS'):
                fields = csv_splitter(line.split(u'\t')[1])
                key = tuple(fields[:eval_size])
                train_set.add(key2lid[key])

    # testの読み込み
    test_set = set()
    with codecs.open(testfile, 'r', 'utf-8') as fin:
        for line in fin:
            line = line.rstrip(u'\r\n')
            if line and (line != u'EOS'):
                fields = csv_splitter(line.split(u'\t')[1])
                key = tuple(fields[:eval_size])
                test_set.add(key2lid[key])

    # 差分をとる
    remove_set = test_set - train_set

    # lexの読み込みつつ，romoveして書き出し
    remove_list = []
    with codecs.open(outputfile, 'w', 'utf-8') as fout:
        with codecs.open(lexfile, 'r', 'utf-8') as fin:
            for line in fin:
                line = line.rstrip(u'\r\n')
                if line:
                    fields = csv_splitter(line)[4:]
                    key = tuple(fields[:eval_size])
                    lid = key2lid[key]
                    if lid not in remove_set:
                        fout.write(line + u'\n')
                    else:
                        print u'remove %s' % lid
                        print u'       ', line
                        remove_list.append(line)

    print u'total ', len(remove_list)


if __name__ == '__main__':

    ###############################################
    # 引数のパース
    ###############################################

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--train', type=str, required=True, help="Trainfile(.mecab)")
    parser.add_argument('--test', type=str, required=True, help='Testfile(.mecab)')
    parser.add_argument('--lex', type=str, required=True, help='Lexfile(.csv)')
    parser.add_argument('--out', type=str, required=True, help='Lex file (.csv)')
    parser.add_argument('--dicrc', type=str, required=True, default=None, help='dicrc')
    parser.add_argument('--lid', type=int, default=None, help='lemma_id field num (pos1 = [1])')

    args = parser.parse_args()

    main(args.train, args.test, args.lex, args.out, args.dicrc, args.lid)

