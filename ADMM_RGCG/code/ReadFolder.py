import os

def ReadFolder(data):
    cwd = os.getcwd()    # 获取当前工作目录
    new_folder = 'UC_AF'   # 当前工作目录下的子文件夹
    file_path = os.path.join(cwd, new_folder)
    dir_list = os.listdir(file_path)
    if data == 1:
        file_list = [file for file in dir_list if 'c' in file]
    else:
        file_list = [file for file in dir_list if 'w' in file]
    file_num = len(file_list)
    return (file_list,file_path,file_num)