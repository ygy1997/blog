import sys
from flask import Flask
from multiprocessing import Process
from flask import request
import re
import collections
import json

from bert_base.client import BertClient

import append_helper
from append_helper import *
import pdb

app = Flask(__name__)


@app.route("/ner", methods=["GET","POST"])
def ner():
    data = request.get_data()
    json_data = json.loads(data.decode("utf-8"))
    sentence = json_data.get("content")
    result = pred_ner(sentence, "nermax", 64)
    return json.dumps({"results":result}, ensure_ascii=False)

@app.route("/stdner", methods=["GET","POST"])
def stdner():
    data = request.get_data()
    json_data = json.loads(data.decode("utf-8"))
    sentence = json_data.get("content")
    print(sentence)
    result = pred_ner(sentence, "ner", 64)
    return json.dumps({"results":result}, ensure_ascii=False)

if __name__ == "__main__":
    app.run(port=5554, threaded=True, host="0.0.0.0",debug=True)
