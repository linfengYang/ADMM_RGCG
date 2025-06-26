import numpy as np
from VCon import VCon
from CreateV_G134 import CreateV_G134
from CreateV_G134_Dual import CreateV_G134_Dual

def division_G(dataUC,tightflag,model_single,G1flag,G2flag,G3flag,dualflag):
    # tightflag:1表示用紧模型如'TP'来代替凸包，0表示用很松的'2P'模型来代替凸包，2表示初始价格随机，3表示直接用凸包模型
    G_1 = []  # 用凸包模型的机组集合1
    G_2 = []  # 用列生成的机组集合2
    G_3 = []  # 用行生成的机组集合3
    R = [[]] * dataUC.N  # 记录每个机组的割平面左端项系数
    G = [[]] * dataUC.N  # 记录每个机组的割平面右端项
    eq_st = [[]] * dataUC.N  # 记录每个机组的无约束变量在所有G3无约束变量中的开始索引
    ineq_st = [[]] * dataUC.N  # 记录每个机组的>=0变量在所有G3>=0变量中的开始索引
    eq_end = [[]] * dataUC.N  # 记录每个机组的无约束变量在所有G3无约束变量中的结束索引
    ineq_end = [[]] * dataUC.N  # 记录每个机组的>=0变量在所有G3>=0变量中结束索引
    M = np.zeros(dataUC.N)
    V_G1 = VCon()

    #data_UC.iframp[i]=1表示机组i考虑爬坡约束, 0表示否.如果考虑爬坡约束，则该机组属于集合G2，否则属于集合G1
    for i in range(dataUC.N):
        if dataUC.iframp[i]:
            a_ON = np.ceil((dataUC.p_up[i] - dataUC.ramp_on[i]) / dataUC.ramp_up[i]) + 1
            a_OFF = np.ceil((dataUC.p_up[i] - dataUC.ramp_off[i]) / dataUC.ramp_down[i]) + 1
            a_UP = np.ceil(dataUC.p_up[i] / dataUC.ramp_up[i])
            a_DOWN = np.ceil(dataUC.p_up[i] / dataUC.ramp_down[i])
            M[i] = max(a_ON, a_OFF, a_UP, a_DOWN, 2)
        if (dataUC.iframp[i] or G1flag != 1) and tightflag != 3:
            #dataUC.iframp[i]=1为G2，0就是G1
            if G2flag or (G3flag != 1 and dataUC.iframp[i]):
                # G2Flag=1表示初始时所有机组都放在G2
                G_2.append(i)
            if G3flag or (G2flag != 1 and dataUC.iframp[i] != 1): 
                # G3Flag=1表示初始时所有机组都放在G3
                G_3.append(i)
        else:
            G_1.append(i)
            #拼接原始G1的凸包矩阵
            if dualflag:
                CreateV_G134_Dual(V_G1,R[i],G[i],model_single[i],1)
            else:
                CreateV_G134(V_G1,R[i],G[i],model_single[i],1)
    return (G_1, G_2, G_3, eq_st,ineq_st,eq_end,ineq_end,M,V_G1)
        