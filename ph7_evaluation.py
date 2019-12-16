#! /bin/python
# coding: utf-8

import argparse
import codecs
import os
import shutil
import subprocess

import ph4_train_dic as train_dic

import remove_shallow_unk_from_lex
import remove_deep_unk_from_lex
import remove_middle_unk_from_lex

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def main(mecab_exe, subcommand_dir, java_path, java_cp, src_seed_dir, eval_work_dir,
         train_corpus_file, test_corpus_file, src_lex_file, output_model_name, lid_field_num,
         init_model_file=None, c=1.0, p=1, f=1):

    ###############################################
    # Work用のディレクトリを用意
    ###############################################
    print u''
    eval_work_dir = eval_work_dir.rstrip(u'/')
    if os.path.isdir(eval_work_dir):
        print eval_work_dir, u'is existing.'
        print u'remove', eval_work_dir
        shutil.rmtree(eval_work_dir)

    print u'make', eval_work_dir
    os.mkdir(eval_work_dir)

    all_lex_work_dir = os.path.join(eval_work_dir, 'all_lex')
    print u'make', all_lex_work_dir
    os.mkdir(all_lex_work_dir)
    all_seed_dir = os.path.join(all_lex_work_dir, 'seed')
    print u''

    shallow_unk_work_dir = os.path.join(eval_work_dir, 'shallow_unk')
    print u'make', shallow_unk_work_dir
    os.mkdir(shallow_unk_work_dir)
    shallow_seed_dir = os.path.join(shallow_unk_work_dir, 'seed')
    print u''

    middle_unk_work_dir = os.path.join(eval_work_dir, 'middle_unk')
    print u'make', middle_unk_work_dir
    os.mkdir(middle_unk_work_dir)
    middle_seed_dir = os.path.join(middle_unk_work_dir, 'seed')
    print u''

    deep_unk_work_dir = os.path.join(eval_work_dir, 'deep_unk')
    print u'make', deep_unk_work_dir
    os.mkdir(deep_unk_work_dir)
    deep_seed_dir = os.path.join(deep_unk_work_dir, 'seed')
    print u''

    ###############################################
    # lexを準備
    ###############################################
    print u'======== Make unk_lex ========='
    print u'copy', src_lex_file, u'->', eval_work_dir
    shutil.copy(src_lex_file, eval_work_dir)
    all_lex_file = os.path.join(eval_work_dir, os.path.basename(src_lex_file))
    shallow_unk_lex_file = os.path.join(eval_work_dir, 'shallow_unk_lex.csv')
    middle_unk_lex_file = os.path.join(eval_work_dir, 'middle_unk_lex.csv')
    deep_unk_lex_file = os.path.join(eval_work_dir, 'deep_unk_lex.csv')
    print u''
    print u'remove_shallow_unk_from_lex.py'
    remove_shallow_unk_from_lex.main(train_corpus_file, test_corpus_file, all_lex_file, shallow_unk_lex_file,
                                     os.path.join(src_seed_dir, 'dicrc'))
    print u''
    print u'remove_middle_unk_from_lex.py'
    remove_middle_unk_from_lex.main(train_corpus_file, test_corpus_file, all_lex_file, middle_unk_lex_file,
                                  os.path.join(src_seed_dir, 'dicrc'), lid_field_num)
    print u''
    print u'remove_deep_unk_from_lex.py'
    remove_deep_unk_from_lex.main(train_corpus_file, test_corpus_file, all_lex_file, deep_unk_lex_file,
                                  os.path.join(src_seed_dir, 'dicrc'), lid_field_num)
    print u''

    ###############################################
    # ３パターンの学習
    ###############################################

    print u'======== TRAIN ALL LEX ========='
    all_final_dir = os.path.join(all_lex_work_dir, 'final')
    train_dic.main(subcommand_dir, src_seed_dir, all_seed_dir, all_final_dir, train_corpus_file, all_lex_file,
                   output_model_name,
                   init_model_file=init_model_file, c=c, p=p, f=f)

    print u'======== TRAIN SHALLOW UNK ========='
    shallow_final_dir = os.path.join(shallow_unk_work_dir, 'final')
    train_dic.main(subcommand_dir, src_seed_dir, shallow_seed_dir, shallow_final_dir,
                   train_corpus_file, shallow_unk_lex_file,
                   output_model_name,
                   init_model_file=init_model_file, c=c, p=p, f=f)

    print u'======== TRAIN MIDDLE UNK ========='
    middle_final_dir = os.path.join(middle_unk_work_dir, 'final')
    train_dic.main(subcommand_dir, src_seed_dir, middle_seed_dir, middle_final_dir,
                   train_corpus_file, middle_unk_lex_file,
                   output_model_name,
                   init_model_file=init_model_file, c=c, p=p, f=f)

    print u'======== TRAIN DEEP UNK ========='
    deep_final_dir = os.path.join(deep_unk_work_dir, 'final')
    train_dic.main(subcommand_dir, src_seed_dir, deep_seed_dir, deep_final_dir,
                   train_corpus_file, deep_unk_lex_file,
                   output_model_name,
                   init_model_file=init_model_file, c=c, p=p, f=f)

    ###############################################
    # mecab実行
    ###############################################
    print u'======== Eval ========='
    for work_dir in [all_lex_work_dir, shallow_unk_work_dir, middle_unk_work_dir, deep_unk_work_dir]:
        print work_dir
        # 平文化
        flat_text = os.path.join(work_dir, 'flat_test.txt')
        meval_base = [java_path, '-cp', java_cp]
        meval_flat = meval_base + ['meval.Flat', '-i', test_corpus_file, '-o', flat_text]
        print unicode(' '.join(meval_flat))
        subprocess.call(meval_flat)
        # mecab
        pred_file = os.path.join(work_dir, 'pred.mecab')
        mecab_command = [mecab_exe, '-d', os.path.join(work_dir, 'final'),
                         '-o', pred_file, flat_text]
        print unicode(' '.join(mecab_command))
        subprocess.call(mecab_command)
        # スコアラー
        meval_scorer_file = os.path.join(work_dir, 'scorer.meval')
        meval_scorer = meval_base + ['meval.Scorer', '-g', test_corpus_file, '-p', pred_file,
                                     '-f', '"1+2+3+4+5+6,7+8,10"']
        print unicode(' '.join(meval_scorer))
        p = subprocess.Popen(meval_scorer, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdoutdata, stderrdata) = p.communicate()
        scorer_output = unicode(stdoutdata)
        with codecs.open(meval_scorer_file, 'w', 'utf-8') as fout:
            fout.write(scorer_output)
            print scorer_output


