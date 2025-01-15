init_val_extra_dict={ # Added for initvalue at the year of 1980
    "al_1980" : 0.3094 , #"al[1980]" , # Added for initvalue at the year of 1980
    "nhw_1980" : 2.0 , #"nhw[1980]" , # Added for initvalue at the year of 1980
    "wf_1980" : 1530.0 , #"wf[1980]" , # Added for initvalue at the year of 1980
    "wso_1980" : 0.5 , #"wso[1980]" , # Added for initvalue at the year of 1980
    "ste_1980" : 1.3 , #"ste[1980]" , # Added for initvalue at the year of 1980
    "soc_trust_1980" : 0.6 , #"soc_trust[1980]" , # Added for initvalue at the year of 1980
    "le_1980" :  67.0  , # from init of le:  ["Life Expectancy y" , "LE" , ["LEM","WELE","EGDPP"] , ["LEMAX","LEA","LEG"] , 67.0 
    "epa_2022": 0.0 , # "epa[2022]" 
    "fola_1980" : 1100.0 , # "fola[1980]"
    "pa_1980" : 62.0 , #pa[1980]
    'gci_in_1980' : 5400,
    'oci_in_1980' : 7081,
    'wfi_in_1980' : 13000,
    'inflation_in_1980' : 0.02 ,
    'pulse_height_1' : 0 ,
    'unemployment_rate_in_1980' : 0.05 ,
    'factor_to_avoid_transient_in_growth_rate' : 0.93 ,
    'output_growth_in_1980_to_avoid_transient' : 0.06 ,
    'awi_in_1980' : 0.65 ,
    'pass_20_1980'  : 100 ,
    'pass_40_1980'  : 64 ,
    'pass_60_1980'  : 38 ,
    'dying_in_1980' : 30 ,
    }

init_varname_dict={ # Added for initvalues at the year of 1980
    "albedo in 1980 (1)" : "al_1980" , #"al[1980]" , # Added for initvalue at the year of 1980
    "Normal hours worked in 1980 kh/ftj/y" : "nhw_1980" , #"nhw[1980]" , # Added for initvalue at the year of 1980
    "workforce in 1980 mp" : "wf_1980" , #"wf[1980]" , # Added for initvalue at the year of 1980
    "WSO in 1980 (1)" : "wso_1980" , #"wso[1980]" , # Added for initvalue at the year of 1980
    "social tension in 1980 (1)" : "ste_1980" , #"ste[1980]" , # Added for initvalue at the year of 1980
    "Social trust in 1980 (1)" : "soc_trust_1980" , #"soc_trust[1980]" , # Added for initvalue at the year of 1980
    "LE in 1980" : "le_1980" , # from init of le:  ["Life Expectancy y" , "LE" , ["LEM","WELE","EGDPP"] , ["LEMAX","LEA","LEG"] , 67.0   - - - 'LE in 1980'==={67}_[y]
    "Extra pension age in 2022 y" : "epa_2022" , # epa[2022]
    "Forestry land in 1980 Mha" : "fola_1980" , # "fola[1980]"
    "Pension age in 1980 y" : "pa_1980" , #pa[1980]
    'GCI in 1980' : 'gci_in_1980' ,
    'OCI in 1980' : 'oci_in_1980' ,
    'WFI in 1980' : 'wfi_in_1980' ,
    'Inflation in 1980 (1/y)' : 'Inflation_in_1980' ,    
    'Demand pulse 2020-25 (1)' : "0 + pulse_height_1 * PULSE( time , 2020,5)" , # CHANGED BECAUSE IT GAVE ERROR
    'Demand in 1980 G$/y' : "oo1980 * prun * SWI1980" ,
    'Pulse height (1)' : 'pulse_height_1' ,
    'Unemployment rate in 1980 (1)' : 'Unemployment_rate_in_1980' ,
    'Factor to avoid transient in growth rate (1)' : 'Factor_to_avoid_transient_in_growth_rate' ,
    'Output growth in 1980 1/y (to avoid transient)' : 'Output_growth_in_1980_to_avoid_transient ' ,
    'AWI in 1980 (1)' : 'AWI_in_1980' ,
    'passing 20 in 1980 mp/y'  :  'pass_20_1980' ,   
    'passing 40 in 1980 mp/y'  :  'pass_40_1980' ,   
    'passing 60 in 1980 mp/y'  :  'pass_60_1980' ,   
    'dying in 1980 mp/y'       :  'dying_in_1980',
    }

