# expand 扩展机组数据
# times_T为扩展时间，24时间段的倍数，1指24时段，2指24*2时段……
# times_Unit为扩展机组个数，1指当前数据文件中机组个数的一倍,即N*1，2指N*2……

import numpy as np

def expand(dataUC,times_T,times_Unit):
    if times_T > 1:  # Extend time period
        dataUC.T *= times_T
        dataUC.PD = np.tile(dataUC.PD, times_T)
        dataUC.reserve = np.tile(dataUC.reserve, times_T)

    if times_T < 1:  # Shrink time period
        dataUC.T *= times_T
        dataUC.PD = dataUC.PD[:dataUC.T, :]
        dataUC.reserve = dataUC.Spin[:dataUC.T, :]

    if times_Unit > 1:  # Extend units
        dataUC.PD *= times_Unit
        dataUC.reserve *= times_Unit
        dataUC.N *= times_Unit

        dataUC.alpha = np.tile(dataUC.alpha, (times_Unit,1)).flatten('F')
        dataUC.beta = np.tile(dataUC.beta, (times_Unit,1)).flatten('F')
        dataUC.gamma = np.tile(dataUC.gamma, (times_Unit,1)).flatten('F')

        dataUC.p_low = np.tile(dataUC.p_low, (times_Unit,1)).flatten('F')
        dataUC.p_up = np.tile(dataUC.p_up, (times_Unit,1)).flatten('F')
        dataUC.ramp_down = np.tile(dataUC.ramp_down, (times_Unit,1)).flatten('F')
        dataUC.ramp_up = np.tile(dataUC.ramp_up, (times_Unit,1)).flatten('F')
        dataUC.ramp_on = np.tile(dataUC.ramp_on, (times_Unit,1)).flatten('F')
        dataUC.ramp_off = np.tile(dataUC.ramp_off, (times_Unit,1)).flatten('F')

        dataUC.t_on = np.tile(dataUC.t_on, (times_Unit,1)).flatten('F')
        dataUC.t_off = np.tile(dataUC.t_off, (times_Unit,1)).flatten('F')
        dataUC.cost_cold = np.tile(dataUC.cost_cold, (times_Unit,1)).flatten('F')
        dataUC.cost_hot = np.tile(dataUC.cost_hot, (times_Unit,1)).flatten('F')
        dataUC.StartCost = np.tile(dataUC.StartCost, (times_Unit,1)).flatten('F')
        dataUC.time_cold = np.tile(dataUC.time_cold, (times_Unit,1)).flatten('F')

        dataUC.time_init = np.tile(dataUC.time_init, (times_Unit,1)).flatten('F')
        dataUC.p_init = np.tile(dataUC.p_init, (times_Unit,1)).flatten('F')
        dataUC.u0 = np.tile(dataUC.u0, (times_Unit,1)).flatten('F')

    return dataUC