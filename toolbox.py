#! /bin/python
# coding: utf-8

import cStringIO
import csv

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def csv_splitter(csv_line, empty_elem=u''):
    fin = cStringIO.StringIO(str(csv_line))     # バイナリにしないとcsvのnextで怒られる
    splitted_line = csv.reader(fin).next()
    fin.close()
    ret = []
    for elem in splitted_line:
        if elem:
            ret.append(unicode(elem))
        else:
            ret.append(empty_elem)
    return ret


def csv_joinner(listed_line):
    ret = []
    for elem in listed_line:
        elem = elem.replace(u'"', u'""')
        if u',' in elem:
            elem = u'"' + elem + u'"'
        ret.append(elem)
    return u','.join(ret)




