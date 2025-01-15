#__________________________________________________ IMPORTS ___________________________________________________________________________________________
import time # for evaluating efficiency
import json # Used to import variable information
from .sectors.sector_classfile import *
from importlib.resources import open_text
#from .sectors.translate_variables_classfile import translate_variables
#_____________________________________________________________________________________________________________________________________________

#__________________________________________________ Class declaration ___________________________________________________________________________________________
class Earth4All(Sector):#, translate_variables):#* REMOVE:, Climate, Demand, Energy, Finance, Food_and_land, Inventory, Labour_market, Other_performance_indicators, Output, Population, Public, Wellbeing , translate_variables): # Inheritance to all sectors   
    ''' The Earth4All class used for running the model simulation'''
    
    def __init__(       # Takes in arguments when initializing
        self,
        year_min=1980, 
        year_max=2100,
        dt= 0.015625, # Original vensim value #NOTE too large time step will cause errors (~0.05 is max)
        demo=True,            # Change to False later
        verbose=False,        # Defines whether to print extra information during simulation run
        all_values = False,
        V2 =True
    ):
        ''' Initializes an Earth4All class object '''
      
        self.v2 =V2 # USed to check if using variable class file
                    
        self.sectornames_list=["climate","demand","energy","finance","food_and_land","inventory","labour_market","other_performance_indicators","output","population","public","wellbeing"]    
        self.demo=demo #TODO REMOVE
        self.verbose = verbose
        self.k=0 
        self.year_min = year_min
        self.year_max = year_max
        self.length = self.year_max - self.year_min

        self.all_values = all_values # TODO REMOVE? If we want to use the exact same values as in demo values version, ie. dt==0.015625 ish.. Then this should be used to define all dt and n and time
        
        self.fetch_variable_information() # Gets information on all variables and parameters and sets as attributes
                
        if all_values==True:
            self.generate_demo_values(all_values=all_values, demo_version=demo) # Use to set dt and so on

        else: 
            self.dt = dt
            self.n = int(self.length / self.dt) + 1 # Same as k_max+1        
            self.time = np.linspace(self.year_min, self.year_max, self.n )       # Defines the time-space, creates a linspace covering all timesteps                
            
            if demo!=False:                
                if demo==True or demo=="DEMO":
                    self.generate_demo_values()
                elif demo=="tltl" or "gl":
                   self.generate_demo_values(demo) 
                else: 
                    raise print("Incorrect argument passed for demo")        

        print(f"\n\n{'':~^150}\n{str(self)}")                                          
        input(f"{' BEGIN? ':_>150}")
    
    #_____________________________________________________________________________________________________________________________________________
    def set_e4a_control(self , **variable_control): #To be implemented later - see set_world_control from pyworld3
        '''Function for implementing control of variables of choice
        **variable_control ==
        {varname_0 string : [equation_string , requires string or None]
        control equation should be on form:
         (*, + ) (....), if using other variable, add to requires
        }        
        '''        
        if variable_control!=None:
            for variable_name, control_list in variable_control.items():
                control_function , requires = control_list
                try:

                    variable_object = getattr(self, variable_name)
                    
                    variable_object.equation_string = '('+variable_object.equation_string + ')'+str(control_function)
                    
                    if requires!=None:
                        for req_variable in requires:
                            variable_object.vars_required.append(req_variable)                        
                        #NOTE; only name is important right now, cause it will later fetch values
                                                
                    variable_object = setattr(self, variable_name , variable_object)
                except Exception as e:
                    print(f"\nThe following exception occured when upon attempting to apply control function ({variable_name}:{control_function}): \n\n{e}\n")
    
    #_____________________________________________________________________________________________________________________________________________
    def fetch_variable_information(self):
        ''' Fetches variable and parameter data and stores as attributes '''        
                
        dir_path =  'sectors.sector_variables'                
        json_vars_path =  'sector_variables.json' 
        json_pars_path =  'sector_parameters.json'


        with open_text(f'earth4all_4py.{dir_path}', json_vars_path ) as variable_json_file: # open file
            dict_of_var_dicts = json.load(variable_json_file)

        self.all_sectors_variables_dict = dict_of_var_dicts        
            
        with open_text(f'earth4all_4py.{dir_path}', json_pars_path ) as parameter_json_file: # open file        
            dict_of_par_dicts = json.load(parameter_json_file)

        self.all_parameters_dict_by_sector = dict_of_par_dicts.copy() #NOTE, used if one wants to fetch parameters for a specific sector
        dict_of_all_pars = {}
        dict_of_all_pars = {dict_of_all_pars.update( dicts ) for dicts in dict_of_par_dicts.values()}
        self.all_sectors_parameters_dict = dict_of_all_pars #NOTE: this contains redundant information, which will be replaced in method: init_sector_constants(self ) in sector class

    #_____________________________________________________________________________________________________________________________________________
    def init_e4a_constants(  
        self,
        **alt_constants ):
        """
        Initialize the constant parameters of the sectors. Constants and
        their unit are defined according to the original vensim model.
        """
        self.init_sector_constants()
    
    #_____________________________________________________________________________________________________________________________________________
    def init_earth4all_variables(self, **alt_inits ):
        """
        Initializes all model variables as objects of the Variable class. 
        """
        self.init_delay()  # Init all the delay functions

        # Fetches initial values from delay objects (only really deaths that need this)
        delay_init_dict={
        'deaths' : getattr(self, "deaths_delay_n" ).initial_value ,
        'pass20' : getattr(self, "pass20_delay_n" ).initial_value ,
        'pass40' : getattr(self, "pass40_delay_n" ).initial_value ,
        'pass60' : getattr(self, "pass60_delay_n" ).initial_value ,
        }
        
        for sector in self.sectornames_list:
            self.sector=sector
            self.variable_mem_alloc_sector(sector)
            self.init_sector_variables(**delay_init_dict) 
    
    #_____________________________________________________________________________________________________________________________________________
    def init_delay(self): # Init all the delay functions
        self.init_delay_functions()

    #_____________________________________________________________________________________________________________________________________________
    def dict_of_var_objects(self):
        obj_dict = {}
        for sector in self.sectornames_list:
            sector_variables_dict=self.all_sectors_variables_dict[sector]            
            sector_dict = {}
            for varname in sector_variables_dict:
                sector_dict[varname] = getattr(self, varname)
            obj_dict[sector] = sector_dict
        
        self.all_sectors_var_objects_dict = obj_dict
        return obj_dict
    
    #_____________________________________________________________________________________________________________________________________________
    def _run_earth4all(self, var_check=False):
        """
        Run an unsorted sequence of updates of the 5 sectors, and reschedules
        each loop computation until all variables are computed.
        """
        from copy import deepcopy
        all_sectors_var_objects_dict = self.dict_of_var_objects() # Create dict of variable objects

        all_sectors_var_names_list = {sector: list(variable_dict.keys()) for sector , variable_dict in deepcopy(all_sectors_var_objects_dict).items()} # Copy and save as attr and remove items at update
        temp_all_sectors_var_names_list =deepcopy( all_sectors_var_names_list)

        self.var_check=var_check   # For error checking
        n = self.n # Cache n         
        all_sectors_demo_values_dict={}
        for sector in self.sectornames_list:
            all_sectors_demo_values_dict.update(getattr(self, f"{sector}_demo_values_dict"))
        setattr(self, "all_sectors_demo_values_dict", all_sectors_demo_values_dict)
                
        self.redo_loop = True
        if self.verbose:
            print(f"\n{'_'*30} K = 0 running: ")#{'_'*30}")        
        #______________________________ First loop at k = 0 __________________________________________        
        self.round=0
        while self.redo_loop:
            
            if self.var_check=="Loop":
                self.print_current_state() # print all variables
                input(f"\n{'#  CONTINUE  #':_^100}\n")                         
            
            self.round+=1
            self.redo_loop = False

            for sector in self.sectornames_list:
                setattr(self, "times_demo_used", 0) #* Moved here from loop0                
                self.current_sector=sector
                self.loop0_sector(sector=sector)
        
        print()
        print(f"{' Starting Loop k=1 to Kmax ':^150}\n")    

        print(f"\n{'':_^150}\n{' Starting looping from k = 0 -> k = '+str(n):^150}\n")        
        print(f"{'k = '+f'{1}/{n} -> |':>20}{'':_>99}| <-> (100)" , end="" , flush=True)

        #______________________________________________ Loop k __________________________________________________
        for k_ in range(1, n):
            self.k=k_
            round_count = self.round
            self.round=0  # Counter of update rounds            
                        
            temp_all_sectors_var_names_list = deepcopy(all_sectors_var_names_list)

            if True:#self.verbose: 
                if k_%(n//100)==0 or k_==1: 
                    progress = k_/(n//100) # Percentage of completion                    
                    print(f"\r{'k = '+f'{k_}/{n} -> |':>20}{('*'*int(progress)):_<100}|  -> ({progress:.2f}%)" , end="" , flush=True)
                    if k_ == n:
                        print("\n\n Finished simulation... \n\n")



            self.redo_loop = True
            while self.redo_loop:
                if self.verbose: 
                    print(f" *** round nr : {self.round}")                
                if self.var_check=="Loop":                                      # Print current state at k, at current round of updating
                    self.print_current_state()                              
                    input(f"\n{'#  CONTINUE  #':_^100}\n")                 
                elif isinstance(self.var_check, int) and self.var_check!=0:     # If checking at a given multiple of k          
                    if k_%self.var_check==0:
                        self.print_current_state()                          
                        input(f"\n{'#  CONTINUE  #':_^100}\n")
                self.round+=1
                self.redo_loop = False                                
                for sector in self.sectornames_list:                                                                                                 
                    self.current_sector=sector                    
                    self.loopk_sector(sector=sector, k=k_ , objs_ordered=all_sectors_var_objects_dict , names_listed=temp_all_sectors_var_names_list)                            
            if self.verbose:
                print(f"{'':_^150}\n Finished loop K = {k_} , in {self.round} rounds")

    #_____________________________________________________________________________________________________________________________________________
    def __str__(self): 
        return  f"\n\n{' Earth4All model class object: ':~^150}\n\n"\
                f"{'':^10}{'':_^10}{' Simulating over timespan: ':_<30}{'year:':>10}{self.year_min:>10} -> {self.year_max:<10} with timestep dt={self.dt} [years]\n"\
                f"{'':^10}{'':_^10}{' k-stepper with steps: ':_<30}{'k:':>10}{self.k:>10} -> {str(self.n):<10} number of steps n = {self.n}\n"\
                f"{'':^10}{'':_^10}{'':_^30}{' Demo = '+str(self.demo):^20}{'':<10}    verbose = {self.verbose} \n{'':~^150}\n\n"                 

    #_____________________________________________________________________________________________________________________________________________
    def get_dict_of_all_variables(self):
        full_dict={}
        for sector in self.sectornames_list:            
            variable_dict = self.all_sectors_variables_dict[sector]
            full_dict.update(variable_dict)
        return full_dict

    #_____________________________________________________________________________________________________________________________________________
    def print_current_state(self):
        full_dict=self.get_dict_of_all_variables()
        full_demo_values_dict= getattr(self, "all_sectors_demo_values_dict") # Gets values from demo as dict

        k=self.k        
        year = self.time[k]  # demo uses year now because of how the dict is set up        
        if self.dt==1:
            year=int(year)
        print(f"{' All variable values at k = ':_>100}{ str(k)+' <-> year = '+str(year) :_<100}")

        names_listed=list(full_dict.keys())

        for i, var_name in enumerate(names_listed):
            
            value=getattr(self, var_name )[k] #* Should work with Variable object as well.                        
            demo_value= full_demo_values_dict[var_name][k] # For comparing                                                    
            demo_value = float(demo_value)
            
            rel_err="_"            
            if not np.isnan(value):
                diff = value - demo_value
                if abs(demo_value)<1e-6:
                    demo_value= 1e-6
                rel_err =  diff / demo_value                                                 
                
            color="" # if no printing color
            color_end=""
            if value==np.inf: # make red if we get infinite value
                color='\033[30;101m'
                color_end='\033[0m'     # Reset color
            elif not np.isnan(value) : # make green if we have calculated the value
                color='\033[32m'
                color_end='\033[0m'     # Reset color
            error_color=""
            if rel_err=="_":
                pass
            elif abs(rel_err)<1e-5: # Almost no error
                error_color='\033[32m'
                rel_err="~0"
            elif abs(rel_err)<1e-1: # Small error # 10%, used 1 before
                error_color='\033[32m'  
            elif abs(rel_err)>=1e-1: # Large error
                error_color='\033[33;101m'
            
            print(f"{color}{var_name:^14.14}= {value:<10.4}{color_end}{error_color}(y_d={demo_value:>9.4}) {color_end}|", end="")            
            if i%6==0:
                print("\n", end=" |")        
        print(f"{' finished round ' + str(self.round) + ' at step k = ':_>100}{ k :_<100}")     
    
    #_____________________________________________________________________________________________________________________________________________
    def generate_demo_values(self, demo_version="tltl" , all_values=False):                
        for sector_name in self.sectornames_list:
            self.current_sector=sector_name            
            self.general_add_demo_values(sector=sector_name , run_version=demo_version , all_values=all_values)                             
                             