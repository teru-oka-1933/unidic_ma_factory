#! /bin/python
# coding: utf-8

#############################################
# matrix.def は、右文脈id 左文脈id cost の順で書かれているのでめんどい・・・
#############################################

import codecs
import os
from toolbox import *

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


if __name__ == '__main__':

    # 引数処理
    argvs = sys.argv
    argc = len(argvs)
    if argc != 2:
        print u''
        print u'python compression_matrix_def work_final_dir'
        print u''
        sys.exit(0)

    work_final_dir = argvs[1]
    print u''

    matrix_file = os.path.join(work_final_dir, 'matrix.def')
    unk_def_file = os.path.join(work_final_dir, 'unk.def')
    left_id_def_file = os.path.join(work_final_dir, 'left-id.def')
    right_id_def_file = os.path.join(work_final_dir, 'right-id.def')
    lex_file_list = [os.path.join(work_final_dir, f) for f in os.listdir(work_final_dir) if f.endswith('.csv')]

    ######################################
    # 入力ファイルの読み込み
    ######################################

    # *.csv (lex)
    print u'Reading *.csv...'
    sys.stdout.flush()
    lex_list = []
    for lex_file in lex_file_list:
        print lex_file
        lex_list.append([])
        with codecs.open(lex_file, 'r', 'utf-8') as fin_lex:
            for line in fin_lex:
                line = line.rstrip(u'\r\n')
                if line:
                    line = csv_splitter(line)
                    lex_list[-1].append(line)
    print u'Done!'

    # unk.def
    print u'Reading unk.def...',
    sys.stdout.flush()
    unk = []
    with codecs.open(unk_def_file, 'r', 'utf-8') as fin_unk:
        for line in fin_unk:
            line = line.rstrip(u'\r\n')
            if line:
                line = csv_splitter(line)
                unk.append(line)
    print u'Done!'

    # left-id.def
    print u'Reading left-id.def...',
    sys.stdout.flush()
    left_id_line_list = []
    with codecs.open(left_id_def_file, 'r', 'utf-8') as fin_left:
        for line in fin_left:
            line = line.rstrip(u'\r\n')
            if line:
                line = line.split(u' ')
                left_id_line_list.append(line)
    print u'Done!'

    # right-id.def
    print u'Reading right-id.def...',
    sys.stdout.flush()
    right_id_line_list = []
    with codecs.open(right_id_def_file, 'r', 'utf-8') as fin_right:
        for line in fin_right:
            line = line.rstrip(u'\r\n')
            if line:
                line = line.split(u' ')
                right_id_line_list.append(line)
    print u'Done!'

    # matrix.def
    print u'Reading matrix.def...',
    sys.stdout.flush()
    matrix = []
    with codecs.open(matrix_file, 'r', 'utf-8') as fin_matrix:
        for line in fin_matrix:
            line = line.rstrip(u'\r\n')
            if line:
                line = line.split(u' ')
                if len(line) == 3:
                    matrix.append(line)
    print u'Done!'

    # 右文脈id->costのmap作成
    print u'Making right_id->cost map...',
    sys.stdout.flush()
    right_id2cost_map = {}
    for line in matrix:
        right_id = int(line[0])
        cost = int(line[2])
        if right_id not in right_id2cost_map:
            right_id2cost_map[right_id] = []
        right_id2cost_map[right_id].append(cost)
    print u'Done!'

    # 左文脈idでindexされたリストをタプル化して，キー化
    # 同一キーを持つ右文脈idを同一視
    print u'Compressing right_id...',
    sys.stdout.flush()
    right_compressed_matrix = {}
    for right_id in right_id2cost_map:
        costs = tuple(right_id2cost_map[right_id])
        # costsは左文脈IDが(暗に)indexになったコストの列
        # 元々のmatrix.def が整順した右文脈idに対し、下のように各左文脈idをツリー状に整順して配置しているので
        # 0 0 cost
        # 0 1 cost
        # 0 2 cost
        # 1 0 cost
        # 1 1 cost
        # 1 2 cost
        if costs not in right_compressed_matrix:
            right_compressed_matrix[costs] = []
        right_compressed_matrix[costs].append(right_id)  # right_compression_matrix[costs]の中身は同一視できる右文脈たち
    # 右文脈idの合一変換をmapに保存
    new_right_id = 0
    new_right_id_map = {}
    for costs in right_compressed_matrix:
        for right_id in right_compressed_matrix[costs]:
            new_right_id_map[right_id] = new_right_id
        new_right_id += 1
    print u'Done!'

    # input_matrix2
    print u'Making left_id->[(new_right_id, cost), ...] map...',
    sys.stdout.flush()
    left_id2list_of_tuple_of_new_right_id_and_cost = {}
    for line in matrix:
        right_id = int(line[0])
        left_id = int(line[1])
        cost = int(line[2])
        if left_id not in left_id2list_of_tuple_of_new_right_id_and_cost:
            left_id2list_of_tuple_of_new_right_id_and_cost[left_id] = []
        left_id2list_of_tuple_of_new_right_id_and_cost[left_id].append((new_right_id_map[right_id], cost))
    print u'Done!'

    # 右文脈idとコストのペアをキー化
    # 同一キーを持つ左文脈idを同一視
    print u'Compressing left_id...',
    sys.stdout.flush()
    left_compressed_matrix = {}
    for left_id in left_id2list_of_tuple_of_new_right_id_and_cost:
        list_of_tuple_of_new_right_id_and_cost = tuple(sorted(left_id2list_of_tuple_of_new_right_id_and_cost[left_id]))
        if list_of_tuple_of_new_right_id_and_cost not in left_compressed_matrix:
            left_compressed_matrix[list_of_tuple_of_new_right_id_and_cost] = []
        left_compressed_matrix[list_of_tuple_of_new_right_id_and_cost].append(left_id)
        # left_compression_matrix[list_of_tuple_of_new_right_id_and_cost]の中身は同一視できる左文脈たち
    # 左文脈idの合一変換をmapに保存
    new_left_id = 0
    new_left_id_map = {}
    for list_of_tuple_of_new_right_id_and_cost in left_compressed_matrix:
        for left_id in left_compressed_matrix[list_of_tuple_of_new_right_id_and_cost]:
            new_left_id_map[left_id] = new_left_id
            new_left_id += 1
    print u'Done!'

    # 圧縮したテーブルを作成
    print u'Making compressed matrix...',
    sys.stdout.flush()
    max_right_size = -sys.maxint - 1
    max_left_size = -sys.maxint - 1
    compressed_matrix = set()
    for list_of_tuple_of_new_right_id_and_cost in left_compressed_matrix:
        for left_id in left_compressed_matrix[list_of_tuple_of_new_right_id_and_cost]:
            new_left_id = new_left_id_map[left_id]
            if max_left_size < new_left_id:
                max_left_size = new_left_id
            for (new_right_id, cost) in list_of_tuple_of_new_right_id_and_cost:
                if max_right_size < new_right_id:
                    max_right_size = new_right_id
                compressed_matrix.add((new_right_id, new_left_id, cost))
    compressed_matrix = sorted(list(compressed_matrix))
    print u'Done!'

    ####################################################
    # 書き出し
    ####################################################
    print u'Writing new matrix.def...',
    sys.stdout.flush()
    os.rename(matrix_file, matrix_file + '.old')
    with codecs.open(matrix_file, 'w', 'utf-8') as fout_matrix:
        fout_matrix.write(u'%s %s\n' % (max_right_size+1, max_left_size+1))
        for (new_right_id, new_left_id, cost) in compressed_matrix:
                fout_matrix.write(u'%s %s %s\n' % (new_right_id, new_left_id, cost))
    print u'Done!'

    print u'Writing new *.csv...'
    [os.rename(f, f+'.old') for f in lex_file_list]
    for lex_num, lex_file in enumerate(lex_file_list):
        print lex_file
        with codecs.open(lex_file, 'w', 'utf-8') as fout_lex:
            for line in lex_list[lex_num]:
                line[1] = unicode(new_left_id_map[int(line[1])])
                line[2] = unicode(new_right_id_map[int(line[2])])
                fout_lex.write(csv_joinner(line) + u'\n')
    print u'Done!'

    print u'Writing new unk.def...'
    os.rename(unk_def_file, unk_def_file+'.old')
    with codecs.open(unk_def_file, 'w', 'utf-8') as fout_unk:
        for line in unk:
            line[1] = unicode(new_left_id_map[int(line[1])])
            line[2] = unicode(new_right_id_map[int(line[2])])
            fout_unk.write(csv_joinner(line) + u'\n')
    print u'Done!'

    print u'Writing new left-id.def...'
    os.rename(left_id_def_file, left_id_def_file+'.old')
    with codecs.open(left_id_def_file, 'w', 'utf-8') as fout_left:
        for line in left_id_line_list:
            left_id = line[0]
            fields = line[1]
            fout_left.write(u'%s %s\n' % (new_left_id_map[int(left_id)], fields))
    print u'Done!'

    print u'Writing new right-id.def...'
    os.rename(right_id_def_file, right_id_def_file + '.old')
    with codecs.open(right_id_def_file, 'w', 'utf-8') as fout_right:
        for line in right_id_line_list:
            right_id = line[0]
            fields = line[1]
            fout_right.write(u'%s %s\n' % (new_right_id_map[int(right_id)], fields))
    print u'Done!'

    print u''

