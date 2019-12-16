#! /bin/python
# coding: utf-8

import argparse
import subprocess
import os
import shutil

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def main(subcommand_dir, src_seed_dir, seed_dir, final_dir, corpus_file, lex_file, output_model_name,
         init_model_file=None, c=1.0, p=1, f=1):

    subcommand_dir = subcommand_dir.rstrip(u'/')
    src_seed_dir = src_seed_dir.rstrip(u'/')
    seed_dir = seed_dir.rstrip(u'/')
    final_dir = final_dir.rstrip(u'/')

    ###############################################
    # 引数の確認
    ###############################################
    final_dir = final_dir.rstrip(u'/')
    print u''
    print u'===== MeCab Learning Script ====='
    print u'MeCab Parameter'
    print u'  libexec: %s' % subcommand_dir
    print u'----------------------------'
    print u'Learning Dir and File'
    print u'  src_seed: %s' % src_seed_dir
    print u'  seed:     %s' % seed_dir
    print u'  final:    %s' % final_dir
    print u'  corpus:   %s' % corpus_file
    print u'  lex:      %s' % lex_file
    print u'----------------------------'
    print u'MeCab Learning Parameter'
    print u'  M = %s' % init_model_file
    print u'  c = %s' % c
    print u'  p = %s' % p
    print u'  f = %s' % f
    print u'  Output Model: %s' % os.path.join(seed_dir, output_model_name)
    print u'----------------------------'
    print u''

    ###############################################
    # MeCabの学習
    ###############################################

    # seedは何回も実験で使いたいし，上書きしたくないので
    if os.path.isdir(seed_dir):
        print seed_dir, u'is existing.'
        print u'remove', seed_dir
        shutil.rmtree(seed_dir)
    print u'make', seed_dir
    print u'copy', src_seed_dir, u'->', seed_dir
    shutil.copytree(src_seed_dir, seed_dir)
    print u''

    print u'lex file copying to seed ...'
    shutil.copy(lex_file, seed_dir)
    print u''

    # if init_model_file is not None:
    #     print u'initial model file copying to seed ...'
    #     shutil.copy(init_model_file, seed_dir)
    #     print u''

    print u'===== mecab-dict-index ====='
    first_dict_index = [os.path.join(subcommand_dir, 'mecab-dict-index'), '-d', seed_dir, '-o', seed_dir]
    print unicode(' '.join(first_dict_index))
    print u'----------------------------'
    subprocess.call(first_dict_index)
    print u''

    print u'===== mecab-cost-train ====='
    cost_train = [os.path.join(subcommand_dir, 'mecab-cost-train'),
                  '-d', seed_dir,
		  '-c', str(c), '-f', str(f), '-p', str(p)]
    if init_model_file is not None:
        cost_train += ['-M', init_model_file]
    cost_train += [corpus_file, os.path.join(seed_dir, output_model_name)]
    print unicode(' '.join(cost_train))
    print u'----------------------------'
    subprocess.call(cost_train)
    print u''

    if os.path.isdir(final_dir):
        print final_dir, u'is existing.'
    else:
        print u'making %s ...' % final_dir
        os.mkdir(final_dir)
    print u''

    print u'===== mecab-dict-gen ====='
    dict_gen = [os.path.join(subcommand_dir, 'mecab-dict-gen'), '-d', seed_dir, '-o', final_dir,
                '-m', os.path.join(seed_dir, output_model_name)]
    print unicode(' '.join(dict_gen))
    print u'----------------------------'
    subprocess.call(dict_gen)
    print u''

    print u'===== mecab-dict-index ====='
    second_dict_index = [os.path.join(subcommand_dir, 'mecab-dict-index'), '-d', final_dir, '-o', final_dir]
    print unicode(' '.join(second_dict_index))
    print u'----------------------------'
    subprocess.call(second_dict_index)
    print u''


if __name__ == '__main__':

    ###############################################
    # 引数のパース
    ###############################################

    parser = argparse.ArgumentParser(description='Usage: mecab_learning --subcommand DIR --src_seed_dir DIR --seed_dir DIR --final_dir DIR --corpus_file MECAB_FILE --lex_file CSV_FILE --output_model_name NAME [-c VALUE] [-p VALUE] [-f VALUE] [-M INIT_MODEL_FILE]')

    parser.add_argument('--subcommand_dir', type=str, required=True,
                        help="mecab's sub command (e.g., mecab-dict-index) directory (e.g., mecab-0.xx/libexec/mecab)")
    parser.add_argument('--src_seed_dir', type=str, required=True, help="Src seed directory (Don't over write)")
    parser.add_argument('--seed_dir', type=str, required=True, help='New seed dic directory (!= src_seed_dir)')
    parser.add_argument('--final_dir', type=str, required=True, help='Final dic directory (!= src_/seed_dir)')
    parser.add_argument('--corpus_file', type=str, required=True, help='Train corpus (.mecab)')
    parser.add_argument('--lex_file', type=str, required=True, help='Lex file (.csv)')
    parser.add_argument('--output_model_name', type=str, required=True, help='"NAME" of output model file (NOT PATH)')
    parser.add_argument('-M', '--init_model_file', type=str, default=None, help='CRF initial model file which already trained')
    parser.add_argument('-c', type=float, default=1.0, help='mecab-cost-train parameter')
    parser.add_argument('-p', type=int, default=1, help='mecab-cost-train parameter')
    parser.add_argument('-f', type=int, default=1, help='mecab-cost-train parameter')

    args = parser.parse_args()

    main(args.subcommand_dir, args.src_seed_dir, args.seed_dir, args.final_dir, args.corpus_file, args.lex_file,
         args.output_model_name, init_model_file=args.init_model_file, c=args.c, p=args.p, f=args.f)


