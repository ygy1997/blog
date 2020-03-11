#!encoding=utf-8
#================================================================
#   Copyright (C) 2019 UltraPower Ltd. All rights reserved.
#   file: discover.py
#   mail: qinhaining@ultrapower.com.cn
#   date: 2019-05-13
#   describe:
#================================================================

import numpy
from collections import defaultdict
import numpy as np
import json
import re
import sys
from functools import reduce
import pickle
import time
from tqdm import tqdm

import logging
import logging.handlers
import datetime
from .mywrapper import log
__all__ = ["log"]


'''
logger = logging.getLogger('mylogger')
logger.setLevel(logging.DEBUG)

rf_handler = logging.handlers.TimedRotatingFileHandler('all.log', when='midnight', interval=1, backupCount=7, atTime=datetime.time(0, 0, 0, 0))
rf_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

f_handler = logging.FileHandler('error.log')
f_handler.setLevel(logging.ERROR)
f_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(filename)s[:%(lineno)d] - %(message)s"))

logger.addHandler(rf_handler)
logger.addHandler(f_handler)

logger.info('jieba-calcu instance')

logger.debug('debug message')
logger.warning('warning message')
logger.error('error message')
logger.critical('critical message')
'''

# 输入文档 输出文档
#inf = sys.argv[1]
#outf = sys.argv[2]

MIN_INT = 0
MIN_FLOAT = -3.14e100
MIN_INF = float("-inf")

'''
def gen():
    lines = open(inf,'r').readlines()
    #lines = open('/home/siy/data/广电全量地址_weak.csv','r').readlines()
    np.random.shuffle(lines)
    for line in lines:
        line.strip()
        if len(line) == 0:
            continue
        yield line

texts = gen
'''

