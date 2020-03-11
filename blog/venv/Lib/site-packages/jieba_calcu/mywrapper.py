import functools

def log(func):
    '''
    print the functions name and purpose
    '''
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print('call %s():' % func.__name__)
        print('args = {}'.format(args))
        return func(*args, **kwargs)
    return wrapper

@log
def helloworld():
    print('hello wolrd')

''' the sample '''
# helloworld()

import time
def timer(func):
    def wrapper(*args, **kw):
        t1 = time.time()
        func(*args,**kw)
        t2 = time.time()

        cost_time = t2 - t1
        print( 'cost time: {} s'.format(cost_time))

    return wrapper

@timer
def cost_time(sleep_time):
    time.sleep(sleep_time)
 
''' the sample '''
# cost_time(1)

