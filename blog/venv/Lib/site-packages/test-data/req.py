import requests, json
import pdb
import re
import codecs
import chardet
import pandas as pd


def clr(sent):
    sent.strip()
    sent = re.sub("\r","",sent)
    sent = re.sub("\n","",sent)
    sent = re.sub(" ","",sent)
    sent = re.sub("\t","",sent)
    #sent = re.sub("[^\u4e00-\u9fa50-9a-zA-Z]","",sent)
    return sent

github_url = "http://nlp.tripet.com.cn:8088/ner"
github_url = "http://122.152.198.99:8088/stdner"

def onebyone(res, lin, flag):
    if flag == 1:
        flag = 0
        res = ""
    if '\t' in lin:
        res+=lin.split("\t")[0]
        #print(res)
        return res,flag 
    else:
        flag = 1
        #print(res)
        return res,flag 

if __name__ == "__main__":
    dfs = {} 
    df = pd.read_csv("barxx.csv")
    #with codecs.open("./test.txt","r","utf-8") as f:
    for line in df.iloc[:,2].values:
        sent = line.split("\t")[0]
        sent = clr(sent)
        print(sent)
        data = json.dumps({"content":sent},ensure_ascii=False)
        data = data.encode("utf-8")
        r = requests.post(github_url, data)
        if r.status_code==200:
            results = json.loads(r.content)["results"]["ner"]
            __dct = {}
            __dct['sent'] = sent
            for lr in results:
                __dct[lr[0]] =  __dct.get(lr[0], "")
                __dct[lr[0]]+= ","
                __dct[lr[0]]+= sent[lr[1]:lr[2]]
                print(lr[0] + '\t' + sent[lr[1]:lr[2]])
            dfs[str(len(dfs))] = __dct
        else:
            pdb.set_trace()
        dfs_ = pd.DataFrame(dfs)
        dfs_.T.to_csv("2019-9-18-guiyang-baoanrenxinxi-pred.csv")


