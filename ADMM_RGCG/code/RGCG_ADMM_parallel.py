import copy
from CreateV_G134 import CreateV_G134
from CreateV_G134_Dual import CreateV_G134_Dual
from GurobiSolve import GurobiSolve
import numpy as np
import scipy.sparse as sp
import time
from SlaveProblem import SlaveProblem
import model_BenK_single
from GModel import GModel
from VCon import VCon
from gurobipy import *     # 在Python中调用gurobi求解包
from Init_ADMM_parallel import Init_ADMM_parallel
#from ADMM_DRMP_1 import ADMM_DRMP_1
from ADMM_DRMP_parallel_1 import ADMM_DRMP_parallel_1
from WriteResult import WriteResult
from UpdateSheet import UpdateSheet
from concurrent.futures import ThreadPoolExecutor, as_completed

def solve_g2_subproblem(i, model_r, model_single, p_k, GAP, TimeLimit, boolean_MILP, QP):
    #
    #
    #Due to the uncertainty of the review cycle, we have annotated the key parts of the code. If the paper is accepted, we will make it public.
    #
    #

def solve_g3_subproblem(i,model_single_BenK,pzuvw, GAP, TimeLimit, firstSlave, model_slave, sFlag, rhsLow, rhsUp,flaglow,flagup):
    #
    #
    #Due to the uncertainty of the review cycle, we have annotated the key parts of the code. If the paper is accepted, we will make it public.
    #
    #

def RGCG_parallel(data_UC,boolean_MILP,QP,J,SpinFlag,history,facet,mflag, PitFlag, UitFlag,GAP,TimeLimit,TightFlag,boxFlag,miu,DoubleFlag,UCObjVal,model,model_single,G1Flag,G2Flag,G3Flag,RelativeFlag,eps,InitialK,wflag,DualFlag,result_path):
    start_time = time.time()
    #——————————————————————————————————————————————————初始化————————————————————————————————————————————————————————#
    eta=0.5
    beta=0.5
    sigma = 0.5
    NumericTrouble = 0
    maxKPointNum = 100  
    maxRCutNum = 100
    iterate_uplift = []
    UB = []
    if boolean_MILP:
        pz_num = 2 * data_UC.T
    else:
        pz_num = data_UC.T
    
    dual_eps=1e-2
    pri_eps=1e-2
    rou=1
    p_k=np.zeros(data_UC.T)
    y_k=np.zeros((data_UC.N,data_UC.T))
    
    ################################################## 得到初始的上下界和初始解
    K = copy.copy(InitialK)  # 浅拷贝只复制引用（id），InitialK下一个TightFlag还要继续用
    (f_ub_k, f_lb_k, y, delta,alpha,y_0, model_r, model_master, K, KPointNum, Bx_T, bineq_i, G_1, G_2, G_3, V_G1, V_G3, y_max,
     y_min, x, eq_st, ineq_st, eq_end, ineq_end, M, model_single_TP, var_num) = Init_ADMM_parallel(data_UC,
                                                                                        boolean_MILP, QP, J,
                                                                                        SpinFlag,
                                                                                        GAP, TimeLimit,
                                                                                        TightFlag, boxFlag,
                                                                                        model, model_single,
                                                                                        G1Flag, G2Flag, G3Flag,
                                                                                        sigma, K, DualFlag,
                                                                                        pz_num,p_k,y_k,rou,pri_eps,dual_eps)

    iterate_uplift.append(UCObjVal - f_lb_k)
    UB.append(f_ub_k)
    if len(G_1) == data_UC.N:
        ps = y
    else:
        ps = y_0
    ################################################## 提前建模
    R = [[]] * data_UC.N  # 记录每个机组的割平面左端项系数
    G = [[]] * data_UC.N  # 记录每个机组的割平面右端项
    RCutNum = np.zeros(data_UC.N)  # RCutNum[i]为机组i的割平面数量
    model_single_BenK = [[]] * data_UC.N
    model_slave = [[]] * data_UC.N
    firstSlave = np.ones(data_UC.N)
    sFlag = np.ones(data_UC.N)  # 1表示尚未找到一个凸包内的点，未做灵敏度分析
    flaglow = 0
    flagup = 0
    rhsLow = [[]] * data_UC.N  # s保持0的最小右侧值
    rhsUp = [[]] * data_UC.N  # s保持0的最大右侧值
    sNum = np.zeros(data_UC.N)
    for i in G_3:
        model_slave[i] = GModel()
        model_single_BenK[i] = model_BenK_single.Build_Single(data_UC, boolean_MILP, QP, J, SpinFlag, i,wflag)
    V_G2 = [VCon() for _ in range(data_UC.N)]

    iterate_num = 0  # 记录迭代次数
    initial_time = time.time() - start_time
    ###############################################################################################################
    p_k_old=np.zeros(data_UC.T)
    
    #————————————————————开始迭代——————————————————————#
    start_time = time.time()
    while 1:
        iterate_num += 1
        print(iterate_num)
        
        G2Flag=np.zeros(data_UC.N)
        G3Flag=np.zeros(data_UC.N)

        p_k=y   # p_k_new
        y_k=alpha
        L_k = np.dot(p_k, model.beq_c)

        AddPoint = np.zeros(data_UC.N)
        terminate_G2=1
        terminate_G3=1
        delta_k=delta

        #
        #
        #Due to the uncertainty of the review cycle, we have annotated the key parts of the code. If the paper is accepted, we will make it public.
        #
        #

        time_solve=time.time()-start_time
        if (terminate_G2 and terminate_G3) or time_solve>TimeLimit:
            #
            #
            #Due to the uncertainty of the review cycle, we have annotated the key parts of the code. If the paper is accepted, we will make it public.
            #
            #
            iterate_uplift.append(UCObjVal - f_lb_k)
            break
    
        if DualFlag:
            (y,alpha,x,delta,f_ub_k)=ADMM_DRMP_parallel_1(data_UC,model_single,model_master,y_min,y_max,GAP,TimeLimit,K,bineq_i,Bx_T,R,G,ineq_st,eq_st,pz_num,G_2,G_3,V_G2,V_G3,G2Flag,G3Flag,AddPoint,AddCut,p_k,y_k,rou,pri_eps,dual_eps)

    #————————————————————————————————————迭代结束————————————————————————————————————#
    # 计算上抬费用uplift payment
    Uplift = UCObjVal - f_lb_k
    if TightFlag != 3:
        UpdateSheet(result_path, TightFlag,0,DualFlag)
    WriteResult('NCG', result_path, TightFlag, y_0, ps, Uplift, KPointNum, data_UC.iframp, M, RCutNum,
                initial_time, iterate_num, time_solve, sigma, f'{RelativeFlag}{eps}', beta, maxKPointNum, maxRCutNum,
                eta, y_max, y_min, NumericTrouble, f_ub_k, f_lb_k, iterate_uplift, UB, G_1, G_2, G_3, DualFlag,
                sNum)
    print(UCObjVal)
    print(f_lb_k)
    print(Uplift)
    print(time_solve)