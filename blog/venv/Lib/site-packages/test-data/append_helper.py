import sys
from multiprocessing import Process
sys.path.append("/app/rsync_client/BERT=BiLSTM-CRF-NER")
#sys.path.append("/home/ultrastar/BERT=BiLSTM-CRF-NER")
from bert_base.client import BertClient
from flask import request
import re
import collections
import json
import collections
from collections import deque
from collections import defaultdict
import codecs
import pdb
import pandas as pd
import jieba
import xlrd

#jieba.load_userdict("./glue_dir/userdict.txt")

#bc_ner = BertClient(port=5557,port_out=5558,mode="NER")
bc_ner_max = BertClient(port=5559,port_out=5560,mode="NER")
print("connect bert server ok")
#bc_mnli = BertClient(mode="CLASS")


def clr(sin):
    sin = re.sub("B-","",sin)
    sin = re.sub("I-","",sin)
    return sin

def jieba_complete(sentence, mypreds):
    preds = mypreds["ner"]
    index = 0
    endindex = 0
    for word in jieba.cut(sentence):
        endindex = index+len(word)
        for pred in preds:
            pred = list(pred)
            if int(pred[2])>index and int(pred[2])<endindex:
                preds.append((pred[0], pred[1], endindex))
                preds.remove(tuple(pred))
            elif int(pred[1])>index and int(pred[1])<endindex:
                preds.append((pred[0], index, pred[2]))
                preds.remove(tuple(pred))
            else:
                pass
        index = endindex
    mypreds["ner"] = preds
    return mypreds
                
def cnt_word_max(preds):
    '''
    convert pred (k,v) to (content, [(pred, indexs, indexe)])
    '''
    last_pred = "O"
    mod_preds = {}
    mod_preds["cont"]=""
    mod_preds["ner"]=[]
    start = -1
    end = -1
    buf = []
    for idx, pred in enumerate(preds):
        k = pred[0]
        mod_preds["cont"]+=k
        v = pred[1]
        if last_pred == "O":
            if v[0] in ["B","I"]:
                start = idx
                last_pred = v[0]
                buf.append(v)
            else:# v == "O":
                last_pred = v[0]
        else:
            if v[0] in ["B","I"]:
                last_pred = v[0]
                buf.append(v)
                pass
            else:# k == "O":
                #buf.append(v)
                end = idx
                if end-start>1 and start>-1:
                     count=collections.Counter(buf)
                     bestv = sorted(count.items(),key=lambda x:x[1],reverse=True)[0][0]
                     mod_preds["ner"].append((bestv,start,end))
                     pass  # print(bestv, sentence[start:end])
                buf = []
                start = -1
                end = -1
                last_pred = "O"
    return mod_preds

def cnt_max(char, alst):
    count=collections.Counter(alst)
    res = sorted(count.items(),key=lambda x:x[1],reverse=True)
    pass  # print(">%s:"%char, res)
    #for i in res:
    #    if i[0]=='O':
    #        continue
    #    else:
    #        return i[0]
    return res[0][0]

def combine(left, right):
    #print(left)
    #print(right)
    '''
    there two ner model here to mark the sentence
    compare them to pick the fscore
    in:left the base model
    in:right the logic model
    out:word_labels [['嫌疑人',0,3]...]
    '''
    assert len(left) == len(right)
    many_sent_lbs = []
    try:
        assert len(left) == len(right)
    except:
        #print(len(left), len(right))
        raise Exception(">>> 句子数目应当等长")
    for lfts,rits in zip(left,right):
        #mll = min(len(rits),len(lfts))
        #rits = rits[:mll] 
        #lfts = lfts[:mll] 
        try:
            assert len(lfts) == len(rits)
        except:
            #print(len(lfts), len(rits))
            raise Exception(">>> 字符数应当等长")
        sent_lbs = [['X',-1,-1]]
        sent_lbs_max = []
        right_label_lst = []
        index = -1
        left_last_one = "O"
        right_last_one = "O"
        for lft,rit in zip(lfts,rits):
            lft = clr(lft)
            rit = clr(rit)
            right_label_lst.append(rit)
            if rit == right_last_one\
                or lft == left_last_one:
                sent_lbs[-1][2]=index
            else:
                max_lb = cnt_max(right_label_lst)
                sent_lbs[-1][0]=max_lb
                sent_lbs[-1][2]=index
                sent_lbs.append([lft, index, index])
                right_label_lst = []
            left_last_one = lft
            index+=1
        #print(index)
        many_sent_lbs.append(sent_lbs)
    return many_sent_lbs


def prt_lst(llst,rlst):
    res = ''
    for i,j in zip(llst,rlst):
        res+="%s/%s "%(i,j)
    return res

    data = request.get_data()
    json_data = json.loads(data.decode("utf-8"))
    sentence = json_data.get("content")