if __name__ == '__main__':

    ###############################################
    # 引数のパース
    ###############################################

    parser = argparse.ArgumentParser(description='Usage: ph7_evaluation --mecab_exe MECAB_EXE --subcommand DIR --java_path JAVA_EXE --java_cp CP_LINE --src_seed_dir DIR --eval_work_dir DIR --train_corpus_file MECAB_FILE --test_corpus_file MECAB_FILE --output_model_name NAME --lid LID_COL_NUM --lex_file CSV_FILE [-c VALUE] [-p VALUE] [-f VALUE] [-M INIT_MODEL_FILE]')

    parser.add_argument('--mecab_exe', type=str, required=True, help="mecab.exe")
    parser.add_argument('--subcommand_dir', type=str, required=True,
                        help="mecab's sub command (e.g., mecab-dict-index) directory (e.g., mecab-0.xx/libexec/mecab)")
    parser.add_argument('--java_path', type=str, required=True, help="java command for running MevAL")
    parser.add_argument('--java_cp', type=str, required=True, help="Class path arg on the case for runnning MevAL including MevAL w/o -cp")
    parser.add_argument('--src_seed_dir', type=str, required=True, help='Seed dic directory')
    parser.add_argument('--eval_work_dir', type=str, required=True, help='Eval directory')
    parser.add_argument('--train_corpus_file', type=str, required=True, help='Train corpus (.mecab)')
    parser.add_argument('--test_corpus_file', type=str, required=True, help='Test corpus (.mecab)')
    parser.add_argument('--src_lex_file', type=str, required=True, help='Src lex file (.csv)')
    parser.add_argument('--output_model_name', type=str, required=True, help='"NAME" of output model file (NOT PATH)')
    parser.add_argument('--lid', type=int, default=None, required=True, help='lemma_id field num (pos1 = [1])')
    parser.add_argument('-M', '--init_model_file', type=str, default=None,
                        help='CRF initial model file which already trained')
    parser.add_argument('-c', type=float, default=1.0, help='mecab-cost-train parameter')
    parser.add_argument('-p', type=int, default=1, help='mecab-cost-train parameter')
    parser.add_argument('-f', type=int, default=1, help='mecab-cost-train parameter')

    args = parser.parse_args()

    main(args.mecab_exe, args.subcommand_dir, args.java_path, args.java_cp,
         args.src_seed_dir, args.eval_work_dir,
         args.train_corpus_file, args.test_corpus_file, args.src_lex_file, args.output_model_name,
         args.lid,
         init_model_file=args.init_model_file, c=args.c, p=args.p, f=args.f)

