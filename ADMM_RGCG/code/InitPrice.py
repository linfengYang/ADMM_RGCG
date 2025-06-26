# 解松弛模型求取初始价格y

from model_MP import produce_model
from GurobiSolve import GurobiSolve
from gurobipy import *
import copy
import scipy.sparse as sp
import numpy as np

def InitPrice(TightFlag,dataUC,boolean_MILP,QP,J,SpinFlag,GAP,TimeLimit,model,model_single,G_1,G_2,G_3,K,G2Flag,pz_num):
    y0=np.zeros(dataUC.T)
    if len(G_1)<dataUC.N and TightFlag!=2:
        if TightFlag==0:
            #不用紧模型
            model_LR=model
        elif TightFlag==1:
            #使用紧模型
            (model_LR,model_single_LR)=produce_model(dataUC,TightFlag,boolean_MILP,QP,J,SpinFlag)

        (x0,Gmodel)=GurobiSolve('Relax',model_LR,GAP,TimeLimit,boolean_MILP,QP,GRB.MINIMIZE)
        pi=np.array(Gmodel.getAttr("Pi", Gmodel.getConstrs()))
        y0=pi[:dataUC.T]
    
    #创建(17)式子的模型
    model_relax=[[]]*dataUC.N
    Bx=[[]]*dataUC.N
    c=[[]]*dataUC.N
    K_num=np.ones(dataUC.N) # 记录每个机组中K_i中点的个数
    AddPoint=np.zeros(dataUC.N) # AddPoint[i]为1表示机组i的K集有新增的点
    #pi'*b
    La_k=np.dot(y0,model.beq_c)
    # 开始处理G2要删除的点
    index=0
    var_num=np.int32(np.zeros(dataUC.N))
    unit_delete=[]
    for i in range(dataUC.N):
        model_relax[i]=copy.copy(model_single[i])
        if TightFlag==0:
            var_num[i]=model_single[i].var_num
        elif TightFlag==1:
            var_num[i]=model_single_LR[i].var_num
        if i in G_2:
            if G2Flag!=1:
                us=x0[index+pz_num:index+var_num[i]]
                interger=np.all((us==0) or (us==1))
                if interger: #是整数，移到G3，不在G2里
                    G_3.append(i)
                    unit_delete.append(i)
        index+=var_num[i]
    for i in unit_delete:
        G_2.remove(i)
    for i in G_2:
        Bx[i]=sp.lil_matrix(np.dot(model_single[i].Aeq_c.toarray(),K[i]))
        c[i]=[np.dot(model_single[i].f, K[i])]

        model_relax[i].f=model_single[i].f-np.dot(y0,model_single[i].Aeq_c.toarray())
        (x_k,relax_model)=GurobiSolve('MIP',model_relax[i],GAP,TimeLimit,boolean_MILP,QP,GRB.MINIMIZE)
        La_k+=relax_model.ObjVal
        K[i]=np.vstack((K[i],x_k))
        Bx_k = sp.lil_matrix(np.dot(model_single[i].Aeq_c.toarray(), K[i][-1, :]))
        c_k = np.dot(model_single[i].f, K[i][-1, :])  
        Bx[i] = sp.vstack([Bx[i], Bx_k], format='lil')
        c[i].append(c_k)
        K_num[i] += 1
    if TightFlag == 1:
        return(y0, model_relax, K, K_num,AddPoint, Bx, c,La_k, var_num, model_single_LR)
    else:
        return(y0, model_relax, K, K_num,AddPoint,Bx,c,La_k, var_num, model_single)