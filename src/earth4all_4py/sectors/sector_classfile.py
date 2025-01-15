#_____________________________________________________________ IMPORTS _________________________________________________________________________________
import numpy as np
import traceback # For information during error handling
from math import exp # some equations use exp
#from math import log as ln # the equations use it with name "ln" log in python is also the natural logarithm
ln=np.log # For usage in eval
from ..utils.special_functions import (ramp, step, pulse, if_then_else, integ , smooth, smoothi, with_lookup) # Special functions
from ..utils.special_functions import Delay_Nth_order # Delay N class
from ..utils.e4a_utils import  requires # For fetching base run values
from ..utils.constants import (init_varname_dict, init_val_extra_dict) 
from ..utils.variable_classfile import Variable , Parameter
from ..utils.e4a_utils import fetch_all_demo_values_from_df , demo_values_df, get_eqs_from_json

#_____________________________________________________ Class declaration __________________________________________________________________________________
class Sector:    
        
    def __init__(self, obj_specific=True, sector_name="e4a_sector", year_min=1980, year_max=2100, dt=1, demo=True, verbose=False):          
        if obj_specific==True:
            self.sector_name=sector_name
            self.iphst = 1940
            self.dt = float(dt)
            self.year_min = year_min
            self.year_max = year_max
            self.verbose = verbose
            self.length = self.year_max - self.year_min
            self.n = int(self.length / self.dt)
            self.time = np.arange(self.year_min, self.year_max, self.dt)
            self.demo=demo
            self.sectornames_list=["climate","demand","energy","finance","food_and_land","inventory","labour_market","other_performance_indicators","output","population","public","wellbeing"]                            
            if demo==True:  # Save the demo values as an attribute
                self.general_add_demo_values(sector_name)
                print(getattr(self, "demo_values_dict"))
    

    def init_sector_constants(self ): #, **alt_const): # Add later
        """
        Initialize the constant parameters and initial values 
        """                               
        all_sectors_parameters_dict={}        
        for sector in self.sectornames_list: # Goes through each sector one by one to get its specific parameters
            
            sector_parameters_dict_real=self.all_parameters_dict_by_sector[sector] 
            sector_parameters_dict=sector_parameters_dict_real.copy() # Copies it because it is global and we want to keep it as it is
            for parameter, value in sector_parameters_dict.items(): # Goes through the parameters one by one to set them as attributes
                sector_parameters_dict[parameter]= value[-1] # overwrite to only save value to name pair                
                parameter_obj = Parameter(name=parameter , value=value[-1]) # value[-1] denotes the value of the parameter
                setattr(self, parameter, parameter_obj) # Creates attribute for saving a parameter class object                                                                    
            setattr(self, f"{sector}_parameters_dict", sector_parameters_dict) # set the entire dict as an attribute
            all_sectors_parameters_dict.update(sector_parameters_dict) # add sectors parameters

        setattr(self, "all_sectors_parameters_dict", all_sectors_parameters_dict) # set the dict of all parameters as attribute
        

    def variable_mem_alloc_sector(self, sector): 
        ''' Allocates memory for variable arrays by initiating Variable class objects '''                
        sector_variables_dict=self.all_sectors_variables_dict[sector]                

        for variable_name in sector_variables_dict:
            nan_array=np.full( (self.n,) , np.nan)            
            variable_object = Variable(name=variable_name , values=nan_array)
            setattr(self, variable_name, variable_object ) # assigns as attribute  passing key value pairs                

    def init_sector_variables(self, **alt_init):
        """ Initialize the state and rate variables of the current sector
        (memory allocation) """        
        sector_variables_dict=self.all_sectors_variables_dict[self.sector] # Gets all variables
        dict_of_eq_sector = get_eqs_from_json( self.sector)
        #dict_of_eq_sector=self.write_sector_eq_contents_json( sector=self.sector, read=True )                
                             
        #------------------------#------------------------#------------------------            
        dict_of_required = self.init_required_dict_v2()       # Gets all possible requirements needed by the variable computations
        #------------------------ Sets known #* EQUATIONS
        # Check which variables has initial values and save them into the attributes
        for variable_key in sector_variables_dict:
            
            try:
                if variable_key=="contr": #Seems to only cause trouble, used to control that everything is working  
                    continue
                eq_string = dict_of_eq_sector[variable_key] # Gets the current variables equation string                                
                var_obj=getattr(self, variable_key)                 
                temp_dict_of_required = dict_of_required.copy()
                temp_dict_of_required[variable_key] = np.nan # Add in case need itself
                var_obj.initiate_eq(eq_string , temp_dict_of_required )
                vars_required = sector_variables_dict[variable_key][2]
                if vars_required == [None] or vars_required == None:
                    var_obj.vars_required = [None] 
                else:
                    var_obj.vars_required = [var.lower() for var in vars_required if isinstance(var, str)] 
                if vars_required!=None:
                    if variable_key in vars_required or ( "integ(" in eq_string or "smooth(" in eq_string or "smoothi(" in eq_string or "_delay_n(" in eq_string ): 
                        var_obj.state_variable=True # Means that it is a state variable, will affect which values updated in updater (k+1)                        
                setattr(self, variable_key, var_obj) # Updates the variable attribute
            
            except Exception as e:
                raise e            
        
        #------------------------ Sets known init values -------------------- 
        # Check which variables has initial values and save them into the attributes
        for variable_key in sector_variables_dict:
            init_value=sector_variables_dict[variable_key][4]
            if init_value!=None:    # If there is init value                         
                var_attribute=getattr(self, variable_key) # Gets attr             
                try:
                    var_attribute[0]=init_value # Asserts init value to array
                except:
                    raise IndexError(var_attribute)                
                setattr(self, variable_key, var_attribute) # Updates the variable attribute
            
        #If there is alternative init_values
        if len(alt_init)>0:
            for alt_init_key, alt_init_value in alt_init.items():
                if alt_init_key in sector_variables_dict: # if it is a variable_init, change it
                    #self.sector_variables_dict[alt_init_key]= alt_init[alt_init_key]

                    var_attribute=getattr(self, alt_init_key) # Gets attr #* Now this is a variable class object Should still work the same  
                    #print(var_attribute)
                    try:
                        var_attribute[0]=alt_init_value # Asserts init value to array
                    except:

                        raise IndexError(var_attribute)#self.__dict__.keys())
                    #print(variable_key, " has initiated array: ", var_attribute)
                    setattr(self, alt_init_key, var_attribute) # Updates the variable attribute                    
                    #print("Added init to ", alt_init_key, " with initvalue=", alt_init_value)    

    def init_delay_functions(self): 
        '''
        Initialize the class objects for DelayN 
        used to save the delay state of those variables        
        '''                                                
        # ______________________________________  Parameters needed (from Vensim):                                    
        pass_20_1980   =  100                       # 'Passing 20 in 1980 Mp/y'==={100}_[Mp/y]
        pass_40_1980   =  64                        # 'Passing 40 in 1980 Mp/y'==={64}_[Mp/y]        
        pass_60_1980   =  38                        # 'Passing 60 in 1980 Mp/y'==={38}_[Mp/y]        
        dying_in_1980  = 30                         # 'Dying in 1980 Mp/y'==={30}_[Mp/y]
        le_at_60_1980  = 67-60                      # 'LE at 60 y'==={Life expectancy y - 60}_[y]        (LE_in_1980 - 60)
        order = 10                                  # 'Order'==={10}_[Mp/y]

        # Initialize DelayN class objects
        pass20_delay_n = Delay_Nth_order(varname="pass20", initial_value = pass_20_1980 , delay_time=20,  order_N=order , dt=self.dt, method="euler")               # 'Passing 20 Mp/y'==={DELAY N("Births Mp/y", 20, "Passing 20 in 1980 Mp/y", Order)}_[y]
        pass40_delay_n = Delay_Nth_order(varname="pass40", initial_value = pass_40_1980 , delay_time=20,  order_N=order , dt=self.dt, method="euler")               # 'Passing 40 Mp/y'==={DELAY N("Passing 20 Mp/y", 20, "Passing 40 in 1980 Mp/y", Order)}_[Mp/y]
        pass60_delay_n = Delay_Nth_order(varname="pass60", initial_value = pass_60_1980 , delay_time=20,  order_N=order , dt=self.dt, method="euler")               # 'Passing 60 Mp/y'==={DELAY N("Passing 40 Mp/y", 20, "Passing 60 in 1980 Mp/y", Order)}_[Mp/y]
        deaths_delay_n = Delay_Nth_order(varname="deaths", initial_value = dying_in_1980 , delay_time=le_at_60_1980,  order_N=order , dt=self.dt, method="euler")   # 'Deaths Mp/y'==={DELAY N("Passing 60 Mp/y", LE at 60 y, "Dying in 1980 Mp/y", Order)}_[Mp/y]        

        setattr(self, "deaths_delay_n" , deaths_delay_n )
        setattr(self, "pass20_delay_n" , pass20_delay_n )
        setattr(self, "pass40_delay_n" , pass40_delay_n )
        setattr(self, "pass60_delay_n" , pass60_delay_n )
    
    def general_add_demo_values(self, sector, run_version="tltl" , all_values=False):                            
        #print(f"Fetching demo values from {sector:>32}")                
        if all_values: 
            try:                            
                var_name_values_dict ,  years = fetch_all_demo_values_from_df(demo_run_type = run_version , sector = sector) #* If all already placed in .csv file (after 20th nov 2024)
                setattr(self, f"{sector}_demo_values_dict", var_name_values_dict) # Sends all variables and all value arrays as keyword args- False, setting a simple dict            
                self.n = int( len(years) ) # Generate n value   # Same as k_max+1                                 
                self.dt = float(self.length / (self.n-1) )                               
                self.time = years # Defines the time-space, creates a linspace covering all timesteps        
                return
            except Exception as e:
                raise e           
             
        else:            
            var_name_values_dict=demo_values_df(sector, run=run_version, dt=self.dt , time= self.time) # Fetches demo values for all variables per each time step dt for given sector            
            setattr(self, f"{sector}_demo_values_dict", var_name_values_dict) # Sends all variables and all value arrays as keyword args- False, setting a simple dict
            return                
          
    def loop0_sector(self, sector, alone=False):
        """
        Run the initial loop updating all the variable values (loop with k=0).        
        """        
        sector_variables_dict=self.all_sectors_variables_dict[sector]
        if alone:   #NOTE this is not yet created
            pass
            #self.loop0_exogenous()                
        
        for var_name in sector_variables_dict:            
            if var_name=="contr": #Seems to only cause trouble, used to control that everything is working i believe
                continue
            variable_object = getattr(self , var_name)             
            var_requirements= variable_object.vars_required # Gets specific requirements of var                                             
            
            if self.demo!="DEMO":
                try:                    
                    if self.round>22:
                        raise Exception("Rounds of computations exceeded 22, there is likely to be an error.")                                                                                       

                    self.update_variable( variable_object, var_requirements, 0 ) # Syntaxwarning happens in here                                                
                    
                except Exception as e :                                        
                    print(f"\nDemo values for {variable_object } used instead because of: {e}" )
                    print(f"\n{traceback.format_exc()}\n")
                    input("Press enter to continue...")
                    demo_uses=getattr(self, "times_demo_used")
                    setattr(self, "times_demo_used", demo_uses+1 )                    
                    self.demo_update_var(variable_object, var_requirements, 0 ) # because init
            else:                
                self.demo_update_var(variable_object, var_requirements, 0 ) # UPDATE USING DEMO VALUES ONLY
            
    def loopk_sector(self, sector, k, alone=False , objs_ordered=None , names_listed=None): #j, k, jk, kl, alone=False): 
        """
        Run the loop updating all the variable values of the current sector (at all k!=0).        
        """                   
        obj_dict = objs_ordered[sector]
        names_list = names_listed[sector]

        for varname in names_list[:]: # Iterate through variable names
            variable_object = obj_dict[varname]
            if str(variable_object)=="contr": #Seems to only cause trouble, used to control that everything is working i believe
                continue
            var_requirements= variable_object.vars_required # Gets specific requirements of var                                
            
            if self.demo!="DEMO":
                try:                                        
                    if self.round>22:
                        raise Exception("Rounds of computations exceeded 22, there is likely to be an error.")    
                                        
                    if self.update_variable(variable_object, var_requirements, k ): #Runs the update and returns True if successful
                        names_list.remove(varname)
                    
                except Exception as e:
                    print(f"At k ={k} {str(variable_object)+'='+variable_object.equation_string:_>100}\nCaught an Exception: '{e} {traceback.format_exc()}")                                                            
                    input("Press enter to continue...")
                    demo_uses=getattr(self, "times_demo_used")
                    setattr(self, "times_demo_used", demo_uses+1 )                                                                                
                    self.demo_update_var(variable_object, var_requirements, k ) # Attempt var update
            else:                 
                self.demo_update_var(variable_object, var_requirements, k ) # UPDATE USING DEMO VALUES ONLY

    def run_sector(self, sector): 
        """
        Runs the update loop for a certain sector exogenously
        """
        self.redo_loop = True
        while self.redo_loop: # Loops until self.redo_loop remains False
            self.redo_loop = False # This will be toggled to True if a requirement is missed within the loop
            self.loop0_sector(sector=sector, alone=True)

        for k_ in range(1, self.n):
            print(f"Loop k={k_}")
            self.redo_loop = True
            while self.redo_loop: # Loops until self.redo_loop remains False
                self.redo_loop = False # This will be flipped back if a requirement is misse at some point
                if self.verbose: # If verbose, notifies which loop is looped
                    print("go loop", k_)
                self.loopk_sector(k_ - 1, k_, k_ - 1, k_, alone=True) # Attempt updating all variables

    @requires()     
    def demo_update_var(self,  variable_obj, required_vars, k , req_met=True, state_variable=False):        
        """
        Updates variable value using demo values 
        """        
        current_value= variable_obj[k] # NOTE Now passing variable object
        variable_name = str(variable_obj)
        sector=self.current_sector               
        year = self.time[k]  # demo uses year now because of how the dict is set up        
    
        try: # Get the values from the demo version    
            demo_var_array=getattr(self, f"{sector}_demo_values_dict")[variable_name]  # Gets values from demo as dict -> # The demo values as an array         
        except: # Incase any error
            print(self.dt)
            print(year)
            raise LookupError("Demo values were not initiated correctly")

        if state_variable == True: # Update next state, requires current state
            if year<self.year_max:                
                                 
                demo_value_at_next_k = demo_var_array[ k+1 ] 
                demo_value_at_k = demo_var_array[ k ]  

                # Update current value with demo, unless it already exists, likely to happen with state vars
                if np.isnan(current_value) and k==0: # State variables mostly are already calculated at current step, except smoothi and ...                    
                    variable_obj[k]=demo_value_at_k
                                
                variable_obj[k+1]=demo_value_at_next_k # Input demo value of next step
            else: # At last step, dont do anything for state variables
                return            
        else: # Update current state of auxilliary variable        
            demo_value_at_k = demo_var_array[ k ]              
            # Update current value with demo, unless it already exists, likely to happen with state vars
            if np.isnan(current_value): # State variables mostly are already calculated at current step, except smoothi and such                
                variable_obj[k]=demo_value_at_k            
        setattr(self, variable_name, variable_obj) # sets it as the new array
        
            
            
    def init_required_dict_v2(self):
        '''Initiate a dictionary of all necessary variables and equations and parameters
        Pass to each variable class object and save. Within the variable, we also truncate the dict by only keeping the ones that are found in eq_string '''
        dict_of_required={}
        #___________________________________ Add locals/ globals to pass to eval #___________________________________________________________ 
        sector_parameters_dict=getattr(self, f"all_sectors_parameters_dict" ) # Gets all parameters
        dict_of_required.update(sector_parameters_dict) # Also requires some parameters        
        dict_of_required["ramp"]=ramp
        dict_of_required["exp"]=exp
        dict_of_required["ln"]=ln
        dict_of_required.update(init_val_extra_dict) # Gets values for initial values extra made parameters                
        dict_of_required["k"]=0
        dict_of_required["time"]=self.time[0] # Time seems to mean year in the equations
        dict_of_required["step"]=step
        dict_of_required["pulse"]=pulse
        dict_of_required["if_then_else"]=if_then_else
        dict_of_required["integ"]=integ
        dict_of_required["smooth"]=smooth
        dict_of_required["smoothi"]=smoothi
        dict_of_required["with_lookup"]=with_lookup                
        dict_of_required["dt"]=self.dt        
        dict_of_required["lambda_"] = sector_parameters_dict["lambda_"] # Parameter with special name that might cause issues
        #equation_string=equation_string.replace("^", "**") # alter eq_string in var obj                
        #le60   = self.le60[0]   # Needed to avoid exception when calling death_delay_n()        
        dict_of_required['le60']   =  0     # Needed to avoid exception when calling death_delay_n()                             
        dict_of_required['order' ] = 10                                 # Needed to avoid exception when calling delay functions                                                                      
        
        for variable_name in ["deaths" , "pass20" , "pass40" , "pass60"]: 
            delay_func = getattr(self, f"{variable_name}_delay_n")
            dict_of_required[f"{variable_name}_delay_n"] = delay_func # Add specific delay function object                
        return dict_of_required 
        
    @requires()   # @requires wraps the update function to check whether all required values are available
    def update_variable(self,  variable_obj, required_vars, k , req_met=True, state_variable=False):  
        '''Function that updates the variable value from required values at current time step '''                        
        current_value= variable_obj[k] # NOTE Now passing variable object        
        variable_name = variable_obj.name    

        # If already calculated, no need to calc again, but state variables, update next step, so doesnt apply to them
        if not req_met or ( not np.isnan(current_value) and not state_variable ):
            return False                     
        if state_variable and (k==self.n-1 or not np.isnan(variable_obj[k + 1]) ):
            return False        
        #______________________________ Add required variables to locals to pass to eval() #______________________________ 
        dict_of_required = {**required_vars, 
                            "k": k, 
                            "time": self.time[k], 
                            variable_name: current_value}                                 
        
        if variable_name in ["deaths" , "pass20" , "pass40" , "pass60"]: 
            if variable_name == "deaths":    
                le60   = self.le60[k] # Needed to avoid exception when calling death_delay_n()
                if np.isnan(le60): # If required not met
                        return False
                dict_of_required['le60']   =  le60     # Needed to avoid exception when calling death_delay_n()         
            delay_func = getattr(self, f"{variable_name}_delay_n")
            dict_of_required[f"{variable_name}_delay_n"] = delay_func # Add specific delay function object
            result , delay_func = variable_obj.compute_value( k , dict_of_required)
            setattr(self, f"{variable_name}_delay_n" , delay_func) # Update delay obj
        else:
            result = variable_obj.compute_value(k , dict_of_required)                   
                
        if state_variable:
            variable_obj[k+1]=result # Asserts the new value at k+1
        else:
            variable_obj[k]=result # Asserts the new value at k
        setattr(self, variable_name, variable_obj) # sets it as the new array            

        if abs(result)==np.inf: 
            raise ValueError("result INF")        
        # NOTE: If we have gotten to here, we have likely managed to compute the value and saved it. 
        # Return a bool regarding if the update was succesful        
        return True
        
    def __str__(self):
        return "sector class object"
    