class WordDiscovery(object):
    def __init__(self, paray=1.2, gen=None):
        import copy
        self.gen = list(gen)
        self.n = 6
        self.min_count = 5
        self.ngrams = defaultdict(int)
        self.min_proba = {}
        self.base_count = 1.0
        paray = max(1, paray)
        for i in range(2, self.n+1):
            self.min_proba[i] = (self.base_count*(paray*i-1)) * (paray ** (i-1))
        #print(">> para of filter:", self.min_proba)
        #self.min_proba = {2:self.min_count*2, 3:self.min_count, 4:self.min_count, 5:self.min_count, 6:self.min_count}
        #self.min_proba = {2:5, 3:10, 4:15, 5:25, 6:40}


    def word_discovery(self):
      with tqdm(total=200) as pbar:
        time.sleep(0.01)
        pbar.update(160)
            
        for t in self.gen:
            for i in range(len(t)):
                for j in range(1, self.n+1):
                   if i+j <= len(t):
                        self.ngrams[t[i:i+j]] += 1
        self.ngrams = {i:j for i,j in self.ngrams.items() if j >= self.min_count}
        total = 1.*sum([j for i,j in self.ngrams.items() if len(i) == 1])

        # 计算凝固度
        def is_keep(s, min_proba):
            if len(s) >= 2:
                score = min([total*self.ngrams[s]/(self.ngrams[s[:i+1]]*self.ngrams[s[i+1:]]) for i in range(len(s)-1)])
                if score > min_proba[len(s)]:
                    return True
            else:
                return False

        self.ngrams_ = set(i for i,j in self.ngrams.items() if is_keep(i, self.min_proba))
        #print("self.ngrms_", self.ngrams_)

        def cut(s):
            r = np.array([0]*(len(s)-1))
            for i in range(len(s)-1):
                for j in range(2, self.n+1):
                    if s[i:i+j] in self.ngrams_:
                        r[i:i+j-1] += 1
            w = [s[0]]
            for i in range(1, len(s)):
                if r[i-1] > 0:
                    w[-1] += s[i]
                else:
                    w.append(s[i])
            return combine(w)

        def combine(w):
            res = []
            res.append(w[0])
            for c in w[1:]:
                if len(c) == 1:
                    res[-1]+=c
                else:
                    res.append(c)
            # print(res)
            # print([item[::-1] for item in res[::-1]])
            return [item for item in res[::-1]]

        words = defaultdict(int)
        for t in self.gen:
            for i in cut(t):
                i.strip()
                i = re.sub("[\r\n]", "", i)
                words[i] += 1

        
        #print("words", words)
        words = {i:j for i,j in words.items() if j >= self.min_count}
        #print("words", words)
        
        def is_real(s):
            if len(s) >= 3:
                for i in range(3, self.n+1):
                    for j in range(len(s)-i+1):
                        if s[j:j+i] not in self.ngrams_:
                            return False
                return True
            elif len(re.sub("[^a-zA-Z0-9\u4e00-\u9fa5]","",s))>1:
                return True
            else:
                return False
        w = {i:j for i,j in words.items() if is_real(i)}
        #_ = self.viterbi_data_prepare()
        pbar.update(200)
        return w

    def viterbi_data_prepare(self):
        import pdb
        self.states= {}
        self.emit_prob_bies = {}
        self.emit_prob = {}
        self.tran_prob = {}
        for i in ['B','I','E','S']:
            self.emit_prob_bies[(i,'n')] = MIN_INT
            self.emit_prob[(i,'n')] = {}
            self.tran_prob[(i,'n')] = {}

        for k in self.ngrams:
            assert self.ngrams[k] > 0
            lenth_k = len(k)
            if lenth_k == 1:
                val = self.emit_prob.get(('S','n'), {})
                val_char = val.get(k, MIN_INT)
                val_char += self.ngrams[k]
                self.emit_prob[('S','n')] = {k: val_char}

                val = self.emit_prob_bies.get(('S','n'), MIN_INT)
                self.emit_prob_bies[('S','n')] = val + self.ngrams[k]
                if not self.states.get(k, None):
                    self.states[k] = (('B','n'),('I','n'),('E','n'),('S','n'))

            elif lenth_k == 2:
                val = self.emit_prob.get(('B','n'), {}).get(k[0], MIN_INT)
                self.emit_prob[('B','n')][k[0]] = val + self.ngrams[k]

                val = self.emit_prob.get(('E','n'), {}).get(k[1], MIN_INT)
                self.emit_prob[('E','n')][k[1]] = val + self.ngrams[k]

                val = self.emit_prob_bies.get(('B','n'), MIN_INT)
                self.emit_prob_bies[('B','n')] = val + self.ngrams[k]

                val = self.emit_prob_bies.get(('E','n'), MIN_INT)
                self.emit_prob_bies[('E','n')] = val + self.ngrams[k]

                val = self.tran_prob.get(('B','n'), {}).get(('E','n'), MIN_INT)
                self.tran_prob[('B', 'n')][('E', 'n')] = val + self.ngrams[k]

                val = self.tran_prob.get(('E','n'), {}).get(('B','n'), MIN_INT)
                self.tran_prob[('E', 'n')][('B', 'n')] = val + self.ngrams[k]

                if not self.states.get(k[0], None):
                    self.states[k[0]] = (('B','n'),('I','n'),('E','n'),('S','n'))

                if not self.states.get(k[1], None):
                    self.states[k[1]] = (('B','n'),('I','n'),('E','n'),('S','n'))

            elif lenth_k > 2:
                val = self.emit_prob.get(('B','n'), {}).get(k[0], MIN_INT)
                self.emit_prob[('B','n')][k[0]] = val + self.ngrams[k]

                if not self.states.get(k[0], None):
                    self.states[k[0]] = (('B','n'),('I','n'),('E','n'),('S','n'))

                if not self.states.get(k[-1], None):
                    self.states[k[-1]] = (('B','n'),('I','n'),('E','n'),('S','n'))

                for c in k[1:-1]:
                    val_char += self.ngrams[c]
                    self.emit_prob[('I','n')][c] = self.emit_prob.get(('I','n'), {}).get(c, MIN_INT) + self.ngrams[c]

                    if not self.states.get(c, None):
                        self.states[c] = (('B','n'),('I','n'),('E','n'),('S','n'))

                val = self.emit_prob.get(('E','n'), {}).get(k[-1], MIN_INT)
                self.emit_prob[('E','n')][k[-1]] = val + self.ngrams[k]

                val = self.tran_prob.get(('B','n'), {}).get(('I','n'), MIN_INT)
                self.tran_prob[('B', 'n')][('I', 'n')] = val + self.ngrams[k]

                val = self.tran_prob.get(('I','n'), {}).get(('E','n'), MIN_INT)
                self.tran_prob[('I', 'n')][('E', 'n')] = val + self.ngrams[k]

                val = self.tran_prob.get(('E','n'), {}).get(('B','n'), MIN_INT)
                self.tran_prob[('E', 'n')][('B', 'n')] = val + self.ngrams[k]

                val = self.tran_prob.get(('I','n'), {}).get(('I','n'), MIN_INT)
                #self.tran_prob[('I', 'n')][('I', 'n')] = val + (enth_k-2)*self.ngrams[k]
                self.tran_prob[('I', 'n')][('I', 'n')] = val + self.ngrams[k] * (lenth_k-2)

                val = self.emit_prob_bies.get(('B','n'), MIN_INT)
                self.emit_prob_bies[('B','n')] = val + self.ngrams[k]

                #val = self.emit_prob_bies.get(('E','n'), MIN_INT)
                #self.emit_prob_bies[('E','n')] = val + self.ngrams[k] * (lenth_k-1)

                #val = self.emit_prob_bies.get(('I','n'), MIN_INT)
                #self.emit_prob_bies[('I','n')] = val + (lenth_k-2) * self.ngrams[k]

            else:
                import pdb
                pdb.set_trace()

        #import pdb
        #pdb.set_trace()
        def log_val(dct):

            def lnxy(y, x=10):
                '''
                x: Logarithmic base
                y: Logarithmic real number
                '''
                y = float(y)
                print(y,x)
                return np.log2(y+3)/np.log2(x+3)

            '''
            total = 0
            for k in dct:
                if type(dct[k]) in [int]:
                    total+=dct[k]
                else:
                    for j in dct[k]:
                        if type(dct[k][j]) in [int]:
                            total+=dct[k][j]
            total = total//1000
            '''

            _dct = {}
            for k in dct:
                if type(dct[k]) in [dict]:
                    for j in dct[k]:
                        _dct[k] = dct.get(k, {})
                        import pdb
                        if type(dct[k][j]) in [int]:
                            assert dct[k][j] > 0
                            if type(j) == str:
                                _dct[k][j] = lnxy(dct[k][j])
                            else:
                                _dct[k][j] = lnxy(dct[k][j])
                        else:
                            import pdb
                            pdb.set_trace()
                elif type(dct[k]) in [int]:
                    try:
                        assert dct[k] > 0
                    except:
                        print(dct[k])
                    _dct[k] = lnxy(dct[k])
                elif type(dct[k]) in [tuple]:
                    _dct[k] = dct[k]
                else:
                    import pdb
                    pdb.set_trace()
            return _dct

        def pickle_save(lst):    
            cont = open("./localdata.pkl","wb")
            for item in lst:
                pickle.dump(item, cont)
        
        lst = [log_val(self.tran_prob), log_val(self.emit_prob), log_val(self.emit_prob_bies), self.states]
        pickle_save(lst)
        return lst
