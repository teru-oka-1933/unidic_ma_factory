#! /bin/python
# coding: utf-8

import codecs
from toolbox import csv_splitter

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


if __name__ == '__main__':
	
	argvs = sys.argv
	argc = len(argvs)
	if argc != 2:
		print u''
		print u'python ph8_count_suw.py lex.csv'
		print u''
		exit(0)

	lex_csv = argvs[1]	

	surface_set = set()
	lid_list = []
	lemma_id_set =set() 

	with codecs.open(lex_csv, 'r', 'utf-8') as fin:
		for line in fin:
			line = line.rstrip(u'\r\n')
			line = csv_splitter(line)
			
			surface = line[0]
			lemma_id = int(line[-1])
			lid = int(line[-2])
			surface_set.add(surface)
			lemma_id_set.add(lemma_id)
			lid_list.append(lid)

	print u''

	print u'辞書のキーをNFKC正規化したエントリを含む延べ短単位数:'
	print len(lid_list)
	print u''

	print u'辞書のキーをNFKC正規化したエントリを含まない延べ短単位数:'
	print len(set(lid_list))
	print u''

	print u'辞書のキーをNFKC正規化したエントリを含む階層的な見出し語を考慮しない表層系の異なり数:'
	print len(surface_set)
	print u''

	lid_bin_str = format(lid, 'b')
	ones = u''.join(['1' for i in range(30)]) 

	print u'書字形出現形数:'
	print len(set([lid & int('0b' + ones + '111111110000000011111111111111111', 0) for lid in lid_list]))
	print u''

	print u'発音形出現形数:'
	print len(set([lid & int('0b' + ones + '000000001111111111111111111111111', 0) for lid in lid_list]))
	print u''

	print u'語形出現形数:'
	print len(set([lid & int('0b' + ones + '000000000000000011111111111111111', 0) for lid in lid_list]))
	print u''

	print u'書字形基本形数:'
	print len(set([lid & int('0b' + ones + '111111110000000000000000000000000', 0) for lid in lid_list]))
	print u''

	print u'発音形基本形数:'
	print len(set([lid & int('0b' + ones + '000000001111111100000000000000000', 0) for lid in lid_list]))
	print u''

	print u'語形基本形数:'
	print len(set([lid & int('0b' + ones + '000000000000000000000000000000000', 0) for lid in lid_list]))
	print u''

	print u'語彙素数:'
	print len(lemma_id_set)
	print u''


