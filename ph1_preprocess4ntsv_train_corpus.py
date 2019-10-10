#! /bin/python
# coding: utf-8

####################################################
# 日常会話コーパスに出て来る厄介な平仮名の名前が入った文を削除
####################################################

import codecs
import unicodedata as ud

import sys
reload(sys)
sys.setdefaultencoding('utf-8')



# 2文字のひらがな名はすべて削除
def is_two_hira_name(field_map):
    if field_map[u'pos3'] == u'人名':
        if len(field_map[u'orth']) == 2:
            if ('HIRAGANA' in ud.name(field_map[u'orth'][0])) and ('HIRAGANA' in ud.name(field_map[u'orth'][1])):
                return True
    return False


def main(input_file, output_file):

    # コーパスの読み込み
    sentence_list = []
    with codecs.open(input_file, 'r', 'utf-8') as fin:
        sentence = []
        for line in fin:
            line = line.lstrip(u'\ufeff')
            line = line.rstrip(u'\r\n')
            # 1行を辞書化
            if line:
                line = line.split(u'\t')
                field_map = {u'pos1': u'*', u'pos2': u'*', u'pos3': u'*', u'pos4': u'*'}
                for field in line:
                    f_name = field.split(u':')[0].strip()
                    f_val = u':'.join(field.split(u':')[1:])  # .strip(u' ') # 全角スペース消されないように
                    if f_name == u'pos':
                        pos1_4 = f_val.split(u'-')
                        for (i, val) in enumerate(pos1_4):
                            field_map[u'pos' + unicode(i + 1)] = val
                    else:
                        field_map[f_name] = f_val
                if field_map[u'boundary'] == u'B':
                    if sentence:
                        sentence_list.append(sentence)
                        sentence = []
                sentence.append(field_map)
        if sentence:
            sentence_list.append(sentence)

    # 書き出し
    full_corpus = 0
    removed_name = 0
    removed_defre = 0
    with codecs.open(output_file, 'w', 'utf-8') as fout:
        for sentence in sentence_list:
            write_flag = True
	    full_corpus += 1
            for fm in sentence:
                # 当該文を書き出すか否か
                if is_two_hira_name(fm):
                    write_flag = False
                    removed_name += 1
		    break
                # デフレスパイラル削除
                if fm[u'orth'] in [u'デフレスパイラル', u'インフレリスク',
                                                  u'アルミサッシ', u'アルミホイル', u'アルミパネル', u'アルミチューブ']:
                    write_flag = False
		    removed_defre += 1
		    break
            if write_flag:
                for fm in sentence:
                    output_line = []
                    for k, v in fm.iteritems():
                        output_line.append(k + u':' + v)
                    fout.write(u'\t'.join(output_line) + u'\n')
    print u'コーパスフルサイズ', full_corpus, u'文'
    print u'削除した名前文数', removed_name, u'文'
    print u'削除したデフレ文数', removed_defre, u'文'


if __name__ == '__main__':

    argvs = sys.argv
    argc = len(argvs)

    if argc != 3:

        print ''
        print 'python remove_hiragana_name_from_ntsv_corpus.py inputfile(ntsv_corpus) outputfile(ntsv_corpus)'
        print ''

    else:

        main(argvs[1], argvs[2])


