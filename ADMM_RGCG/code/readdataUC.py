import os
import numpy as np

class dataUC:
    
    def UC(self,pathandname):
        with open(pathandname) as f:
            #忽略第一行
            f.readline()
            #读取第二行数据
            self.T=int(f.readline().split()[1])
            #读取第三行数据
            self.N=int(f.readline().split()[1])
            #忽略第4-10行数据
            for _ in range(7):
                f.readline()
            #读取第11行数据
            pd=f.readline()
            for each in pd.split():
                self.PD.append(float(each))
            # self.PD=list(f.readline().split())
            # self.PD=[float(_)for _ in self.PD]
            #忽略第12行数据
            f.readline()
            #读取第13行数据
            rt = f.readline()
            for each in rt.split():
                self.reserve.append(float(each))
            #忽略第14行数据
            f.readline()
            #读取机组参数
            unitparams=[]
            for _ in range(self.N):
                unitparams.append(f.readline().split())
                temp=f.readline()
                self.ramp_up.append(float(temp.split()[1]))
                self.ramp_down.append(float(temp.split()[2]))
            
            self.alpha=[float(_[3])for _ in unitparams]
            self.beta=[float(_[2])for _ in unitparams]
            self.gamma=[float(_[1])for _ in unitparams]

            #最小出力
            self.p_low=[float(_[4])for _ in unitparams]
            #最大出力
            self.p_up=[float(_[5])for _ in unitparams]
            #初始运行时间
            self.time_init=[int(float(_[6]))for _ in unitparams]
            #初始出力
            self.p_init=[int(float(_[15]))for _ in unitparams]
            #最小开机时间
            self.t_on=[int(float(_[7]))for _ in unitparams]
            #最小停机时间
            self.t_off=[int(float(_[8]))for _ in unitparams]
            #热启动成本
            self.cost_hot=[float(_[13])for _ in unitparams]
            self.PD=np.array(self.PD)
            self.reserve=np.array(self.PD)
            if "_std" in pathandname:
                #冷启动成本
                if "5_std" in pathandname:
                    self.cost_cold=[1*_ for _ in self.cost_hot]
                else:
                    self.cost_cold=[2*_ for _ in self.cost_hot]
                #冷却时间
                self.time_cold=[int(float(_[16]))for _ in unitparams]
            else:
                self.cost_cold=[1*_ for _ in self.cost_hot]
                self.time_cold=[1 for _ in range(self.N)]
            
            #开机爬坡
            self.ramp_on=self.p_low
            #停机爬坡
            self.ramp_off=self.p_low
            #u0
            self.u0=[1 if _>0 else 0 for _ in self.p_init]


            self.StartCost=self.cost_hot
            self.iframp=np.ones(self.N)
            self.CostFlag=np.ones(self.N)

            if "8_std" in pathandname:
                temp=[0.71, 0.65, 0.62, 0.6, 0.58, 0.58, 0.6, 0.64,
                        0.73, 0.8, 0.82, 0.83, 0.82, 0.8, 0.79, 0.79,
                        0.83, 0.91, 0.9, 0.88, 0.85, 0.84, 0.79, 0.74]
                
                self.PD=[sum(self.p_up)*_ for _ in temp]
                self.reverse=[_*0.03 for _ in self.PD]
        
        f.close()


    def __init__(self):

        self.T = 0
        self.N = 0
        self.PD = []
        self.reserve = []
        self.ramp_up = []
        self.ramp_down = []
        # 成本二次函数系数
        self.alpha = []
        self.beta = []
        self.gamma = []
        # 发电功率下限
        self.p_low = []
        # 发电功率上限
        self.p_up = []
        
        self.time_init = []
        self.p_init = []
        self.t_on = []
        self.t_off = []
        # 热启动费用
        self.cost_hot = []
        # 冷启动费用
        self.cost_cold = []
        self.time_cold = []
        # 开机爬坡
        self.ramp_on = []
        # 停机爬坡
        self.ramp_off = []
        # 机组时刻 0 的状态
        self.u0 = []
        self.StartCost = []  # 固定的启动费用
        self.iframp = []
        self.CostFlag = []
        #self.UC(pathandname)


# if __name__ == "__main__":
#    filename=r'UC_AF/10_std.mod'
#    data=dataUC(filename)
#    print(data)
