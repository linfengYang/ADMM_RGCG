#求解定价子问题(pricing subproblem)

from GurobiSolve import GurobiSolve
from gurobipy import *
import numpy as np
import scipy.sparse as sp
import copy
from readdataUC import dataUC
from model_MP import produce_model

def SubProblem(model,r,GAP,TimeLimit):

    m=copy.copy(model)

    m.Aeq=m.Aeq_s
    m.Aineq=m.Aineq_s
    m.beq=m.beq_s
    m.bineq=m.bineq_s

    m.f=model.f-np.dot(r,m.Aeq_c.toarray())

    (x,m_k)=GurobiSolve('MIP',m,GAP,TimeLimit,0,0,GRB.MINIMIZE)
    return (x,m_k.ObjVal+np.dot(r,model.beq_c))

