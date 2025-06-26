#函数说明：2P-CO模型的建模

import numpy as np
import scipy.sparse as sp
from UCModel import UCModel
from gurobipy import *     

def model_2P_single(dataUC,boolean_MILP,QP,D,SpinFlag,i):
    
    model_i=UCModel()

    U=max(0,min(dataUC.T,dataUC.u0[i]*(dataUC.t_on[i]-dataUC.time_init[i])))
    L=max(0, min(dataUC.T, (1 - dataUC.u0[i]) * (dataUC.t_off[i] + dataUC.time_init[i])))

    # 变量排序：Pit，zit，Sit，uit， sit，dit
    # 连续变量个数
    model_i.q_num = dataUC.T
    if boolean_MILP:  # 目标函数线性化
        model_i.phi_num = model_i.q_num
    else:
        model_i.phi_num = 0
    model_i.qphi_num = model_i.q_num + model_i.phi_num
    ConVar = model_i.qphi_num  # 连续变量个数
    if dataUC.CostFlag[i]:  # 1表示考虑冷热启动成本, 0表示启动成本固定
        ConVar += dataUC.T  # 增加连续变量SitWan
    model_i.var_num = int(ConVar + 3 * dataUC.T)

    #(4)式
    model_i.Aeq_c = sp.lil_matrix((dataUC.T, model_i.var_num))
    model_i.Aeq_c[:, : model_i.q_num] = sp.identity(model_i.q_num,format='lil') # pit

    #(5)式
    if SpinFlag:  # 1表示考虑旋转备用,0表示不考虑
        model_i.Aineq_c = sp.lil_matrix((dataUC.T, model_i.var_num))
        model_i.Aineq_c[:, ConVar : ConVar + dataUC.T] = -1 * dataUC.p_up[i] * sp.identity(dataUC.T,format='lil')

    #(3)式
    A_generation_lower = sp.lil_matrix((dataUC.T, model_i.var_num))
    b_generation_lower = [0] * dataUC.T
    A_generation_lower[:, : model_i.q_num] = -1 * sp.identity(model_i.q_num, format='lil')  # Pit
    A_generation_lower[:, ConVar: ConVar + dataUC.T] = dataUC.p_low[i] * sp.identity(dataUC.T, format='lil')  # uit

    A_generation_upper = sp.lil_matrix((dataUC.T, model_i.var_num))
    b_generation_upper = [0] * dataUC.T
    A_generation_upper[:, : model_i.q_num] = sp.identity(model_i.q_num, format='lil')  # Pit
    A_generation_upper[:, ConVar: ConVar + dataUC.T] = -1 * dataUC.p_up[i] * sp.identity(dataUC.T, format='lil')  # uit

    #(10)式
    A_initial_status = sp.lil_matrix((U + L,model_i.var_num))
    A_initial_status[: U + L, ConVar : ConVar + U + L] = sp.identity(U + L,format='lil')
    b_initial_status = [dataUC.u0[i]] * (U + L)
    # vit=0，求slave problem时这个约束很必要，为了和凸包模型的tao对应上，而且还能使松弛模型变紧
    if dataUC.u0[i]:  # 机组初始为开
        A_initial_status_v = sp.lil_matrix((U+dataUC.t_off[i], model_i.var_num))
        A_initial_status_v[:, ConVar+dataUC.T: ConVar+dataUC.T + U + dataUC.t_off[i]] = sp.identity(U + dataUC.t_off[i], format='lil')   #sit
        b_initial_status_v = [0] * (U + dataUC.t_off[i])
        A_initial_status = sp.vstack([A_initial_status,A_initial_status_v],format='lil')
        b_initial_status = b_initial_status + b_initial_status_v
    elif dataUC.u0[i] == 0 and L > 0:
        A_initial_status_v = sp.lil_matrix((L, model_i.var_num))
        A_initial_status_v[:,ConVar + dataUC.T: ConVar + dataUC.T + L] = sp.identity(L,format='lil')  # vit
        b_initial_status_v = [0] * L
        A_initial_status = sp.vstack([A_initial_status, A_initial_status_v], format='lil')
        b_initial_status = b_initial_status + b_initial_status_v

    #(12)式
    beq_state = []
    Aeq_state = sp.lil_matrix((dataUC.T,model_i.var_num))
    Aeq_state[:, ConVar: ConVar + dataUC.T] = sp.identity(dataUC.T,format='lil') - sp.diags(np.ones(dataUC.T - 1),-1)   # uit
    Aeq_state[:, ConVar + dataUC.T: ConVar + 2 * dataUC.T] = -1 * sp.identity(dataUC.T,format='lil')   # vit
    Aeq_state[:, ConVar + 2 * dataUC.T: ConVar + 3 * dataUC.T] = sp.identity(dataUC.T,format='lil')   # wit
    beq_state.extend([dataUC.u0[i]] + [0] * (dataUC.T - 1))

    # (13)(14)式
    # 最小开机时间约束
    A_min_up_time = []
    b_min_up_time = []
    for t in range(U + 1,dataUC.T + 1):
        min_up_time = sp.lil_matrix((1, model_i.var_num))
        min_up_time[0, ConVar + t - 1] = -1  # uit
        # sit
        omega = max(0, t - dataUC.t_on[i]) + 1
        for r in range(omega,t + 1):
            min_up_time[0, ConVar + dataUC.T + r - 1] = 1
        if min_up_time.data.any():
            if A_min_up_time == []:
                A_min_up_time = min_up_time
            else:
                A_min_up_time = sp.vstack([A_min_up_time,min_up_time], format='lil')
            b_min_up_time.append(0)

    # 最小关机时间约束
    A_min_down_time = []
    b_min_down_time = []
    for t in range(L + 1, dataUC.T + 1):
        min_down_time = sp.lil_matrix((1,model_i.var_num))
        min_down_time[0, ConVar + t - 1] = 1  # uit
        # wit
        omega = max(0, t - dataUC.t_off[i]) + 1
        for r in range(omega, t + 1):
            min_down_time[0, ConVar + 2 * dataUC.T + r - 1] = 1

        if min_down_time.data.any():
            if A_min_down_time == []:
                A_min_down_time = min_down_time
            else:
                A_min_down_time = sp.vstack([A_min_down_time,min_down_time], format='lil')
            b_min_down_time.append(1)

    #(19)(20)式
    if dataUC.CostFlag[i]:  # 1表示考虑冷热启动成本, 0表示启动成本固定
        b_start_cost = []
        A_start_cost = sp.lil_matrix((dataUC.T, model_i.var_num))
        for t in range(1,dataUC.T + 1):
            A_start_cost[t - 1, model_i.qphi_num + t - 1] = -1  # SitWan
            A_start_cost[t - 1, ConVar + dataUC.T + t - 1] = dataUC.cost_cold[i] - dataUC.cost_hot[i]  # vit
            # wit
            for r in range(max(1,t - dataUC.t_off[i] - dataUC.time_cold[i]),t):
                A_start_cost[t - 1, ConVar + 2 * dataUC.T + r - 1] = dataUC.cost_hot[i] - dataUC.cost_cold[i]

            # 启动成本约束右端项
            if (t - dataUC.t_off[i] - dataUC.time_cold[i]) <= 0 and max(0,-dataUC.time_init[i]) < abs(t - dataUC.t_off[i] - dataUC.time_cold[i] - 1) + 1:  # f_init = 1
                b_start_cost.append(dataUC.cost_cold[i] - dataUC.cost_hot[i])
            else:     # f_init = 0
                b_start_cost.append(0)

    #(17)(18)式/(15)(16)式
    if dataUC.iframp[i]:  # dataUC.iframp[i]=1表示机组i考虑爬坡约束, 0表示否
        # p(t) - p(t-1) <= u(t-1)Pup + v(t)Pstart  t从1到T
        A_ramp_up = sp.lil_matrix((dataUC.T, model_i.var_num))
        A_ramp_up[:, : model_i.q_num] = -1 * sp.diags(np.ones(model_i.q_num - 1), -1, format='lil') + sp.identity(model_i.q_num, format='lil')  # Pit
        A_ramp_up[:, ConVar: ConVar + dataUC.T] = -1 * dataUC.ramp_up[i] * sp.diags(np.ones(dataUC.T - 1), -1, format='lil')  # uit
        A_ramp_up[:, ConVar + dataUC.T: ConVar + 2 * dataUC.T] = -1 * dataUC.ramp_on[i] * sp.identity(dataUC.T, format='lil')  # vit
        b_ramp_up = [0] * dataUC.T
        b_ramp_up[0] = dataUC.p_init[i] + dataUC.u0[i] * dataUC.ramp_up[i]

        # p(t-1) - p(t) <= u(t)Pdown + w(t)Pshut  t从1到T
        A_ramp_down = sp.lil_matrix((dataUC.T, model_i.var_num))
        A_ramp_down[:, : model_i.q_num] = sp.diags(np.ones(model_i.q_num - 1), -1, format='lil') - sp.identity(model_i.q_num,format='lil')  # Pit
        A_ramp_down[:, ConVar: ConVar + dataUC.T] = -1 * dataUC.ramp_down[i] * sp.identity(dataUC.T, format='lil')  # uit
        A_ramp_down[:, ConVar + 2 * dataUC.T: model_i.var_num] = -1 * dataUC.ramp_off[i] * sp.identity(dataUC.T, format='lil')  # wit
        b_ramp_down = [0] * dataUC.T
        b_ramp_down[0] = -dataUC.p_init[i]

    #目标函数线性化
    if boolean_MILP == 1:  # 1表示目标函数线性化，对模型的目标函数进行线性化处理
        Aineq_lean = sp.lil_matrix((0, model_i.var_num))
        bineq_lean = []
        a = np.zeros(D + 1)
        b = np.zeros(D + 1)
        for j in range(D + 1):
            pil = dataUC.p_low[i] + j * (dataUC.p_up[i] - dataUC.p_low[i]) / D
            a[j] = 2 * dataUC.gamma[i] * pil + dataUC.beta[i]
            b[j] = dataUC.alpha[i] - dataUC.gamma[i] * pil * pil
            gradiant = sp.lil_matrix((dataUC.T, model_i.var_num))  # 新增的不等式约束
            gradiant[:, : model_i.q_num] = a[j] * sp.identity(model_i.q_num, format='lil') # Pit
            gradiant[:, ConVar: ConVar + dataUC.T] = b[j] * sp.identity(dataUC.T, format='lil') # uit
            gradiant[:, model_i.q_num: model_i.qphi_num] = -1 * sp.identity(model_i.q_num, format='lil') # zit
            Aineq_lean = sp.vstack([Aineq_lean, gradiant], format='lil')
            bineq_lean += [0] * model_i.q_num
    
    #拼约束矩阵
    model_i.Aeq_s = sp.vstack([A_initial_status,Aeq_state], format='lil')
    model_i.beq_s = b_initial_status + beq_state
    
    model_i.Aineq_s = sp.vstack([A_min_up_time,A_min_down_time,A_generation_upper,A_generation_lower], format='lil')
    model_i.bineq_s = b_min_up_time + b_min_down_time + b_generation_upper + b_generation_lower

    if dataUC.CostFlag[i]:  # 1表示考虑冷热启动成本, 0表示启动成本固定
        model_i.Aineq_s = sp.vstack([model_i.Aineq_s, A_start_cost], format='lil')
        model_i.bineq_s = model_i.bineq_s + b_start_cost
    if dataUC.iframp[i]:  # 1表示考虑爬坡约束, 0表示否
        model_i.Aineq_s = sp.vstack([model_i.Aineq_s, A_ramp_up, A_ramp_down], format='lil')
        model_i.bineq_s = model_i.bineq_s + b_ramp_up + b_ramp_down
    if boolean_MILP:
        model_i.Aineq_s = sp.vstack([model_i.Aineq_s, Aineq_lean], format='lil')
        model_i.bineq_s = model_i.bineq_s + bineq_lean

    #目标函数
    model_i.f = np.zeros(model_i.var_num)
    if boolean_MILP:  # 目标函数线性化
        model_i.f[model_i.q_num: model_i.qphi_num] = np.ones(model_i.phi_num)  # zit弯弯
    else:  # 目标函数线是二次的且不线性化或目标函数本就是线性的
        # q一次项
        model_i.f[: model_i.q_num] = dataUC.beta[i] * np.ones(model_i.q_num)  # pit
        # q二次项
        if QP:
            model_i.H = sp.lil_matrix((model_i.var_num, model_i.var_num))
            model_i.H[: model_i.q_num, : model_i.q_num] = dataUC.gamma[i] * sp.identity(model_i.q_num, format='lil')  # pit
        model_i.f[ConVar: ConVar + dataUC.T] = dataUC.alpha[i] * np.ones(dataUC.T)  # uit

    # 启动成本
    if dataUC.CostFlag[i]:  # 1表示考虑冷热启动成本, 0表示启动成本固定
        model_i.f[model_i.qphi_num: ConVar] = np.ones(dataUC.T)  # Sit弯弯
    if dataUC.CostFlag[i]:  # 1表示考虑冷热启动成本, 0表示启动成本固定
        model_i.f[ConVar + dataUC.T: ConVar + 2 * dataUC.T] = dataUC.cost_hot[i] * np.ones(dataUC.T)  # vit
    else:
        model_i.f[ConVar + dataUC.T: ConVar + 2 * dataUC.T] = dataUC.StartCost[i] * np.ones(dataUC.T)  # vit

    model_i.lb = [0] * model_i.var_num  # Sit弯弯,uit,vit,wit
    model_i.ub = [np.inf] * model_i.var_num  # uit,vit,wit
    model_i.lb[: model_i.qphi_num] = [-1 * np.inf] * model_i.qphi_num
    # model_i.lb[:ConVar]=[-1*np.inf]*ConVar

    model_i.vtype = [GRB.BINARY] * model_i.var_num  # uit,vit,wit
    model_i.vtype[: ConVar] = [GRB.CONTINUOUS] * ConVar  # pit,zit,Sit弯弯

    model_i.bineq_s = np.array(model_i.bineq_s)
    model_i.beq_s = np.array(model_i.beq_s)
    return model_i

    
