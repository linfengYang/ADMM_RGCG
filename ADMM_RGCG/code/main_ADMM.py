from gurobipy import *    
import numpy as np
from readdataUC import dataUC
from model_MP import produce_model
from GurobiSolve import GurobiSolve
import os
from RGCG_ADMM import RGCG
from RGCG_ADMM_parallel import RGCG_parallel
from ReadFolder import ReadFolder
from CreateExcel import CreateExcel
from expand import expand

    
J = 10                   # 目标函数线性化的分段段数
times_T = 1       # 时间拓展，1表示24，2表示2*24，...
times_Unit = 1       # 机组拓展，1表示1*N,2表示2*N,...
GAP = 1e-4#1e-5              # 下界MILP问题的误差，精度太低，最后的价格离凸包价格很远
gap = 'MGap1e4'    #下界MILP问题的误差
TimeLimit = 3600       # 求解终止时间
data = 2                # 数据集，分别取1，2，读取不同类型数据
mflag = 2               # 1表示MP-1模型,2表示MP-2模型,3表示MP-3模型
history = 1             # 1表示模型含历史状态，0表示模型不含历史状态
facet = 1               # 1表示只含facet不等式，0表示含全部不等式
PitFlag = 0               # 1表示最后输出变量pit
UitFlag = 0               # 1表示最后输出变量uit
miu = 1                    # 稳定项系数miu
Zflag = 0                  # 1表示子问题目标函数二次项含z，0表示子问题目标函数二次项不含z。z的维度等于UC模型单机组约束个数，大系统复杂模型的z会很长，大概率出现数值问题，所以Zflag最好取0
YZflag = 1                  # 1表示主问题目标函数含y,z，0表示主问题目标函数不含y,z，建议YZflag取1
DoubleFlag = 0         # 1表示使用邻近水平束稳定方法，0表示使用水平束稳定方法，2表示不用稳定化。只有Kelley算法能取2
ConFlag = 1     # 1表示用最少的约束，0表示可以增加适当量的约束
G1Flag = 0      # 1表示初始时G1里面有简单凸包机组
G2Flag = 1      # 1表示初始时所有机组都放在G2
G3Flag = 0      # 1表示初始时所有机组都放在G3
RelativeFlag = 'R'   # R表示收敛准则上下界使用相对误差，A表示收敛准则上下界使用绝对误差
CGap = 1e-4   # 收敛准则上下界使用的误差
Cgap = f'{RelativeFlag}Gap1e4'   # 收敛准则上下界使用的误差
boxFlag = 0 # boxFlag为1表示价格有上下界，为0表示价格无界
wflag = 2 # 1表示slave problem中只含q和phi的关系等式，2含uv，3含uvw，4含uvwtao，0表示都不含
DualFlag = 1   # 1表示解DRMP，0表示解RMP

workbook = CreateExcel(f'result_ADMM_200/template.xlsx')

file_num = 1
SpinFlag=0
boolean_MILP=1
QP=1
(file_list,file_path,file_num) = ReadFolder(data)

data_path=f'UC_AF/100_0_1_w.mod'
data_UC=dataUC()
data_UC.UC(data_path)
result_path=f'result_ADMM_200/data_{data}/_{50}index_{data_UC.N}unit_{data_UC.T}period'
if G1Flag:
    result_path+='_withG1'
elif G2Flag:
    result_path+='_allG2'
elif G3Flag:
    result_path+='_allG3'
else:
    result_path+='_noG1'
result_path += f'_{gap}_{Cgap}_time{TimeLimit}.xlsx'
result_path = os.path.join(os.getcwd(), result_path)
if os.path.exists(result_path) == 0:   #如果工作簿不存在，则创建新的工作簿
    workbook.save(result_path)  # 保存工作簿到文件夹result_UC_AF，文件名为算例名

(model, model_single) = produce_model(data_UC, 0, boolean_MILP, QP, J, SpinFlag)
(x_0, Gmodel) = GurobiSolve('MIP', model, 1e-3, TimeLimit, boolean_MILP, QP, GRB.MINIMIZE)  # 只是一个参照值，MIP精度不影响
print(Gmodel.ObjVal)
K = [[]] * data_UC.N  # K列表存储每个机组的点集
st = 0
for i in range(data_UC.N):  # 为G2中所有机组建立初始点集K，注意全零点不一定是可行点，比如初始为开机且还不能马上关机时
    ed = st + model_single[i].var_num
    K[i] = x_0[st:ed]
    st = ed
for TightFlag in range(0,1):  # 1表示用紧模型如'TP'来代替凸包，0表示用很松的'2P'模型来代替凸包，2表示初始价格随机，3表示直接用凸包模型
    if TightFlag == 3:
        (model, model_single) = produce_model(data_UC, 3, boolean_MILP, QP, J, SpinFlag)
    for i in [0]:#range(3,4):
        if TightFlag == 3 and i > 0:
            break
        if i == 0:  
            
            # RGCG(data_UC, 1, 1, J, 0, history, facet, mflag, PitFlag, UitFlag,
            #      GAP, TimeLimit,TightFlag, boxFlag, miu, DoubleFlag, Gmodel.ObjVal, model,
            #      model_single, G1Flag, G2Flag, G3Flag, RelativeFlag, CGap, K, wflag, DualFlag)
            
            RGCG_parallel(data_UC, boolean_MILP, QP, J, SpinFlag, history, facet, mflag, PitFlag, UitFlag,
                    GAP, TimeLimit,TightFlag, boxFlag, miu, DoubleFlag, Gmodel.ObjVal, model,
                    model_single, G1Flag, G2Flag, G3Flag, RelativeFlag, CGap, K, wflag, DualFlag,result_path)

print('Ending')                