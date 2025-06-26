import pandas as pd

def CreateExcel(template):
    data = {'period': ['', ''], 'CHP': ['YU', 'final'], 'CG1': ['2P', 'initial'], 'CG2': ['2P', 'final'],
            'CG3': ['TP', 'initial'], 'CG4': ['TP', 'final'], 'CG5': ['random', 'initial'], 'CG6': ['random', 'final'],
            'DCG1': ['2P', 'initial'], 'DCG2': ['2P', 'final'], 'DCG3': ['TP', 'initial'], 'DCG4': ['TP', 'final'],
            'DCG5': ['random', 'initial'], 'DCG6': ['random', 'final'], 'LM1': ['2P', 'initial'],
            'LM2': ['2P', 'final'], 'LM3': ['TP', 'initial'], 'LM4': ['TP', 'final'], 'LM5': ['random', 'initial'],
            'LM6': ['random', 'final'], 'ymin': ['', ''], 'ymax': ['', '']}
    price_sheet = pd.DataFrame(data)  # 工作表保存价格

    data = {'VAL': ['initial price'], 'CHP': ['YU'], 'CG1': ['2P'], 'CG2': ['TP'], 'CG3': ['random'], 'DCG1': ['2P'],
            'DCG2': ['TP'], 'DCG3': ['random'], 'LM1': ['2P'], 'LM2': ['TP'], 'LM3': ['random']}
    Uplift_sheet = pd.DataFrame(data)  # 工作表保存Uplift

    data = {'unit': [''], 'CG1': ['2P'], 'CG2': ['TP'], 'CG3': ['random'], 'DCG1': ['2P'], 'DCG2': ['TP'],
            'DCG3': ['random'], 'ifRamp': [''], 'M': ['']}
    KPoint_sheet = pd.DataFrame(data)  # 工作表保存K_i中点的个数

    data = {'unit': [''], 'CG1': ['2P'], 'CG2': ['TP'], 'CG3': ['random'], 'DCG1': ['2P'], 'DCG2': ['TP'],
            'DCG3': ['random'], 'ifRamp': [''], 'M': [''], 'sNum1': ['2P'], 'sNum2': ['TP']}
    RCut_sheet = pd.DataFrame(data)  # 工作表保存R_i中割平面的个数

    G_sheet = pd.DataFrame(columns=['G1', 'G2', 'G3', 'G4','DG1', 'DG2', 'DG3', 'DG4'])  # 工作表保存每个机组集中的机组索引号

    data = {'time': ['', 'initialization', 'solve', 'total'], 'CHP': ['YU', '', '', ''], 'CG1': ['2P', '', '', ''],
            'CG2': ['TP', '', '', ''], 'CG3': ['random', '', '', ''], 'DCG1': ['2P', '', '', ''],
            'DCG2': ['TP', '', '', ''], 'DCG3': ['random', '', '', ''], 'LM1': ['2P', '', '', ''],
            'LM2': ['TP', '', '', ''], 'LM3': ['random', '', '', '']}
    time_sheet = pd.DataFrame(data)  # 工作表保存求解时间

    data = {'IterateNum': [''], 'CG1': ['2P'], 'CG2': ['TP'], 'CG3': ['random'], 'DCG1': ['2P'], 'DCG2': ['TP'],
            'DCG3': ['random'], 'LM1': ['2P'], 'LM2': ['TP'], 'LM3': ['random']}
    iterate_sheet = pd.DataFrame(data)  # 工作表保存每次迭代所需的时间

    data = {'IterateNum': [''], 'CG1': ['2P'], 'CG2': ['TP'], 'CG3': ['random'], 'DCG1': ['2P'], 'DCG2': ['TP'],
            'DCG3': ['random'], 'LM1': ['2P'], 'LM2': ['TP'], 'LM3': ['random']}
    UB_sheet = pd.DataFrame(data)  # 工作表保存每次迭代所需的时间

    data = {'parameter': ['sigma', 'eps', 'beta', 'maxKPointNum', 'maxRCutNum', 'eta'], 'CG': ['', '', '', '', '', ''],
            'DCG': ['', '', '', '', '', ''], 'LM': ['', '', '', '', '', '']}
    parameter_sheet = pd.DataFrame(data)  # 工作表保存算法参数

    with pd.ExcelWriter(template, engine='openpyxl') as writer:  # 将多个不同的dataframe导出到同一个Excel文件的不同Sheet页
        price_sheet.to_excel(writer,sheet_name='price', index=False)
        Uplift_sheet.to_excel(writer,sheet_name='Uplift', index=False)
        KPoint_sheet.to_excel(writer, sheet_name='KPoint', index=False)
        RCut_sheet.to_excel(writer, sheet_name='RCut', index=False)
        G_sheet.to_excel(writer, sheet_name='G', index=False)
        time_sheet.to_excel(writer, sheet_name='time', index=False)
        iterate_sheet.to_excel(writer, sheet_name='iterate', index=False)
        UB_sheet.to_excel(writer, sheet_name='UB', index=False)
        parameter_sheet.to_excel(writer, sheet_name='parameter', index=False)
        workbook = writer.book

    return workbook