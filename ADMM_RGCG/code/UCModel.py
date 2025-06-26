# 函数说明：UC模型通用类。

class UCModel:
    def __init__(self):
        self.Aineq_c = []  # 创建和初始化耦合不等式约束左端项系数矩阵
        self.bineq_c = []  # 创建和初始化耦合不等式约束右端项
        self.Aeq_c = []  # 创建和初始化耦合等式约束左端项系数矩阵
        self.beq_c = []  # 创建和初始化耦合等式约束右端项
        self.Aineq_s = []  # 创建和初始化单机组不等式约束左端项系数矩阵
        self.bineq_s = []  # 创建和初始化单机组不等式约束右端项
        self.Aeq_s = []  # 创建和初始化单机组等式约束左端项系数矩阵
        self.beq_s = []  # 创建和初始化单机组等式约束右端项
        self.lb = []  # 创建和初始化变量下界
        self.ub = []  # 创建和初始化变量上界
        self.vtype = []  # 创建和初始化变量类型
        self.H = []  # 创建和初始化目标函数二次项系数矩阵
        self.f = []  # 创建和初始化目标函数一次项系数
        self.var_num = 0  # 模型的变量个数
        self.tao_sum = 0  # 模型的变量tao个数
        self.q_num = 0  # 模型的变量q的个数
        self.phi_num = 0  # 模型的变量phi的个数
        self.qphi_num = 0  # 模型的变量q和phi的总个数
        self.Aeq_pzuvw = []  # 用凸包模型变量表示紧模型的系数矩阵
        # self.Aeq_qp = []  # 用变量q表示pit的系数矩阵
        # self.Aeq_phiz = []  # 用变量phi表示zit的系数矩阵
        # self.Aeq_xyu = []  # 用变量x,y表示uit的系数矩阵
        # self.Aeq_xyv = []  # 用变量x,y表示vit的系数矩阵
        # self.Aeq_xyw = []  # 用变量x,y表示wit的系数矩阵
        # self.Aeq_xytao = []  # 用变量x,y表示taoit的系数矩阵
        self.theta_lo = []  # 模型的变量w的索引号
        self.y_lo = []  # 模型的变量z的索引号
