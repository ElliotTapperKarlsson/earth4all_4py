import matplotlib.pyplot as plt
from earth4all_4py.utils.e4a_utils import alt_plot_world_variables
from earth4all_4py.earth4all import Earth4All 

#___________________________ Initiating variables and running the simulation
model=Earth4All(demo='tltl' , dt=None, all_values= True) #NOTE dt == timestep in years, all_values ==True -> dt = 0.015625
model.init_e4a_constants()
model.init_earth4all_variables()


'''# ________ Control example:
control_dict = {
    "pop" : ['*0.75' , None],
    "ow"  : ['+( 0.5*al)' , ['al']]
}
model.set_e4a_control(**control_dict)'''

#______ Run the simulation:
model._run_earth4all(var_check=False)


#___________________________ Plotting variables:
plot_variables = [ "pop" , 'awbi' , 'ow' ] # Population Mp , "Average WellBeing Index (1)", "OBserved WArming deg C"
title = f"Plot of "
time = model.time
var_data    =   list()
var_names   =   list()
var_lims    =   list()
line_styles =   list()
line_widths =   list()
# ________________________________ modify plotting

demo = True     #set demo to True to compare to demo run

# ________________________________________________
for var in plot_variables:
    var_values= getattr( model , var ) # Fetches variable array        
    var_data.append( var_values ) 
    var_names.append( var ) # Save name        
    var_lims.append( ( min( 0 , min( var_values) )*1.1  , max(var_values)*1.1 ) ) # Gets smallest and biggest values to create limits
    title+=f" {var} "
    line_styles.append("-")        
    line_widths.append(3)            
    
    # ____________ Only used if demo values are printed
    if demo:                        
        full_demo_values_dict= getattr(model, "all_sectors_demo_values_dict" ) # Fetches all demo values from same model
        demo_var_values=full_demo_values_dict[var] # Fetches demo variable dict                        
        demo_var_values = demo_var_values.reshape(-1)                    
        var_lims.append(( min( 0 , min( demo_var_values) )*1.1  , max(demo_var_values)*1.1 ))            
        var_data.append( demo_var_values )              
        var_names.append(var+"_d" )                      
        line_styles.append(":")                    
        line_widths.append(2)
# ________________________________________________


attributes_dict = {
                'var_data' : var_data , 
                'var_names' : var_names , 
                'var_lims' : var_lims , 
                'line_styles' : line_styles , 
                'line_widths' : line_widths , 
                }                   


# Plotting function:
alt_plot_world_variables(time=time, **attributes_dict,img_background=None, 
                        title=title, figsize=[12,7], dist_spines=0.09, grid=True)
plt.tight_layout()
plt.show()