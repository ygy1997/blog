import chardet
from bert_base.client import BertClient
import time
import codecs
import os
import pdb


cont = ''
def tab2(double):
    assert type(double) == list
    return ' ||| '.join(double)

tp = 0
fp = 0
tn = 0
fn = 0
result = []
with BertClient(show_server_config=False, check_version=False, check_length=False, mode='NER') as bc:
    print('>>> enter bertclient')
    start_t = time.perf_counter()
    with codecs.open('/home/ultrastar/BERT-BiLSTM-CRF-NER/glue_dir/NER/test2.txt','r','utf-8') as f:
        for line in f.readlines():

            cols = line.split('\t')
            cont+=cols[0]
            if not '\t' in line:
                rst = bc.encode([cont])
                rst = rst[0]
                for rsti,char in zip(rst,cont):
                    if rsti == 'O':
                        continue
                    print("%s/%s "%(char,rsti))
                cont = ''
                pdb.set_trace()

#with codecs.open('tmp.txt','w+','utf-8') as g:
#    for resu in result:
#        g.write(resu+'\r\n')

#print('>>> time used:{}'.format(time.perf_counter() - start_t))

