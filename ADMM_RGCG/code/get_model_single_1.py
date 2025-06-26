from GurobiSolve import GurobiSolve
from gurobipy import *
import scipy.sparse as sp
import numpy as np
from GModel import GModel

def get_model_single(dataUC,model_single,model_master,y_min,y_max,K,cx,BxT,R,G,ineq_st,eq_st,pz_num,AddPoint,AddCut,G2,G3,V_G2,V_G3,G2Flag,G3Flag):

    model_PI=[[] for _ in range(dataUC.N)]
    for i in range(dataUC.N):
        if i in G2:
            model_PI[i]=model_G2(dataUC,model_single,model_master,y_min,y_max,K,cx,BxT,V_G2,G2Flag,AddPoint,i)
        if i in G3:
            model_PI[i]=model_G3(dataUC,model_single,model_master,y_min,y_max,R,G,ineq_st,eq_st,pz_num,V_G3,G3Flag,AddCut,i)

    return model_PI

def model_G2(dataUC,model_single,model_master,y_min,y_max,K,cx,BxT,V_G2,G2Flag,AddPoint,i):
    
    if AddPoint[i]:
        #机组i的K集有新增的点
        BxT_k = sp.lil_matrix(np.dot(model_single[i].Aeq_c.toarray(),K[i][-1, :]))   # BxT
        cx_k = np.dot(model_single[i].f, K[i][-1, :])   # cx
        BxT[i] = sp.vstack([BxT[i], BxT_k], format='lil')
        cx[i].append(cx_k)

        increment = sp.lil_matrix(np.zeros(model_master[i].Aineq.shape[1]))
        increment[0,:dataUC.T] = BxT_k
        increment[0,dataUC.T] = 1
        model_master[i].Aineq = sp.vstack([model_master[i].Aineq, increment], format='lil')
        model_master[i].bineq = np.append(model_master[i].bineq, cx_k)
        
    elif G2Flag[i]: #集合G2机组有变
        increment = sp.lil_matrix(np.ones((BxT[i].shape[0],1)))
        if V_G2[i].Aineq == []:
            V_G2[i].Aineq = increment
        else:
            V_G2[i].Aineq = sp.block_diag([V_G2[i].Aineq, increment], format='lil')
        if V_G2[i].Aineq_c == []:
            V_G2[i].Aineq_c = BxT[i]
        else:
            V_G2[i].Aineq_c = sp.vstack([V_G2[i].Aineq_c, BxT[i]], format='lil')
        V_G2[i].f = np.append(V_G2[i].f,1)
        V_G2[i].lb.append(-np.inf)
        V_G2[i].ub.append(np.inf)
        V_G2[i].bineq = np.append(V_G2[i].bineq, np.array(cx[i]))

        model_master[i].lb.extend(y_min * np.ones(dataUC.T))  # y
        model_master[i].ub.extend(y_max * np.ones(dataUC.T))  # y
        model_master[i].lb.extend(V_G2[i].lb)
        model_master[i].ub.extend(V_G2[i].ub)
        model_master[i].vtype=GRB.CONTINUOUS
        model_master[i].f=np.concatenate((model_single[0].beq_c,V_G2[i].f))

        coupleAineq = []
        model_master[i].bineq = V_G2[i].bineq
        if V_G2[i].Aineq!= []:
            if model_master[i].Aineq==[]:
                model_master[i].Aineq=V_G2[i].Aineq
                coupleAineq=V_G2[i].Aineq_c
            else:
                model_master[i].Aineq = sp.bmat([[None, model_master[i].Aineq], [V_G2[i].Aineq, None]], format='lil')
                coupleAineq = sp.vstack([coupleAineq, V_G2[i].Aineq_c], format='lil')
        model_master[i].Aineq=sp.hstack([coupleAineq, model_master[i].Aineq],format='lil')

    return model_master[i]

def model_G3(dataUC,model_single,model_master,y_min,y_max,R,G,ineq_st,eq_st,pz_num,V_G3,G3Flag,AddCut,i):
    
    if G3Flag[i]!=1:
        if AddCut[i]: #如果有新增割平面
            incre_ineq=sp.lil_matrix((model_master[i].Aineq.shape[0],1))
            incre_eq=sp.lil_matrix((model_master[i].Aeq.shape[0],1))
            cut=R[i].T #求转置
            if cut.ndim>1:
                uvw_num = cut.shape[0] - pz_num
                incre_ineq[ineq_st[i]:ineq_st[i]+uvw_num,0] = cut[pz_num:, -1]
                incre_eq[eq_st[i]:eq_st[i]+pz_num,0] = cut[:pz_num, -1]
            else:
                uvw_num = cut.size - pz_num
                incre_ineq[ineq_st[i]:ineq_st[i]+uvw_num,0] = cut[pz_num:]
                incre_eq[eq_st[i]:eq_st[i]+pz_num,0] = cut[:pz_num]
            model_master[i].Aineq = sp.hstack([model_master[i].Aineq, incre_ineq], format='lil')
            model_master[i].Aeq = sp.hstack([model_master[i].Aeq, incre_eq], format='lil')
            model_master[i].f = np.append(model_master[i].f, G[i][-1])
            model_master[i].lb.append(-np.inf)
            model_master[i].ub.append(0)
    
    if G3Flag[i]:
        model_master[i].lb.extend(y_min * np.ones(dataUC.T))  # y
        model_master[i].ub.extend(y_max * np.ones(dataUC.T))  # y
        model_master[i].lb.extend(V_G3[i].lb)
        model_master[i].ub.extend(V_G3[i].ub)
        model_master[i].vtype = GRB.CONTINUOUS

        model_master[i].f = np.concatenate((model_single[0].beq_c,V_G3[i].f))
        coupleAeq = []
        model_master[i].beq=V_G3[i].beq

        if V_G3[i].Aeq != []:
            model_master[i].Aeq = V_G3[i].Aeq
            coupleAeq = V_G3[i].Aeq_c
        if model_master[i].Aeq!=[]:
            model_master[i].Aeq = sp.hstack([coupleAeq,model_master[i].Aeq], format='lil')
        
        coupleAineq=[]
        model_master[i].bineq=V_G3[i].bineq

        if V_G3[i].Aineq != []:
            model_master[i].Aineq = V_G3[i].Aineq
            coupleAineq = V_G3[i].Aineq_c
        model_master[i].Aineq = sp.hstack([coupleAineq, model_master[i].Aineq], format='lil')

    return model_master[i]

