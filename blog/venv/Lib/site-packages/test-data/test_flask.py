import sys
from flask import Flask
from multiprocessing import Process
from bert_base.client import BertClient
from flask import request
import re
import collections
import json
import pdb


app = Flask(__name__)

@app.route("/nerboost", methods=["GET","POST"])
def post_ner_boost():
    #sentence = re.sub("[\r\n\t ]","",sentence)
    pred_ner = bc_ner.encode([sentence])
    pred_ner_max = bc_ner_max.encode([sentence])
    result = combine(pred_ner, pred_ner_max)
    print(' '.join(list(sentence)))
    print(pred_ner)
    print(pred_ner_max)
    return json.dumps({"results":result}, ensure_ascii=False)
    #return json.dumps({"results":'/'.join(pred_ner[0])}, ensure_ascii=False)

@app.route("/ner", methods=["GET","POST"])
def post_ner():
    data = request.get_data()
    json_data = json.loads(data.decode("utf-8"))
    sentence = json_data.get("content")
    #sentence = re.sub("[\r\n\t ]","",sentence)
    print(sentence)
    pred_ner = bc_ner.encode([sentence])
    print(pred_ner)
    #result = combine(pred_ner, pred_ner_max)
    #return json.dumps({"results":result}, ensure_ascii=False)
    return json.dumps({"results":'/'.join(pred_ner[0])}, ensure_ascii=False)


@app.route("/nermax", methods=["GET","POST"])
def post_ner_max():
    data = request.get_data()
    json_data = json.loads(data.decode("utf-8"))
    sentence = json_data.get("content")
    #sentence = re.sub("[\r\n\t ]","",sentence)
    print(sentence)
    pred_ner = bc_ner_max.encode([sentence])
    print(pred_ner)
    #result = combine(pred_ner, pred_ner_max)
    #return json.dumps({"results":result}, ensure_ascii=False)
    return json.dumps({"results":'/'.join(pred_ner[0])}, ensure_ascii=False)

if __name__ == "__main__":
    app.run(port=5554, threaded=True, host="0.0.0.0",debug=True)



