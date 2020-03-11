import chardet
from bert_base.client import BertClient
import time
import codecs
import pdb
import os
import pdb


def tab2(double):
    assert type(double) == list
    return '\t'.join(double)

tp = 0
fp = 0
tn = 0
fn = 0
result = []
with BertClient(show_server_config=False, check_version=False, check_length=False, mode='CLASS') as bc:
    print('>>> enter bertclient')
    start_t = time.perf_counter()
    with codecs.open('/home/ultrastar/BERT-BiLSTM-CRF-NER/glue_dir/MNLI/mnli_test_shuf.tsv','r','utf-8') as f:
        for line in f.readlines():
            cols = line.split('\t')
            #print(cols)
            #cont = tab2([cols[0],cols[1]])
            #if cols[1] == '其他':
            #    continue
            #rst = bc.encode([cont])
            #print(line)
            if len(line)>600:
                continue

            rst = bc.encode([tab2(cols[:2])])
            #print(rst)
            rst = rst[0]['pred_label'][0]
            #print(rst)
            cols[2] = cols[2].strip()
            label = int(cols[2])
            rst = int(rst)
            if label == 1 and  rst == 1:
                tp+=1
            elif label == 0 and  rst == 0:
                tn+=1
            elif label == 0 and  rst == 1:
                #print('>>> label:', cols[2])
                #print('>>> pred:', rst)
                print(line)
                fp+=1
                #pdb.set_trace()
                #pdb.set_trace()
                #result.append(line)
            elif label == 1 and  rst == 0:
                fn+=1
                print(line)
                #print(">>> line:", line)
                #print('>>> label:', cols[2])
                #print('>>> pred:', rst)
                #pdb.set_trace()
                #result.append(line)
            else:
                pdb.set_trace()
                #print('u r kidding?')
            #print(line)
            #print(len(line))
            print("tp, fp, tn, fn")
            print(tp, fp, tn, fn)
            result.append([cols[:2],label,rst])

with codecs.open('tmp.txt','w+','utf-8') as g:
    for resu in result:
        g.write(','.join(resu)+'\r\n')

print('>>> time used:{}'.format(time.perf_counter() - start_t))

