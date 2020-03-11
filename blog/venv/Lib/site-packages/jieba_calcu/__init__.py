#!

import sys
import os
import sys

import logging
import logging.handlers
import datetime
from .word_discovery import WordDiscovery

__all__=["WordDiscovery"]

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

logger.debug('debug message')
logger.info('info message')
logger.warning('warning message')
logger.error('error message')
logger.critical('critical message')
'''


class JiebaCalcu(object):
    '''
    the class of count the doc and generate a private
    - probability matrix
    - transition probability 
    '''

    def __init__(self, filepaths):
        self.filenames = []
        try:
            assert type(filepaths) == list
        except:
            raise Exception("the input type should be list")
        for filepath in filepaths:
            #:wself.filenames.extend(self.walk2file(filepath,types=['txt'])[:2])
            self.filenames.extend(self.walk2file(filepath,types=['txt','csv','py','md']))
        #print(self.filenames)
        self.gen = self.gen_files()

    def walk2file(self, path, types):
        '''
        get all the filename we need
        '''
        filenames = []
        for (rootpath, subpaths, subfiles) in os.walk(path):
            for subfile in subfiles:
                if subfile.split(".")[-1] in types:
                    filenames.append(os.path.join(rootpath, subfile))
        return filenames

    def gen_files(self):
        '''
        get the content of all file, and into a generator
        '''
        for filename in self.filenames:
            import codecs
            try:
                for line in codecs.open(filename,'r','utf-8').readlines():
                    yield line
            except:
                print(filename)
                import traceback
                traceback.print_exc()
                continue

    '''
    def gen_file(self, filename):
        for line in open(filename,'r').readlines():
            yield line
    '''

    def word_discovery(self, parax):
        '''
        word_discovery
        '''
        self.gen = self.gen_files()
        self.mWordDiscovery = WordDiscovery(parax,self.gen)
        res = self.mWordDiscovery.word_discovery()
        return res

    def viterbi_cut(self, src):
        from viterbi import viterbi
        result = viterbi(src, self.mWordDiscovery.states, self.mWordDiscovery.emit_prob_bies, self.mWordDiscovery.tran_prob, self.mWordDiscovery.emit_prob)
        return result

'''
if __name__ == '__main__':
    import pdb
    mJiebaCalcu = JiebaCalcu(['/home/qin/pri-jieba-calcu/jieba-calcu/test'])
    print('创建类实例', mJiebaCalcu)
    res = mJiebaCalcu.word_discovery(1.0)
    print('分词结果', res)
'''
