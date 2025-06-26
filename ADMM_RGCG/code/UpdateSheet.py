import pandas as pd
import openpyxl   #用于处理Excel文件

def UpdateSheet(file,TightFlag,i,DualFlag):
    ################################################## 读取excel中的数据并清空UB中的数据
    dfUB = pd.read_excel(file, sheet_name="UB", header=None, engine="openpyxl")
    dfUplift = pd.read_excel(file, sheet_name="Uplift", header=None, engine="openpyxl")

    if i == 0:
        j = 1 + TightFlag + DualFlag*3
        dfG = pd.read_excel(file, sheet_name="G", header=None, engine="openpyxl")
        dfG.iloc[1:, DualFlag*4:4+DualFlag*4] = None
    elif i == 1:
        j = 7 + TightFlag
    dfUB.iloc[2:, j] = None
    dfUplift.iloc[2:, j+1] = None

    ################################################## 删除原来的UB
    wb = openpyxl.load_workbook(file)  # 打开记录计算结果的工作簿
    wb.remove(wb["UB"])
    wb.remove(wb["Uplift"])
    if i == 0:
        wb.remove(wb["G"])
    wb.save(file)
    with pd.ExcelWriter(file, engine='openpyxl', mode="a") as writer:  # 将多个不同的dataframe导出到同一个Excel文件的不同Sheet页
        dfUB.to_excel(writer, sheet_name='UB', index=False, header=None)
        dfUplift.to_excel(writer, sheet_name='Uplift', index=False, header=None)
        if i == 0:
            dfG.to_excel(writer, sheet_name='G', index=False, header=None)