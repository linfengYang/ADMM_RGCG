import numpy as np
import scipy.sparse as sp
from gurobipy import *
from UCModel import UCModel
from readdataUC import dataUC
from model_2P_single import model_2P_single

def produce_model(dataUC,TightFlag,boolean_MILP,QP,J,SpinFlag):
    ################################################## 将data_UC中的部分数据转换成int类型
    dataUC.t_on = np.int16(dataUC.t_on)  # 机组最小开机时间
    dataUC.t_off = np.int16(dataUC.t_off)  # 机组最小停机时间

    if sum(dataUC.CostFlag) > 0:    # 1表示考虑冷热启动成本,0表示启动成本固定
        dataUC.time_cold = np.int16(dataUC.time_cold)  # 火电机组冷启动时间

    dataUC.time_init = np.int16(dataUC.time_init)  # 机组在初始状态前已经开机（正）/停机的时间（负）

    model = UCModel()
    model_single = []
    
    for i in range(dataUC.N):
        if TightFlag == 0:  # 0表示用很松的'2P'模型
            model_i = model_2P_single(dataUC, boolean_MILP, QP, J, SpinFlag, i)

        # 变量上下界
        model.lb.extend(model_i.lb)
        model.ub.extend(model_i.ub)

        # 变量类型
        model.vtype.extend(model_i.vtype)
        model.var_num = model.var_num + model_i.var_num
        model.tao_sum = model.tao_sum + model_i.tao_sum

        # 目标函数 objective
        if QP and boolean_MILP != 1:  # 目标函数线是二次的且不线性化
            if model.H == []:
                model.H = model_i.H
            else:
                model.H = sp.block_diag((model.H,model_i.H),format='lil')

        if model.f is []:
            model.f = model_i.f
        else:
            model.f = np.append(model.f, model_i.f)

        # 形成完整的功率平衡的左端项
        if model.Aeq_c == []:
            model.Aeq_c = model_i.Aeq_c
        else:
            model.Aeq_c = sp.hstack([model.Aeq_c, model_i.Aeq_c], format='lil')

        # 形成完整的备用约束的左端项
        if SpinFlag:  # 1表示考虑旋转备用,0表示不考虑
            if model.Aineq_c == []:
                model.Aineq_c = model_i.Aineq_c
            else:
                model.Aineq_c = sp.hstack([model.Aineq_c,model_i.Aineq_c],format='lil')

        # 形成完整的单机组不等式约束的左端项
        if model.Aineq_s == []:
            model.Aineq_s = model_i.Aineq_s
        else:
            model.Aineq_s = sp.block_diag((model.Aineq_s,model_i.Aineq_s),format='lil')

        # 形成完整的单机组不等式约束的右端项
        model.bineq_s = np.append(model.bineq_s,model_i.bineq_s)

        # 形成完整的单机组等式约束的左端项
        if model.Aeq_s == []:
            model.Aeq_s = model_i.Aeq_s
        else:
            model.Aeq_s = sp.block_diag((model.Aeq_s,model_i.Aeq_s),format='lil')

        # 形成完整的单机组等式约束的右端项
        model.beq_s = np.append(model.beq_s, model_i.beq_s)

        model_i.Aeq = model_i.Aeq_s
        model_i.beq = model_i.beq_s
        model_i.Aineq = model_i.Aineq_s
        model_i.bineq = model_i.bineq_s
        model_i.beq_c = np.array(dataUC.PD)
        model_single.append(model_i)

    # 形成完整的功率平衡和备用约束的右端项
    if SpinFlag:  # 1表示考虑旋转备用,0表示不考虑
        model.bineq_c = -np.array(dataUC.PD) - np.array(dataUC.reserve)
        model.Aineq = sp.vstack([model.Aineq_s, model.Aineq_c], format='lil')
        model.bineq = np.append(model.bineq_s,model.bineq_c)
    else:
        model.Aineq = model.Aineq_s
        model.bineq = np.array(model.bineq_s)

    model.beq_c = np.array(dataUC.PD)

    model.Aeq = sp.vstack([model.Aeq_c, model.Aeq_s], format='lil')
    model.beq = np.append(model.beq_c,model.beq_s)
    
    return (model,model_single)


