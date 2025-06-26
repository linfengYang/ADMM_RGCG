# 函数说明：用GUROBI求解优化问题。

from gurobipy import *     # 在Python中调用gurobi求解包
import numpy as np
import pandas as pd
#from compare_matrix import compare_matrix
import scipy.sparse as sp
import traceback

def GurobiSolve(problem,model,GAP,TimeLimit,boolean_MILP,QP,sense):

    #problem:求松弛还是原问题；model:构造后的模型
    #GAP:间隔；Time:时间限制；boolean:是否线性化
    #QP:目标函数为二次，sense：最大化或者最小化
    # print("type(model.vtype):", type(model.vtype))

    Gmodel = Model()  # 创建模型
    # 设置参数
    Gmodel.setParam('OutputFlag', 0)           # 0表示命令行窗口不显示求解过程，1表示显示过程
    Gmodel.setParam('MIPGap', GAP)  # 求解精度
    Gmodel.setParam('TimeLimit', TimeLimit)    # 求解时间限制
    # if problem == 'Relax':
    #     # 案例9,46全G2要设置这个参数
    #     Gmodel.setParam('Method', 2)  # 求解方法
    #     #案例16全G2要设置这个参数
    #     Gmodel.setParam('DualReductions', 0)  # 显示求解详细状态：不可行/无界
    # Gmodel.setParam('BarHomogeneous', 1)    #
    # Gmodel.setParam('NumericFocus', 2)  # 控制代码尝试检测和管理数值问题的程度
    # Gmodel.setParam('Presolve', 0)  # 控制代码尝试检测和管理数值问题的程度
    #Gmodel.setParam('BarConvTol', 1e-12) # Barrier convergence tolerance 默认1e-8

   
    if problem == 'Relax':
        vtype = [GRB.CONTINUOUS] * len(model.vtype)
    else:
        vtype = model.vtype
    
    # 添加变量
    x = Gmodel.addMVar((np.size(model.f),), model.lb, model.ub, 0, vtype, name="x")
    # 添加约束
    if model.Aeq != []:
        Gmodel.addConstr(model.Aeq @ x == model.beq, name="equalities")
    if model.Aineq != []:
        Gmodel.addConstr(model.Aineq @ x <= model.bineq, name="inequalities")

    # 设定目标函数
    if QP and boolean_MILP != 1:  # QP=1表示目标函数是二次的,boolean_MILP=1表示对目标函数线性化
        Gmodel.setMObjective(model.H, model.f, 0.0, None, None, None, sense)
    else:
        Gmodel.setMObjective(None, model.f, 0.0, None, None, None, sense)

    # Optimize model
    Gmodel.optimize()

    # 把模型写到文件里
    # Gmodel.write("model.lp")
    if Gmodel.Status != 2:
        Gmodel.computeIIS()
        Gmodel.write('model.ilp')
    #return (x.X, Gmodel)
    if Gmodel.Status == 12:
        return (['NumericTrouble'] , Gmodel)
    elif Gmodel.Status == 3:
        return (['infeasible'], Gmodel)
    elif Gmodel.Status == 5:
        return (['unbounded'], Gmodel)
    else:
        return (x.X,Gmodel)