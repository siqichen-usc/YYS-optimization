#!/usr/bin/env python
# coding: utf-8

# In[2]:


def optimize(inputFile,simulations = 400):
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
    material.loc['per second',:] = material.loc['per hour',:]/3600
    total_hour = information.iloc[0,0]
    material.loc['Sum',:] = np.floor(material.loc['per hour',:]*total_hour) + material.loc['in stock',:]
    # 精英调查数量
    num = level.iloc[:,0][0]
    
    import itertools
    M = material.columns[2:]
    C = list(itertools.combinations_with_replacement(M,3))
    
    w1 = np.random.random_sample([simulations,3])*0.2+1
    w2 = np.random.random_sample([simulations,3])*0.2+1
    w3 = np.random.random_sample([simulations,3])*0.67+3

    result = pd.DataFrame(index = C)
    for c in C:
        for i in range(simulations):
            material_copy = material.copy(deep = True)
            material_copy.loc['Sum','墨水'] += round(sum(w1[i])*material.loc['per hour','墨水'])
            material_copy.loc['Sum','纸'] += round(sum(w2[i])*material.loc['per hour','纸'])
            for j in range(num):
                material_copy.loc['Sum',c[j]] +=  round(material.loc['per hour',c[j]]*w3[i,j])

            mod=grb.Model()

            # varaible
            M = material.columns
            W = wip.index
            P = product.columns

            X=mod.addVars(W, vtype = grb.GRB.INTEGER)
            Y=mod.addVars(P, vtype = grb.GRB.INTEGER)
            mod.setObjective(sum(Y[p]*product.loc['price',p] for p in P),sense=grb.GRB.MAXIMIZE)

            for m in M:
                mod.addConstr(sum(wip.loc[w,m]*X[w] for w in W) <= material_copy.loc['Sum',m])

            for w in W:
                mod.addConstr(sum(product.loc[w,p]*Y[p] for p in P) <= X[w] + wip.loc[w,'in stock'])
                mod.addConstr(X[w] >= 0)

            for p in P:
                mod.addConstr(Y[p] >= 0)

            mod.setParam('outputflag',False)    
            mod.optimize()

            result.loc[c,'test '+str(i+1)] = mod.objval
            
    mod=grb.Model()

    # varaible
    M = material.columns
    W = wip.index
    P = product.columns

    X=mod.addVars(W, vtype = grb.GRB.INTEGER)
    Y=mod.addVars(P, vtype = grb.GRB.INTEGER)
    mod.setObjective(sum(Y[p]*product.loc['price',p] for p in P),sense=grb.GRB.MAXIMIZE)

    exp = sum(Y[p]*product.loc['exp',p] for p in P)

    for m in M:
        mod.addConstr(sum(wip.loc[w,m]*X[w] for w in W) <= material.loc['Sum',m])

    for w in W:
        mod.addConstr(sum(product.loc[w,p]*Y[p] for p in P) <= X[w] + wip.loc[w,'in stock'])
        mod.addConstr(X[w]  >= 0)

    for p in P:
        mod.addConstr(Y[p] >= 0)

    mod.setParam('outputflag',False)    
    mod.optimize()

    result = result - mod.objval
    Final_choice = result.mean(axis = 1).idxmax()
                  
    print(result.mean(axis = 1))
    print('精英调查选：' + str(Final_choice))
    
    I = int(np.random.random(1)*simulations)
    
    material_copy = material.copy(deep = True)
    material_copy.loc['Sum','墨水'] += round(sum(w1[I])*material.loc['per hour','墨水'])
    material_copy.loc['Sum','纸'] += round(sum(w2[I])*material.loc['per hour','纸'])
    for j in range(num):
        material_copy.loc['Sum',Final_choice[j]] +=  round(material.loc['per hour',Final_choice[j]]*w3[I,j])

    mod=grb.Model()

    # varaible
    M = material.columns
    W = wip.index
    P = product.columns

    X=mod.addVars(W, vtype = grb.GRB.INTEGER)
    Y=mod.addVars(P, vtype = grb.GRB.INTEGER)
    mod.setObjective(sum(Y[p]*product.loc['price',p] for p in P),sense=grb.GRB.MAXIMIZE)

    exp = sum(Y[p]*product.loc['exp',p] for p in P)
    
    for m in M:
        mod.addConstr(sum(wip.loc[w,m]*X[w] for w in W) <= material_copy.loc['Sum',m])

    for w in W:
        mod.addConstr(sum(product.loc[w,p]*Y[p] for p in P) <= X[w] + wip.loc[w,'in stock'])
        mod.addConstr(X[w] >= 0)

    for p in P:
        mod.addConstr(Y[p] >= 0)

    mod.setParam('outputflag',False)    
    mod.optimize()
    
    
    # Output Table: 制造数量 & 委派数量
    soln_wip = pd.DataFrame()

    for w in W:
        if X[w].x != 0:
            soln_wip.loc[w,'制造数量'] = X[w].x
        else:
            soln_wip.loc[w,'制造数量'] = ''

    soln_product = pd.DataFrame()

    for p in P:
        if Y[p].x != 0:
            soln_product.loc[p,'委派数量'] = Y[p].x 
        else:
            soln_product.loc[p,'委派数量'] = ''
    
    # exp got        
    exp_24 = exp.getValue()
    exp_24 

    # revenue got
    rev_24 = mod.objval
    rev_24
    
    # Output
    summary = [[f'{total_hour}小时计划共将获得经验:', str(exp_24)],           [f'{total_hour}小时计划共将获得资金:',str(rev_24)]]
    summary = pd.DataFrame(summary)

    # write output file
    outputFile = '精英调查.xlsx'
    writer = pd.ExcelWriter(outputFile, engine='xlsxwriter')

    summary.to_excel(writer,sheet_name = 'summary', header = False, index = False)
    soln_wip.to_excel(writer, sheet_name=f'{total_hour}H制造安排')
    soln_product.to_excel(writer, sheet_name=f'{total_hour}H委派安排')

    # Get the xlsxwriter workbook and worksheet objects.
    worksheet = writer.sheets['summary']

    # Set the column width
    worksheet.set_column('A:A', 28)

    writer.save()


# In[3]:


if __name__=='__main__':
    import sys, os
    print (f'Running {sys.argv[0]} using argument list {sys.argv}')
    if len(sys.argv)!=2:
        print('Correct syntax: python books.py inputFile')
    else:
        inputFile=sys.argv[1]
        if os.path.exists(inputFile):
            optimize(inputFile)
            print(f'Successfully optimized. Results in 精英调查.xlsx')
        else:
            print(f'File "{inputFile}" not found!')

# In[ ]:




