# 函数说明：模型通用类。
class GModel:
    def __init__(self):
        self.Aineq = []  # 创建和初始化不等式约束左端项系数矩阵
        self.bineq = []  # 创建和初始化不等式约束右端项
        self.Aeq = []  # 创建和初始化等式约束左端项系数矩阵
        self.beq = []  # 创建和初始化等式约束右端项
        self.lb = []  # 创建和初始化变量下界
        self.ub = []  # 创建和初始化变量上界
        self.vtype = []  # 创建和初始化变量类型
        self.H = []  # 创建和初始化目标函数二次项系数矩阵
        self.f = []  # 创建和初始化目标函数一次项系数