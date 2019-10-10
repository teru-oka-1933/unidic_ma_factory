#! /bin/python
# coding: utf-8

import codecs
import numpy as np
import os
import shutil


import sys
reload(sys)
sys.setdefaultencoding('utf-8')

np.random.seed(seed=32)


def sampling_test_data(input_corpus, output_dir):

    print u''
    print u'######################################'
    print u'# Sampling Test Data'
    print u'######################################'
    print u''

    print u'Read corpus...',
    sys.stdout.flush()
    corpus_file_list = {}
    with codecs.open(input_corpus, 'r', 'utf-8') as fin:
        for line in fin:
            line = line.rstrip(u'\r\n')
            if line:
                line = line.split(u'\t')
                line_map = {}
                for kv in line:
                    k = kv.split(u':')[0]
                    v = u':'.join(kv.split(u':')[1:])
                    line_map[k] = v

                corpus_name = line_map[u'corpus']
                file_name = line_map[u'file']
                if corpus_name not in corpus_file_list:
                    corpus_file_list[corpus_name] = dict()
                if file_name not in corpus_file_list[corpus_name]:
                    corpus_file_list[corpus_name][file_name] = {u'lemma_bag': dict(), u'form_base_bag': dict(),
                                                                u'form_bag': dict(), u'token_bag': dict(),
                                                                u'goshu_bag': dict()}

                sample = corpus_file_list[corpus_name][file_name]

                token = int(line_map[u'lid'])
                form_base = token >> 33
                lemma = form_base >> 5
                form = unicode(form_base) + u'_' + line_map[u'form']
                goshu = line_map[u'goshu']

                if lemma not in sample[u'lemma_bag']:
                    sample[u'lemma_bag'][lemma] = 0.0
                sample[u'lemma_bag'][lemma] += 1.0

                if form_base not in sample[u'form_base_bag']:
                    sample[u'form_base_bag'][form_base] = 0.0
                sample[u'form_base_bag'][form_base] += 1.0

                if form not in sample[u'form_bag']:
                    sample[u'form_bag'][form] = 0.0
                sample[u'form_bag'][form] += 1.0

                if token not in sample[u'token_bag']:
                    sample[u'token_bag'][token] = 0.0
                sample[u'token_bag'][token] += 1.0

                if goshu not in sample[u'goshu_bag']:
                    sample[u'goshu_bag'][goshu] = 0.0
                sample[u'goshu_bag'][goshu] += 1.0
    print u'Done!'
    print u''

    # 各サンプルの正規化と各コーパスのセントロイドの計算
    print u'Regularized frequency and Calculate centroid...',
    sys.stdout.flush()
    centroid_list = dict()
    for corpus_name in corpus_file_list:
        this_corpus = corpus_file_list[corpus_name]
        if corpus_name not in centroid_list:
            centroid_list[corpus_name] = {u'lemma_bag': dict(), u'form_base_bag': dict(),
                                          u'form_bag': dict(), u'token_bag': dict(),
                                          u'goshu_bag': dict()}
        centroid = centroid_list[corpus_name]
        for file_name in this_corpus:
            sample = this_corpus[file_name]
            for bag_type in sample:
                total_freq_of_this_feature_type = sum([sample[bag_type][f] for f in sample[bag_type]])
                for f in sample[bag_type]:
                    reg_val = sample[bag_type][f] / total_freq_of_this_feature_type
                    sample[bag_type][f] = reg_val
                    # セントロイドもついでに計算（シグマ）
                    if f not in centroid[bag_type]:
                        centroid[bag_type][f] = 0.0
                    centroid[bag_type][f] += reg_val
        for bag_type in centroid:
            for f in centroid[bag_type]:
                centroid[bag_type][f] = centroid[bag_type][f] / float(len(this_corpus) - 1)
    print u'Done!'
    print u''

    print u'Calculate cosine similarity and Sampling test set...',
    sys.stdout.flush()
    test_set = {}
    for corpus_name in corpus_file_list:
        centroid = centroid_list[corpus_name]
        sigma_centroid_beki = 0.0
        for bag_type in centroid:
            for f in centroid[bag_type]:
                sigma_centroid_beki += (centroid[bag_type][f]) ** 2.0
        sample_name_list = []
        sim_list = []
        for file_name in corpus_file_list[corpus_name]:
            sample_name_list.append(file_name)
            this_file = corpus_file_list[corpus_name][file_name]
            sigma_file_beki = 0.0
            sigma_centroid_file = 0.0
            for bag_type in this_file:
                for f in this_file[bag_type]:
                    sigma_file_beki += (this_file[bag_type][f] ** 2.0)
                    sigma_centroid_file += (this_file[bag_type][f] * centroid[bag_type][f])
            cosine_sim = sigma_centroid_file / ((sigma_centroid_beki ** 0.5) * (sigma_file_beki ** 0.5))
            # sim_list.append(cosine_sim + 1.0)  # cosine類似度(cos_sita)の範囲は-1~1だけど，今回負の値は出ないので
            sim_list.append(cosine_sim)
        sum_sim_list = sum(sim_list)
        reg_sim_list = [s/sum_sim_list for s in sim_list]
        test_sample_list = np.random.choice(sample_name_list, int(float(len(sample_name_list)) * 0.1),
                                            replace=False, p=reg_sim_list)
        test_set[corpus_name] = {}
        for file_name in test_sample_list:
            test_set[corpus_name][file_name] = 1
    print u'Done!'
    print u''

    print u'Output...'
    if os.path.exists(output_dir):
        print u''
        print u'already exit', output_dir
        print u'rm -r', output_dir
        shutil.rmtree(output_dir)
    print u''
    print u'mkdir', output_dir
    print u''
    os.mkdir(output_dir)
    fout_test_corpus_list = dict()
    for corpus_name in corpus_file_list:
        fout_test_corpus_list[corpus_name] = codecs.open(
            os.path.join(output_dir, str(corpus_name+u'.test.ntsv')), 'w', 'utf-8')
    fout_test_corpus_list[u'__all__'] = codecs.open(os.path.join(output_dir, 'all.test.ntsv'), 'w', 'utf-8')
    train_set = {}
    with codecs.open(os.path.join(output_dir, 'train.ntsv'), 'w', 'utf-8') as fout_train:
        with codecs.open(input_corpus, 'r', 'utf-8') as fin:
            for line in fin:
                line = line.rstrip(u'\r\n')
                if line:
                    splitted_line = line.split(u'\t')
                    line_map = {}
                    for kv in splitted_line:
                        k = kv.split(u':')[0]
                        v = u':'.join(kv.split(u':')[1:])
                        line_map[k] = v
                    corpus_name = line_map[u'corpus']
                    file_name = line_map[u'file']
                    if file_name in test_set[corpus_name]:
                        fout_test_corpus_list[corpus_name].write(line + u'\n')
                        fout_test_corpus_list[u'__all__'].write(line + u'\n')
                    else:
                        fout_train.write(line + u'\n')
                        if (corpus_name, file_name) not in train_set:
                            train_set[(corpus_name, file_name)] = 1
    for corpus_name in fout_test_corpus_list:
        fout_test_corpus_list[corpus_name].close()
    with codecs.open(os.path.join(output_dir, 'train_list.tsv'), 'w', 'utf-8') as fout_trlst:
        for (corpus_name, file_name) in sorted(train_set.keys()):
            fout_trlst.write(u'%s\t%s\n' % (corpus_name, file_name))
    with codecs.open(os.path.join(output_dir, 'test_list.tsv'), 'w', 'utf-8') as fout_telst:
        for corpus_name in sorted(test_set.keys()):
            for file_name in sorted(test_set[corpus_name].keys()):
                fout_telst.write(u'%s\t%s\n' % (corpus_name, file_name))
    print u'Done!'
    print u''


if __name__ == '__main__':
    argvs = sys.argv
    argc = len(argvs)
    if argc != 3:
        print u''
        print u'python ph0_sampling_test_data.py input_corpus_utf8(.ntsv) output_dir_name'
        print u''
        sys.exit(0)
    sampling_test_data(argvs[1], argvs[2])