# -*- coding: cp936 -*-
def strQ2B(ustring):
    """全角转半角"""
    rstring = ""
    for uchar in ustring:
        inside_code=ord(uchar)
        if inside_code == 12288:                              #全角空格直接转换            
            inside_code = 32 
        elif (inside_code >= 65281 and inside_code <= 65374): #全角字符（除空格）根据关系转化
            inside_code -= 65248

        rstring += chr(inside_code)
    return rstring
    
def strB2Q(ustring):
    """半角转全角"""
    rstring = ""
    for uchar in ustring:
        inside_code=ord(uchar)
        if inside_code == 32:                                 #半角空格直接转化                  
            inside_code = 12288
        elif inside_code >= 32 and inside_code <= 126:        #半角字符（除空格）根据关系转化
            inside_code += 65248

        rstring += chr(inside_code)
    return rstring


'''

b = strQ2B("ｍｎ123abc博客园".decode('cp936'))                           
print b

c = strB2Q("ｍｎ123abc博客园".decode('cp936'))                           
print c
'''

def gen(filepath="./mnli_dev_shuf.tsv"):
    lines = codecs.open(filepath,"r","utf-8").readlines()
    for line in lines:
        line = line.split("\t")[0]
        line.strip()
        line = re.sub("\r","",line)
        line = re.sub("\n","",line)
        line = re.sub("\t","",line)
        line = re.sub(" ","",line)
        line = strQ2B(line)
        #line = re.sub("[^\u4e00-\u9fa50-9a-zA-Z]",",",line)
        yield line
        #yield [list(line), ["O"]*len(line)]


def get_ner_block(sentence, ner="ner", maxlen=50):
    append_lst = []
    if len(sentence)<maxlen:
        sentence+=","*maxlen
        sentence = sentence[:maxlen]
    rowcnt = len(sentence)//maxlen
    colcnt = len(sentence)%maxlen
    for row in range(rowcnt):
        append_lst.append(sentence[row*maxlen:(row+1)*maxlen])
    if colcnt>0:
        append_lst.append(sentence[-colcnt:])
    pred_ner = None
    if ner == 'max':
        pred_ner = bc_ner_max.encode(append_lst)
        #pred_ner = bc_ner_max.encode(append_lst,is_tokenized=True)
    elif ner == 'ner':
        pred_ner = bc_ner.encode(append_lst)
        #pred_ner = bc_ner.encode(append_lst,is_tokenized=True)
    result = []
    [result.extend(pred[:maxlen]) for pred in pred_ner]
    try:
        assert len(result) == len(sentence)
    except:
        raise Exception("len of result if not equal sentence", len(result), len(sentence))
    finally:
        return result
    return result

def get_ner(sentence, ner="ner", maxlen=50):
    '''
    :move window to pick 64 char to feed into algor fetch result
    '''
    #cutlen = maxlen//3
    #cutnum = len(sentence)//cutlen
    #cutlenlst = [i*cutlen for i in range(cutnum+1)]
    append_lst = []
    dq = []
    if len(sentence)<maxlen:
        dummy = [","]*maxlen*2
        dummy = "".join(dummy)
        sentence+=dummy
        sentence = sentence[:2*maxlen]
        pass  # print(sentence)
    for id_,char in enumerate(sentence):
        if id_+maxlen<len(sentence):
            if True: #id_ in cutlenlst:
                batch = sentence[id_:id_+maxlen]
                assert len(batch) == maxlen
                append_lst.append("".join(batch))
            '''
            :use for token
            batch = list(batch)
            batch[-1] = '[CLS]'
            batch.append('[SEP]')
            append_lst.append(batch)
            '''
    try:
        assert len(append_lst) == len(sentence)-maxlen
    except:
        raise Exception("append_lst length %s not equal sentence lenth %s - maxlen length %s "%(len(append_lst),len(sentence), maxlen))
    pred_ner = None
    if ner == 'nermax':
        pred_ner = bc_ner_max.encode(append_lst)
        #pred_ner = bc_ner_max.encode(append_lst,is_tokenized=True)
    elif ner == 'ner':
        pred_ner = bc_ner.encode(append_lst)
        #pred_ner = bc_ner.encode(append_lst,is_tokenized=True)
    else:
        pass
    result = defaultdict(list)
    assert len(pred_ner) == len(append_lst)
    for _idy, pred in enumerate(pred_ner):
        try:
            assert len(pred)==maxlen
            assert maxlen==append_lst[_idy]
        except:
            pass  # print("there is not enough num of pred \r\n%s \r\n%s \r\n%s"%(_idy, pred, append_lst[_idy]))
            pred = pred[:maxlen]
            #raise Exception("there is not enough num of pred %s"%_idy, pred, append_lst[_idy])
        for _idx, lbc in enumerate(pred):
            index = _idx + _idy
            result[index].append(lbc)
            #assert index < len(sentence)
            print(index, len(sentence))
    return result

