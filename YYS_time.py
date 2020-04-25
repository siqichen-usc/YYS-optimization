#!/usr/bin/env python
# coding: utf-8


## 夏之蝉-涉江采芙蓉 参上
## 喜欢的话请给我的GitHub项目加个星星吧


def optimize(inputFile):
    # read packages
    import gurobipy as grb
    import pandas as pd
    import numpy as np

    # read files
    level = pd.read_excel(inputFile, sheet_name = 'level',index_col = 0)
    material=pd.read_excel(inputFile, sheet_name = 'material',index_col=0)
    wip = pd.read_excel(inputFile, sheet_name = 'WIP',index_col = 0)
    product = pd.read_excel(inputFile, sheet_name = 'product',index_col = 0)
    worker = pd.read_excel(inputFile, sheet_name = 'worker',index_col = 0)
    information = pd.read_excel(inputFile, sheet_name = 'info',index_col = 0, header = None)


    # refinement
    level = level[level['belongs to'] == 1]
    product = product.iloc[:,:level['product'][0]]
    worker = worker.iloc[:level['worker'][0]+1,:]
    total_hour = information.iloc[0,0]
    material.loc['per second',:] = material.loc['per hour',:]/3600
    material.loc['Sum',:] = np.floor(material.loc['per hour',:]*total_hour) + material.loc['in stock',:] + np.floor(material.loc['per hour',:]*(total_hour//24)*9)
    # 精英调查数量
    num = level.iloc[:,0][0]
    # 计算生产速度
    SX = pd.DataFrame(index = wip.index, columns = worker.index)
    for wk in worker.index:
        for w in wip.index:
            SX.loc[w,wk] = 3600*0.5/(wip.loc[w,'time']*(1-worker.loc[wk,w]*0.05))


    # # Get plan

    # Optimization 1: get long term plan
    mod=grb.Model()


    M = material.columns
    W = wip.index
    P = product.columns
    WK = worker.index
    # Number of worker
    N = level.iloc[0,1]

    # varaible
    XS = mod.addVars(W, vtype = grb.GRB.INTEGER,  lb = 0)

    X=mod.addVars(W,WK, vtype = grb.GRB.INTEGER, lb = 0)
    Y=mod.addVars(P,WK, vtype = grb.GRB.INTEGER, lb = 0)

    mod.setObjective(sum(Y[p,wk]*product.loc['price',p] for p in P for wk in WK),sense=grb.GRB.MAXIMIZE)

    exp = sum(Y[p,wk]*product.loc['exp',p] for p in P for wk in WK)

    for m in M:
        mod.addConstr(sum(wip.loc[w,m]*X[w,wk] for w in W for wk in WK) <= material.loc['Sum',m])

    for w in W:
        mod.addConstr(sum(product.loc[w,p]*Y[p,wk] for p in P for wk in WK) <= sum(X[w,wk] for wk in WK) + wip.loc[w,'in stock'])

    for wk in WK:
        mod.addConstr(sum(product.loc['time',p]*Y[p,wk] for p in P)\
                  + sum(wip.loc[w,'time']*X[w,wk] for w in W) <= total_hour*3600)  

    # total time limit
    mod.addConstr(sum(product.loc['time',p]*Y[p,wk] for p in P for wk in WK)\
                  + sum(wip.loc[w,'time']*X[w,wk] for w in W for wk in WK) <= total_hour*3600*N)   

    # optimize
    mod.setParam('outputflag',False)
    mod.optimize()


    # exp got
    exp_24 = exp.getValue()

    # revenue got
    rev_24 = mod.objval


    # Output Table: 制造安排 & 委派安排
    soln_wip = pd.DataFrame()

    for w in W:
        if sum(X[w,wk].x for wk in WK) != 0:
            soln_wip.loc[w,'制造数量'] = sum(X[w,wk].x for wk in WK)
        else:
            soln_wip.loc[w,'制造数量'] = ''

    soln_product = pd.DataFrame()

    for p in P:
        if sum(Y[p,wk].x for wk in WK) != 0:
            soln_product.loc[p,'委派数量'] = sum(Y[p,wk].x for wk in WK)
        else:
            soln_product.loc[p,'委派数量'] = ''

    # prepare for short term plan     
    plan = pd.DataFrame()

    for w in W:
        plan.loc[w,'units'] = sum(X[w,wk].x for wk in WK)
    for p in P:
        plan.loc[p,'units'] = sum(Y[p,wk].x for wk in WK)



   # Optimization 2: get short term plan
    mod=grb.Model()

    # varaible
    M = material.columns
    W = wip.index
    P = product.columns
    WK = worker.index
    # Number of worker
    N = level.iloc[0,1]
    E = level.iloc[0,2]
    # short term plan hour
    R = information.iloc[1,0]/60
    # stop times
    K = information.iloc[2,0]

    # binary decision variable
    BX = mod.addVars(W, WK, vtype = grb.GRB.BINARY)
    BY = mod.addVars(P, WK, vtype = grb.GRB.BINARY)

    # amount produced
    X = mod.addVars(W, WK, lb = 0)
    XS = mod.addVars(W, vtype = grb.GRB.INTEGER,  lb = 0)
    Y = mod.addVars(P, WK, lb = 0)


    # Production Time
    TX = mod.addVars(WK, lb = 0)
    TY = mod.addVars(WK, lb = 0)

    # big M
    B = 2000

    # set objective
    efficient_time = sum(X[w,wk]*wip.loc[w,'time'] for w in W for wk in WK)\
                      + sum(Y[p,wk]*product.loc['time',p]*worker.loc[wk,p]/10 for p in P for wk in WK)
    mod.setObjective(efficient_time, sense=grb.GRB.MAXIMIZE)


    exp = sum(Y[p,wk]*product.loc['exp',p] for p in P for wk in WK)

    for m in M:
        # material in stock sufficient to produce wip at start time
        mod.addConstr(sum(BX[w,wk]*wip.loc[w,m] for w in W for wk in WK) <= material.loc['in stock',m])
        for wk in WK:
            # check the change_rate * time <= material
            mod.addConstr((sum(BX[w,wk]*wip.loc[w,m]*SX.loc[w,wk]  for w in W for wk in WK) - np.floor(material.loc['per hour',m]))*TX[wk]\
                          <= material.loc['in stock',m])
            # check stock + change_rate * time <= capacity
            mod.addConstr((np.floor(material.loc['per hour',m]) - sum(BX[w,wk]*wip.loc[w,m]*SX.loc[w,wk] for w in W for wk in WK))*TX[wk]\
                                  <= (material.loc['capacity',m] - material.loc['in stock',m]))
            mod.addConstr((np.floor(material.loc['per hour',m]) - sum(BX[w,wk]*wip.loc[w,m]*SX.loc[w,wk] for w in W for wk in WK))*R\
                          <= (material.loc['capacity',m] - material.loc['in stock',m]))



    for w in W:
        # follow plan
        mod.addConstr(sum(X[w,wk] for wk in WK) == XS[w])
        mod.addConstr(sum(X[w,wk] for wk in WK) <= plan.loc[w,'units'])
        #mod.addConstr(sum(BX[w,wk]*np.floor(SX.loc[w,wk])*R for wk in WK for m in M) <= sum(X[w,wk] for wk in WK for m in M))

        # wip in stock sufficient to produce product at start time
        mod.addConstr(sum(BY[p,wk]* product.loc[w,p] for p in P for wk in WK) <= wip.loc[w,'in stock'])
        for wk in WK:
            # check the change_rate * time <= wip
            mod.addConstr((sum(BY[p,wk]*product.loc[w,p]/product.loc['time',p]*3600 for p in P for wk in WK) - sum(BX[w,wk]*wip.loc[w,m]*SX.loc[w,wk] for wk in WK))*TY[wk]\
                          <= wip.loc[w,'in stock'])
            mod.addConstr((sum(BY[p,wk]*product.loc[w,p]/product.loc['time',p]*3600 for p in P for wk in WK) - sum(BX[w,wk]*wip.loc[w,m]*SX.loc[w,wk] for wk in WK))*TX[wk]\
                          <= wip.loc[w,'in stock'])
            # check stock + change_rate * time <= capacity
            mod.addConstr(wip.loc[w,'in stock'] + (sum(BX[w,wk]*wip.loc[w,m]*SX.loc[w,wk] for wk in WK) - sum(BY[p,wk]*product.loc[w,p]/product.loc['time',p]*3600 for p in P for wk in WK))*TY[wk]  <= wip.loc[w,'capacity'])
            mod.addConstr(wip.loc[w,'in stock'] + (sum(BX[w,wk]*wip.loc[w,m]*SX.loc[w,wk] for wk in WK) - sum(BY[p,wk]*product.loc[w,p]/product.loc['time',p]*3600 for p in P for wk in WK))*TX[wk]  <= wip.loc[w,'capacity'])


    for wk in WK:
        # time limit per person
        mod.addConstr(sum(X[w,wk]/SX.loc[w,wk] for w in W) + sum(Y[p,wk]*product.loc['time',p]/3600 for p in P) <= R)

        # one task per worker in given time frame
        mod.addConstr(sum(BX[w,wk] for w in W) + sum(BY[p,wk] for p in P) <= 1)

        mod.addConstr(sum(X[w,wk]*wip.loc[w,'time'] for w in W)/3600 == TX[wk])
        mod.addConstr(sum(Y[p,wk]*product.loc['time',p] for p in P)/3600 == TY[wk])
        for w in W:
            mod.addConstr(X[w,wk] <= BX[w,wk]*B)

        for p in P:
            mod.addConstr(Y[p,wk] <= BY[p,wk]*B)


    for p in P:
        mod.addConstr(sum(Y[p,wk] for wk in WK) <= plan.loc[p,'units'])

    # number of workers limit
    mod.addConstr(sum(BX[w,wk] for w in W for wk in WK) + sum(BY[p,wk] for p in P for wk in WK) <= N)

    # output limit
    mod.addConstr(sum(Y[p,wk] for p in P for wk in WK) <= (E-N)*K)
    mod.setParam('outputflag',False)
    mod.optimize()



    # Output Table: 短期计划
    soln_next = pd.DataFrame()
    if mod.status != 2:
        print('没有找到不爆仓的短期计划，请加速委派后再来尝试生成短期计划吧～也请检查有没有填错数值哦！')
    else:
        for wk in WK:
            for w in W:
                if BX[w,wk].x != 0:
                    soln_next.loc[wk,'行为'] = w
                    soln_next.loc[wk,'生产数量'] = X[w,wk].x

            for p in P:
                if BY[p,wk].x != 0:
                    soln_next.loc[wk,'行为'] = p
                    soln_next.loc[wk,'生产数量'] = Y[p,wk].x



    # # 输出计划

    summary = [['24小时计划共将获得经验:', exp_24],           ['24小时计划共将获得资金:',rev_24],           ['短期计划时间：（分钟）',information.iloc[1,0] ],           ['短期计划收菜次数）',K ]]
    summary = pd.DataFrame(summary)
    summary


    # Output
    summary = [[f'{total_hour}小时计划共将获得经验:', str(exp_24)],           [f'{total_hour}小时计划共将获得资金:',str(rev_24)],           ['短期计划时间：（分钟）',information.iloc[1,0]],           ['短期计划收菜次数）',information.iloc[2,0]]]
    summary = pd.DataFrame(summary)

    # write output file
    outputFile = '优化方案.xlsx'
    writer = pd.ExcelWriter(outputFile, engine='xlsxwriter')

    summary.to_excel(writer,sheet_name = 'summary', header = False, index = False)
    if mod.status == 2:
        soln_next.to_excel(writer, sheet_name='短期计划')
    soln_wip.to_excel(writer, sheet_name=f'{total_hour}H制造安排')
    soln_product.to_excel(writer, sheet_name=f'{total_hour}H委派安排')

    # Get the xlsxwriter workbook and worksheet objects.
    worksheet = writer.sheets['summary']

    # Set the column width
    worksheet.set_column('A:A', 28)

    writer.save()


if __name__=='__main__':
    import sys, os
    print (f'Running {sys.argv[0]} using argument list {sys.argv}')
    if len(sys.argv)!=2:
        print('Correct syntax: python books.py inputFile')
    else:
        inputFile=sys.argv[1]
        if os.path.exists(inputFile):
            optimize(inputFile)
            print(f'Successfully optimized. Results in 优化方案.xlsx')
        else:
            print(f'File "{inputFile}" not found!')


