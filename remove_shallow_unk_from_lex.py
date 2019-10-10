#! /bin/python
# coding: utf-8

####################################################################
# dicrcのeval-sizeで，テストデータにしか現れない単語を
# lex.csvから除去したファイルを作成するスクリプト
####################################################################

import argparse
import codecs
import sys

from toolbox import *

reload(sys)
sys.setdefaultencoding('utf-8')


# dicrcからevalsizeを取得するメソッド
def get_eval_size(dicrc):
    eval_size = -1
    with codecs.open(dicrc, 'r', 'utf-8') as fin:
        for line in fin:
            if line.startswith(u'eval-size'):
                eval_size = int(line.split(u'=')[1].strip())
                break
    print u'eval-size: ', eval_size
    return eval_size


def main(trainfile, testfile, lexfile, outputfile, dicrc):

    # フィールド中の語一意識別キーの範囲を設定
    eval_size = get_eval_size(dicrc)

    print u'discriminative key = fields[:%s]' % eval_size

    # trainの読み込み
    train_set = set()
    with codecs.open(trainfile, 'r', 'utf-8') as fin:
        for line in fin:
            line = line.rstrip(u'\r\n')
            if line and (line != u'EOS'):
                fields = csv_splitter(line.split(u'\t')[1])
                key = tuple(fields[:eval_size])
                train_set.add(key)

    # testの読み込み
    test_set = set()
    with codecs.open(testfile, 'r', 'utf-8') as fin:
        for line in fin:
            line = line.rstrip(u'\r\n')
            if line and (line != u'EOS'):
                fields = csv_splitter(line.split(u'\t')[1])
                key = tuple(fields[:eval_size])
                test_set.add(key)

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
                    if key not in remove_set:
                        fout.write(line + u'\n')
                    else:
                        print u'remove (', csv_joinner(list(key)), u')'
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

    args = parser.parse_args()

    main(args.train, args.test, args.lex, args.out, args.dicrc)


