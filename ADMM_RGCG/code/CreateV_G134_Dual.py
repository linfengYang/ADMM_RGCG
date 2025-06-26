import numpy as np
import scipy.sparse as sp

def CreateV_G134_Dual(V,R,G,model_i,FLAG):

    V.lb.extend([-np.inf]*model_i.Aeq_s.shape[0])
    V.ub.extend([np.inf]*model_i.Aeq_s.shape[0])
    V.lb.extend([-np.inf] * model_i.Aineq_s.shape[0])
    V.ub.extend([0] * model_i.Aineq_s.shape[0])

    increment_b = np.append(model_i.beq_s, model_i.bineq_s)
    if FLAG == 3 and len(G) > 0:
        increment_b = np.append(increment_b, np.array(G))
    if len(V.f) > 0:
        V.f = np.append(V.f, increment_b)
    else:
        V.f = increment_b

    increment = sp.hstack([model_i.Aeq_s.T, model_i.Aineq_s.T], format='lil')  # 拼接单机组约束
    if FLAG == 3 and len(R) > 0:
        Cut = sp.lil_matrix(R).T
        Cut = sp.vstack([Cut, sp.lil_matrix((increment.shape[0]-Cut.shape[0],Cut.shape[1]))], format='lil')
        increment = sp.hstack([increment, Cut], format='lil')  # 拼接单机组约束
        V.lb.extend([-np.inf] * Cut.shape[1])
        V.ub.extend([0] * Cut.shape[1])

    V.bineq = np.append(V.bineq,model_i.f[model_i.qphi_num:])
    if V.Aineq == []:
        V.Aineq = increment[model_i.qphi_num:,:]
    else:
        V.Aineq = sp.block_diag((V.Aineq, increment[model_i.qphi_num:,:]), format='lil')

    V.beq = np.append(V.beq,model_i.f[:model_i.qphi_num])
    if V.Aeq == []:
        V.Aeq = increment[:model_i.qphi_num,:]
    else:
        V.Aeq = sp.block_diag((V.Aeq, increment[:model_i.qphi_num,:]), format='lil')

    if V.Aeq_c == []:
        V.Aeq_c = model_i.Aeq_c.T[:model_i.qphi_num,:]
    else:
        V.Aeq_c = sp.vstack((V.Aeq_c, model_i.Aeq_c.T[:model_i.qphi_num,:]), format='lil')

    if V.Aineq_c == []:
        V.Aineq_c = model_i.Aeq_c.T[model_i.qphi_num:,:]
    else:
        V.Aineq_c = sp.vstack((V.Aineq_c, model_i.Aeq_c.T[model_i.qphi_num:,:]), format='lil')