def pred_ner_block(sentence, filepath,ner):
    with codecs.open(filepath,"a+",'utf-8') as f:
        result = get_ner_block(sentence,ner=ner,maxlen=20)
        try:
            assert len(sentence) == len(result)
        except:
            #print(len(sentence), ' is not equal', len(result))
            #raise Exception(len(sentence), ' is not equal', len(result))
            pass
        preds = []
        cnt = 0
        for key in result:
            if cnt>len(sentence)-1:
                pass  # print("length of sentence and pred is not equal %s %s %s"%(cnt, len(sentence), len(preds)))
                break

            preds.append((sentence[cnt], key))
            f.write("%s\t%s\r\n"%preds[-1])
            pass  # print(preds[-1])
            cnt+=1
        return preds

def pred2json(sent, preds):
    resdct = {}
    snet = preds["cont"]
    for pred in preds["ner"]:
        vl = resdct.get(pred[0],"")
        vl += ","
        vl += sent[pred[1]:pred[2]]
        resdct[pred[0]] =vl
    if not "I-案发地" in resdct:
        print(">> :\r\n",sent)
        print(">> :\r\n",resdct)
        #print(">> 案发地未发现:\r\n",sent)
        #pdb.set_trace()
    resdct["cont"] = sent
    return resdct


def pred_ner(sentence, lb, maxlen):
        if len(sentence) == 0:
            return []
        #with codecs.open(filepath,"a+",'utf-8') as f:
        #f.write("=======================\r\n"*3)
        result = get_ner(sentence, ner=lb, maxlen=maxlen)
        try:
            assert len(sentence) == len(result)
        except:
            pass
            #raise Exception(len(sentence), ' is not equal', len(result))
        preds = []
        for key in result:
            try:
                predchar = cnt_max(sentence[key], result[key])
                preds.append((sentence[key],predchar))
                #pdb.set_trace()
            except IndexError:
                print(key, len(sentence), "is not equal")
            #f.write("%s\t%s\r\n"%preds[-1])
        preds = cnt_word_max(preds)
        preds = jieba_complete(sentence, preds)
        return preds

def xls_read(fp):
    data = xlrd.open_workbook(fp)
    contents = data.sheets()[0].col_values(3)[:200]
    stdner = {}
    maxner = {}
    for cont in contents:
        std__ = pred2json(cont, pred_ner(cont, "ner", 64))
        #max__ = pred2json(cont, pred_ner(cont, "nermax", 64))
        stdner[str(len(stdner))] = std__
        #maxner[str(len(stdner))] = max__
        #print(len(stdner), "FINISH")
    pd.DataFrame(stdner).T.to_csv("stdner.csv")
    #pd.DataFrame(maxner).T.to_csv("maxner.csv")
    print("SUCCESS")

import pandas as pd

def pred_mnli():
    dfs = []
    csv__ = pd.read_csv("barxx.csv")
    for line in csv__.iloc[1:3,1].values:
        line = "我叫金华，我居住在金华，祖籍浙江金华，在金华工具厂做钣金工,上班时，丢失一部手机"
        df = {}
        #cuts = line.split("\t")
        #pred_inp = "%s\t%s"%(cuts[0],cuts[1])
        pred = pred_ner(line, lb="nermax", maxlen=64)
        #pred = get_ner(line, ner="ner", maxlen=64)
        df['cont'] = line
        for preditem in pred["ner"]:
            df[preditem[0]] = line[preditem[1]:preditem[2]]
        dfs.append(df)
        break
    dfs = pd.DataFrame(dfs)
    dfs.to_csv("pred_dfs.csv")
    dfs.T.to_csv("pred_T_dfs.csv")

if __name__ == "__main__":
  pred_mnli()
  #xls_read("电信诈骗案件.xls")

  pass
  """
  with codecs.open("./pred_label.txt","w+",'utf-8') as f:
     print("letus go ...")
     generate = gen()
     n = 200
     maxlen = 64
     while(n>0):
        sentence = generate.__next__()
        ner_word = pred_ner(sentence, 'ner',maxlen)
        nermax_word = pred_ner(sentence, 'nermax', maxlen)
        nerst = set([sentence[word[1]:word[2]] for word in ner_word])
        nermaxst = set([sentence[word[1]:word[2]] for word in ner_word])
        diff_ner = nerst.isdisjoint(nermaxst)
        [f.write("%s\t%s "%(word[0],word[1])) for word in nermax_word]
        if diff_ner:
            print(">>diff_ner ", diff_ner)
            pdb.set_trace()
        #print(pred_ner["ner"])
        n-=1
  """

