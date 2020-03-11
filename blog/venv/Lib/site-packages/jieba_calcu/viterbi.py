import sys
import operator
import pickle

MIN_FLOAT = -3.14e100
MIN_INF = float("-inf")
print(MIN_INF)
print(MIN_FLOAT)

if sys.version_info[0] > 2:
    xrange = range

def get_top_states(t_state_v, K=4):
    return sorted(t_state_v, key=t_state_v.__getitem__, reverse=True)[:K]

def viterbi(obs, states, start_p, trans_p, emit_p):
    import pdb
    print('矩阵信息打印')
    #pdb.set_trace()
    V = [{}]  # tabular
    mem_path = [{}]
    all_states = trans_p.keys()
    for y in states.get(obs[0], all_states):  # init
        V[0][y] = start_p[y] + emit_p[y].get(obs[0], MIN_FLOAT)
        mem_path[0][y] = ''
    print('>> mem_path ', mem_path)
    print('>> V', V)
    for t in xrange(1, len(obs)):
        V.append({})
        mem_path.append({})
        #prev_states = get_top_states(V[t-1])
        prev_states = [
            x for x in mem_path[t - 1].keys() if len(trans_p.get(x,[])) > 0]
        print('>> perv_states', prev_states)

        prev_states_expect_next = set(
            (y for x in prev_states for y in trans_p[x].keys()))
        print(">> prev_states_expect_next ", prev_states_expect_next)

        obs_states = set(
            states.get(obs[t], all_states)) & prev_states_expect_next
        print('>> obs_states', obs_states)

        if not obs_states:
            obs_states = prev_states_expect_next if prev_states_expect_next else all_states
            print('>> obs_states', obs_states)

        print(obs_states)
        for y in obs_states:
            '''add'''
            print('>> V', V)
            cal_tmp = ((V[t - 1][y0] , trans_p[y0].get(y, MIN_INF) ,
                               emit_p[y].get(obs[t], MIN_FLOAT), y0) for y0 in prev_states)
            for cal_tmp_one in cal_tmp:
                print('>> V, trans, emit, y0')
                print('>> cal_tmp_one ', list(cal_tmp_one))
            #pdb.set_trace()
            '''add end'''

            prob, state = max((V[t - 1][y0] + trans_p[y0].get(y, MIN_INF) +
                               emit_p[y].get(obs[t], MIN_FLOAT), y0) for y0 in prev_states)
            V[t][y] = prob
            mem_path[t][y] = state
            print('>> mem_path ',t, y , mem_path)
            print('>> prob, state, calcu')
            #pdb.set_trace()

    last = [(V[-1][y], y) for y in mem_path[-1].keys()]
    # if len(last)==0:
    #     print obs
    prob, state = max(last)

    route = [None] * len(obs)
    i = len(obs) - 1
    while i >= 0:
        route[i] = state
        state = mem_path[i][state]
        i -= 1
    return (prob, route)

def viterbi_test(sent, prob_from='./data.pkl'):
    def pickle_load_prob_mat(filepath):
        pkl = open(filepath,'rb')
        trans_p = pickle.load(pkl)
        emit_p = pickle.load(pkl)
        start_p = pickle.load(pkl)
        states = pickle.load(pkl)
        return states, start_p, trans_p, emit_p
    states, start_p, trans_p, emit_p = \
        pickle_load_prob_mat(prob_from)
    prob, route = viterbi(sent, states, start_p, trans_p, emit_p)
    print('prob', prob)
    print('route', route)
    words = []
    for i,j in zip(route, sent):
        if i[0] in ['B','S']:
            words.append(j)
        elif i[0] == 'I':
            words[-1]+=j
        elif i[0] == 'E':
            words[-1]+=j
    return words

if __name__ == '__main__':
    '''
    import jieba
    import jieba.posseg
    for i in jieba.posseg.cut('大家好，我是谷爱灵'):
        pass

    '''
    cont = '国家主席江泽民与马来西亚总统，中国人民的老朋友马哈蒂尔主席，共同走过了，红毯，接受三军仪仗队检阅'
    cont = '安徽省合肥市肥东县八斗路镇北恢复楼8栋802室'
    cont = '10,A3401040801002019091893,2019年9月14日，报案人（姓名：刘健康，男，身份证号码：341622200007102138；电话：17364449003，户籍住址：安徽省亳州市蒙城县立仓镇罗集社区老街中庄24-1号，家庭住址：安徽省合肥市蜀山区警官职业技术学院）报案称：2019年9月14日17时许，其在交易猫APP上与客服联系告诉对方要买一个游戏账号，对方告诉让其将钱转入平台用于保证金，之后其通过软件平台支付3997元，之后其一直没有收到游戏账号。受害人支付宝账号：17364449003。经查，拟立案。,2019-09-15 01:31:58000000'
    #viterbi_test('人中吕布，马中赤兔，江阔云低，断雁叫西风', './data.pkl')
    #viterbi_test('人中吕布，马中赤兔，江阔云低，断雁叫西风', './localdata.pkl')

    #viterbi_test(cont, './data.pkl')
    words = viterbi_test(cont, './localdata.pkl')
    [print(word) for word in words]


