from GurobiSolve import GurobiSolve
from gurobipy import *
import scipy.sparse as sp
import numpy as np
from solve_SubProblem_G2 import solve_SubProblem_G2
from solve_SubProblem_G3 import solve_SubProblem_G3
from get_model_single_1 import get_model_single
from concurrent.futures import ThreadPoolExecutor

def rou_apt(rou,yita_incr,yita_decr,miu_incr,miu_decr,dual,primal):
    if primal>miu_incr*dual:
        rou_new=rou*(1+yita_incr)
    elif dual>miu_decr*primal:
        rou_new=rou/(1+yita_decr)
    else:
        rou_new=rou
    
    return rou_new

def ADMM_DRMP_parallel_1(dataUC,model_single,model_master,y_min,y_max,GAP,TimeLimit,K,cx,BxT,R,G,ineq_st,eq_st,pz_num,G2,G3,V_G2,V_G3,G2Flag,G3Flag,AddPoint,AddCut,p_k,y_k,r,abs_tol,rel_tol):
    N=dataUC.N
    T=dataUC.T

    k=0
    epsilon_1=np.inf
    epsilon_2=np.inf
    
    z_k=np.zeros((N,T))# yi
    p_k_old=p_k.copy()

    #
    #
    #Due to the uncertainty of the review cycle, we have annotated the key parts of the code. If the paper is accepted, we will make it public.
    #
    #

    model_PI=get_model_single(dataUC,model_single,model_master,y_min,y_max,K,cx,BxT,R,G,ineq_st,eq_st,pz_num,AddPoint,AddCut,G2,G3,V_G2,V_G3,G2Flag,G3Flag)
    BxISO=[x/N for x in model_single[0].beq_c]

    while epsilon_2>tol_dul and epsilon_1>tol_pri:
        
        k+=1
        objval=0
        delta_G2 = [None] * N
        delta_G3 = [None] * N
        x=[]

        #
        #
        #Due to the uncertainty of the review cycle, we have annotated the key parts of the code. If the paper is accepted, we will make it public.
        #
        #

        
       
        print(f"[iter {k}] primal_res={epsilon_1:.2e}, dual_res={epsilon_2:.2e}, rho={r:.2e}")
        if epsilon_1<=tol_pri and epsilon_2<=tol_dul:
            M2=k
            break
        #print(y_k)
    
    delta_G2 = [d for d in delta_G2 if d is not None]
    delta_G3 = [d for d in delta_G3 if d is not None]
    delta_G2 = np.concatenate(delta_G2) if delta_G2 else np.array([])
    delta_G3 = np.concatenate(delta_G3) if delta_G3 else np.array([])

    return p_k,y_k,x,delta_G2,objval
