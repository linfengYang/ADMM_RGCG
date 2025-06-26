# 函数说明：得到初始的上下界和初始解

from gurobipy import *
from InitPrice import InitPrice
from GurobiSolve import GurobiSolve
from Master_Problem import MasterProblem
from Master_Problem_Dual import MasterProblemDual
from SubProblem import SubProblem
from GModel import GModel
from VCon import VCon
from division_G import division_G
from CreateV_G134 import CreateV_G134
from CreateV_G134_Dual import CreateV_G134_Dual
import numpy as np

from readdataUC import dataUC
from model_MP import produce_model
from ADMM_DRMP_parallel import ADMM_DRMP_parallel

def Init_ADMM_parallel(dataUC,boolean_MILP,QP,J,SpinFlag,GAP,TimeLimit,TightFlag,isbound,model,model_single,G1Flag,G2Flag,G3Flag,sigma,K,DualFlag,pz_num,p_k,y_k,rou,abs_tol,rel_tol):
    
    #先将机组按特性进行分类,分为1/2/3类
    (G_1, G_2, G_3, eq_st,ineq_st,eq_end,ineq_end,M,V_G1)=division_G(dataUC,TightFlag,model_single,G1Flag,G2Flag,G3Flag,DualFlag)
    (y0, model_relax, K, K_num,AddPoint, Bx, bineq_i,lb, var_num, model_single_TP)=InitPrice(TightFlag,dataUC,boolean_MILP,QP,J,SpinFlag,GAP,TimeLimit,model,model_single,G_1,G_2,G_3,K,G2Flag,pz_num)
    if isbound and TightFlag!=2: #有上下界
        y_min = np.minimum(y0 * sigma, y0 / sigma)
        y_max = np.maximum(y0 * sigma, y0 / sigma)
    else:
        y_min = -1 * np.inf * np.ones(dataUC.T)
        y_max = np.inf * np.ones(dataUC.T)
    
    # 生成机组i的紧模型
    V_G3 = [VCon() for _ in range(dataUC.N)]
    R = [[]] * dataUC.N  # 记录每个机组的割平面左端项系数
    G = [[]] * dataUC.N  # 记录每个机组的割平面右端项
    for i in G_3:  # 遍历机组集G3
        if DualFlag:
            eq_st[i] = len(V_G3[i].beq)
            ineq_st[i] = len(V_G3[i].bineq)
            CreateV_G134_Dual(V_G3[i], R[i], G[i], model_single_TP[i], 3)
            eq_end[i] = len(V_G3[i].beq)
            ineq_end[i] = len(V_G3[i].bineq)
        else:
            CreateV_G134(V_G3, R[i], G[i], model_single_TP[i], 3)

    # 初始上界
    model_master=[GModel() for _ in range(dataUC.N)]
    V_G2 = [VCon() for _ in range(dataUC.N)]
    
    AddCut = np.zeros(dataUC.N)  # AddCut[i]为1表示机组i有新增的割平面
    R = [[]] * dataUC.N  # 记录每个机组的割平面左端项系数
    G = [[]] * dataUC.N  # 记录每个机组的割平面右端项
    if DualFlag:   # 1表示解DRMP，0表示解RMP
        (y,alpha,x,delta,ub) = ADMM_DRMP_parallel(dataUC,model_single,model_master,y_min,y_max,GAP,TimeLimit,K,bineq_i,Bx,R,G,ineq_st,eq_st,pz_num,G_2,G_3,V_G2,V_G3,G2Flag,G3Flag,AddPoint,AddCut,p_k,y_k,rou,abs_tol,rel_tol)
    ################################################## 初始下界
    if len(G_1) == dataUC.N:
        (x_k, lb) = SubProblem(model, y, GAP, TimeLimit)
    else:
        G_13 = G_1 + G_3
        for i in G_13:  # 遍历机组集1,3
            model_relax[i].f = model_single[i].f - np.dot(y0, model_single[i].Aeq_c.toarray())
            (x_k, r_model) = GurobiSolve('MIP', model_relax[i], GAP, TimeLimit, boolean_MILP, QP, GRB.MINIMIZE)
            lb += r_model.ObjVal

    return (
    ub, lb, y,delta,alpha,y0, model_relax, model_master, K, K_num, Bx, bineq_i, G_1, G_2, G_3, V_G1, V_G3,y_max, y_min,x,eq_st,ineq_st,eq_end,ineq_end,M,model_single_TP,var_num)

