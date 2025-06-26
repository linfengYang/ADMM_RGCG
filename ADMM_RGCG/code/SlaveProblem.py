# 求解SlaveProblem

from GModel import GModel
import scipy.sparse as sp
from GurobiSolve import GurobiSolve
from gurobipy import *
import numpy as np

def SlaveProblem(i,model_i,pzusd,GAP,TimeLimit,firstSlave,model_slave,rhslow,rhsup,sflag):

    if firstSlave[i]: #如果第一次调用本函数
        firstSlave[i]=0
        model_slave.lb=model_i.lb+[0]
        model_slave.ub=model_i.ub+[np.inf]
        model_slave.vtype=model_i.vtype+[GRB.CONTINUOUS]

        #目标函数
        model_slave.f=np.zeros(len(model_slave.lb))
        model_slave.f[-1]=1

        #约束条件
        model_slave.Aeq=model_i.Aeq_pzuvw[:pzusd.size,:]
        model_slave.Aeq=sp.hstack([model_slave.Aeq,sp.lil_matrix((model_slave.Aeq.shape[0],1))],format='lil')
        model_slave.beq=pzusd
        Aeq_s = sp.hstack([model_i.Aeq_s, sp.lil_matrix((model_i.Aeq_s.shape[0], 1))], format='lil')
        model_slave.Aeq=sp.hstack([model_slave.Aeq,Aeq_s],format='lil')
        model_slave.beq=np.append(model_slave.beq,model_i.beq_s)

        model_slave.Aineq=sp.hstack([model_i.Aineq_s,sp.lil_matrix(model_i.Aineq_s.shape[0],1)],format='lil')
        model_slave.Aineq[:,-1]=-1
        model_slave.bineq=model_i.bineq_s
    else:
        model_slave.beq[:pzusd.size]=pzusd

    (q_p_x_y_s,Gmodel_Slave)=GurobiSolve('Relax',model_slave,GAP,TimeLimit,0,0,GRB.MINIMIZE)
    if Gmodel_Slave.ObjVal==0:
        #变量在凸包里面
        sflag[i]=0
        if len(rhslow)>0:
            rhslow = np.vstack((rhslow,np.array(Gmodel_Slave.getAttr(GRB.Attr.SARHSLow)[:pzusd.size])))
            rhsup = np.vstack((rhsup,np.array(Gmodel_Slave.getAttr(GRB.Attr.SARHSUp)[:pzusd.size])))
        else:
            rhslow = np.array(Gmodel_Slave.getAttr(GRB.Attr.SARHSLow)[:pzusd.size])
            rhsup = np.array(Gmodel_Slave.getAttr(GRB.Attr.SARHSUp)[:pzusd.size])
    #不在凸包里
    x = np.array(Gmodel_Slave.getAttr("Pi",Gmodel_Slave.getConstrs()))  # 获得松弛问题的最优对偶变量
    l_k = x[:pzusd.size]
    b = np.append(model_i.beq_s,model_i.bineq_s)
    g = -1 * np.dot(x[pzusd.size:],b)

    return (Gmodel_Slave.ObjVal,l_k,g,rhslow,rhsup)