import pandas as pd

loc_m = '/Users/yunmai/Documents/NLP_annotation/cancerdrug_notes_860_summary.xlsx'
loc_k = '/Users/yunmai/Documents/NLP_annotation/final_cancer_drugs.xlsx'
loc_t = '/Users/yunmai/Documents/NLP_annotation/All_annotated_entities_in_1226_lca_notes.xlsx'
loc_a = '/Users/yunmai/Documents/cancer_drug_shared/cancer_drugs_Dan_OA_Sunny_Reviewed_by_KL_and_Sunny_WJ_edits(1).xlsx'
loc_c = '/Users/yunmai/Documents/NLP_annotation/SEER_Rx_Interactive_Antineoplastic_Regimens_Database.xlsx'

#my summary
a=pd.read_excel(loc_m,sheet_name=1)
a = a[['word','note']]
a = a.apply(lambda x: x.astype(str).str.lower())
a.drop_duplicates(keep='first',inplace=True) # 361; 348 after rm duplicates

#kl's summary
b=pd.read_excel(loc_k,sheet_name=3)
b.head()
b.columns
b.Captured = b.Captured.str.lower()
b.Not_captured = b.Not_captured.str.lower()

b2=pd.read_excel(loc_k,sheet_name=6)
b2.head()
b2.columns
b2.Captured = b2.Captured.str.lower()
b2.Not_captured = b2.Not_captured.str.lower()

b3 = pd.concat([b[['Captured', 'Not_captured']],b2[['Captured', 'Not_captured']]],0)
b3.drop_duplicates(keep='first',inplace=True)
b3[~(b3.Captured.isna()|b3.Not_captured.isna())]
b4 = b3.set_index('Captured').Not_captured.str.split(',',expand=True).stack().reset_index()
b4 = b4.rename(columns={0:'Not_captured'})
b4 = b4.loc[:,['Captured', 'Not_captured']]
b4.drop_duplicates(keep='first',inplace=True) # 99, not duplicates

#meng's entity list
c=pd.read_excel(loc_t)
c.drop_duplicates(keep='first',inplace=True) # 801, not duplicates
c.head()

#three team list
d=pd.read_excel(loc_a,sheet_name=1)
d.head()
d=pd.melt(d,id_vars='generic_name',value_vars=['trade_name_dan', 'trade_name_OA', 'trade_name_sunny'])
d=d[['generic_name','value']]
d.drop_duplicates(keep='first',inplace=True) # 487 after rm dup
#d.to_csv('/Users/yunmai/Documents/cancer_drug_shared/cancer_drugs_Dan_OA_Sunny_list.csv')

# stack dif trade name in three team table
d = pd.read_excel(loc_a,sheet_name=2)
d = d[['generic_name', 'trade_name_dan', 'trade_name_OA', 'trade_name_sunny']]
d_l = pd.melt(d,id_vars='generic_name',value_vars=['trade_name_dan', 'trade_name_OA', 'trade_name_sunny'],var_name='team',value_name='trade_name')[['generic_name','trade_name']]
d_l = d_l[~d_l.trade_name.isna()].drop_duplicates(keep='first')
d_l = d_l.apply(lambda x: x.astype(str).str.lower())

#cancer_drug_combination
cm = pd.read_excel(loc_c,sheet_name=0)
cm1 = cm[['Name', 'Drugs']]
cm2 = cm[['Alternate Names','Drugs']]
cm2 = cm2.set_index('Drugs')['Alternate Names'].str.split(';',expand=True).stack().reset_index()
cm2 = cm2.rename(columns={0:'Name'})
cm2 = cm2.loc[:,['Name', 'Drugs']]
cm_l = pd.concat([cm1,cm2],0).drop_duplicates(keep='first')
cm_l = cm_l.apply(lambda x: x.astype(str).str.lower())

#merge entity with mine
m1 = pd.merge(c,a,how='left', left_on = 'Entity',right_on='word')
m1['Normatlized Name'] = (m1['Normatlized Name'].fillna('') + m1['note'].fillna(''))

#join with kl's list
m2 = pd.merge(m1,b4,how='left', left_on = 'Entity',right_on='Not_captured')
m2['Normatlized Name'] = (m2['Normatlized Name'].fillna('') + '|'+ m2['Captured'].fillna('')).str.strip('|')

#join with three team list 
m3 = pd.merge(m2,d_l,how='left', left_on = 'Entity',right_on='trade_name')
m3['Normatlized Name'] = (m3['Normatlized Name'].fillna('') + '|'+ m3['generic_name'].fillna('')).str.strip('|')
m3.drop_duplicates(keep='first',inplace=True)

#join with cdc list 
m4 = pd.merge(m3,cm_l,how='left', left_on = 'Entity',right_on='Name')
m4['Normatlized Name'] = (m4['Normatlized Name'].fillna('') + '|'+ m4['Drugs'].fillna('')).str.strip('|')
m4.drop_duplicates(keep='first',inplace=True) # 838, rm dup 838

c.shape #801
m1.shape #803
m2.shape #804
m3.shape #826
m4.shape #826

m1[(m1['Normatlized Name']=='')| (m1['Normatlized Name'].isna())|(m1['Normatlized Name'] == 'nan')].shape # 803 total, 624 na|empty|'nan' # 179 filled
m2[(m2['Normatlized Name']=='')| (m2['Normatlized Name'].isna())|(m2['Normatlized Name'] == 'nan')].shape # 804 total, 598 na|empty|'nan'  # 27 more filled; 206 filled
m3[(m3['Normatlized Name']=='')| (m3['Normatlized Name'].isna())|(m3['Normatlized Name'] == 'nan')].shape # 826 total, 483 na|empty|'nan'  # 137 more filled; 343 filled
m4[(m4['Normatlized Name']=='')| (m4['Normatlized Name'].isna())|(m4['Normatlized Name'] == 'nan')].shape # 826 total, 449 na|empty|'nan'  # 34 more filled; 377 filled


output = m4[c.columns]

output.to_csv('/Users/yunmai/Documents/NLP_annotation/All_annotated_entities_in_1226_lca_notes_1.csv')