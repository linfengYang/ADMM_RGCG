import numpy as np
import scipy.sparse as sp

def CreateV_G134(V,R,G,model_i,FLAG):
    V.lb.extend(model_i.lb)
    V.ub.extend(model_i.ub)
    V.bineq = np.append(V.bineq,model_i.bineq_s)

    if len(V.f) > 0:
        V.f = np.append(V.f,model_i.f)
    else:
        V.f = model_i.f

    increment = model_i.Aineq_s
    if FLAG == 3 and len(R) > 0:
        #转化成稀疏矩阵，方便高效处理大型稀疏矩阵
        Cut = sp.lil_matrix(R)
        #将 Cut 与 increment 对齐，确保它们列数一致（通过补充零矩阵来扩展）
        Cut = sp.hstack([Cut, sp.lil_matrix((Cut.shape[0], increment.shape[1] - Cut.shape[1]))], format='lil')
        #按竖直方向堆叠
        increment = sp.vstack([increment,Cut], format='lil')
        V.bineq = np.append(V.bineq,G)

    if V.Aineq == []:
        V.Aineq = increment
    else:
        V.Aineq = sp.block_diag((V.Aineq, increment), format='lil')

    V.beq = np.append(V.beq,model_i.beq_s)
    if V.Aeq == []:
        V.Aeq = model_i.Aeq_s
    else:
        #合并成一个块对角矩阵
        V.Aeq = sp.block_diag((V.Aeq, model_i.Aeq_s), format='lil')

    V.beq_c = model_i.beq_c
    if V.Aeq_c == []:
        V.Aeq_c = model_i.Aeq_c
    else:
        V.Aeq_c = sp.hstack((V.Aeq_c, model_i.Aeq_c), format='lil')

