# 函数说明：机组集约束通用类。

class VCon:
    def __init__(self):
        self.Aineq = []  # 创建和初始化不等式约束左端项系数矩阵
        self.bineq = []  # 创建和初始化不等式约束右端项
        self.Aeq = []  # 创建和初始化等式约束左端项系数矩阵
        self.beq = []  # 创建和初始化等式约束右端项
        self.Aeq_c = []  # 创建和初始化耦合约束左端项系数矩阵
        self.beq_c = []  # 创建和初始化耦合约束右端项
        self.Aineq_c = []  # 创建和初始化耦合约束左端项系数矩阵
        self.bineq_c = []  # 创建和初始化耦合约束右端项
        self.lb = []  # 创建和初始化变量下界
        self.ub = []  # 创建和初始化变量上界
        self.f = []  # 创建和初始化目标函数一次项系数