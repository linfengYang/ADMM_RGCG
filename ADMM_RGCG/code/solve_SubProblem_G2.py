from GurobiSolve import GurobiSolve
from gurobipy import *
import scipy.sparse as sp
import numpy as np
from GModel import GModel

def solve_SubProblem_G2(tol_model,obj_c,Q,GAP,TimeLimit):

    model=GModel()
    model.f=obj_c
    model.H=Q
    model.lb=tol_model.lb
    model.ub=tol_model.ub
    model.Aineq=tol_model.Aineq
    model.bineq=tol_model.bineq
    model.vtype=tol_model.vtype

    (ydelta,m)=GurobiSolve('Relax', model, GAP, TimeLimit, 0, 1, GRB.MAXIMIZE)
    return ydelta,m.ObjVal

