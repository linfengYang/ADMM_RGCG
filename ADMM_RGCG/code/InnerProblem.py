import numpy as np
import copy
from GurobiSolve import GurobiSolve
from gurobipy import *     # 在Python中调用gurobi求解包
from readdataUC import dataUC
from model_2P_single import model_2P_single

def InnerProblem(model, y_k, GAP, TimeLimit):
    model_inner = copy.copy(model)
    model_inner.Aeq = model_inner.Aeq_s
    model_inner.Aineq = model_inner.Aineq_s
    model_inner.beq = model_inner.beq_s
    model_inner.bineq = model_inner.bineq_s

    ################################################## 目标函数 min sum((c_i - y * B_i) * x_i)
    model_inner.f = model.f - np.dot(y_k, model_inner.Aeq_c.toarray())

    ################################################## Optimize model
    (x_k, inner) = GurobiSolve('MIP', model_inner, GAP, TimeLimit, 0, 0, GRB.MINIMIZE)

    return (x_k, inner.ObjVal+np.dot(y_k, model.beq_c))

'''
if __name__=='__main__':
    filename=r'UC_AF/10_std.mod'
    data=dataUC(filename)
    model=model_2P_single(data,1,0,10,0,1)
    lamda=1000*np.ones(data.T)
    (x,ans)=InnerProblem(model,lamda,1e-3,1000)
    
    print(ans)
'''