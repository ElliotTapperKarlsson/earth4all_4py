import numpy as np

from sympy import symbols, lambdify, sympify , Function 
import sympy as sp

class Variable:
    ''' Class used for the model variables '''
    def __init__(self, name, vensim_name = None, jl_name = None, vars_required = None, params_required = None, state_variable = False, equation_string=None, values=None, variable=True , demo_values=None):
        self.name=name
        self.vensim_name = vensim_name
        self.jl_name = jl_name
        self.vars_required = vars_required
        self.params_required = params_required                 
        self.state_variable = state_variable        
        self.equation_string = equation_string              
        self.variable =variable        
        
        if not isinstance(values, np.ndarray):  
            values=np.full((201,), np.nan)    #Set a more appropriate length based on tltl run
        self.values=values #Either std array, or passed tltl or gl run, or full(nan) array of certain length
        
        self.demo_values = demo_values # For storing demo variables to compare to

        if name=="pnis": # "pnis": "##RAND_PINK_NOISE", essentially=1 # This specific variable is used as noise to make the model stochastic, this is currenlty not in use
            equation_string = '1'        
        
    
    def __getitem__(self, k): #Called through variable[k] to get the value
        return self.values[k]
    

    def __setitem__(self, k, value): #Called through variable[k]= value to assign value
        self.values[k]=value    

    def compile_equation(self , dict_of_required):

        equation = compile(self.equation_string, "<string>", "eval" )
        self.equation = equation 


    def compute_value(self,k, dict_of_required_additional):
        #Uses the precompiled function to calculate the result at a given k 
        # dict_of_required_additional should be a dictionary of required variables        
        
        dict_of_required = self.dict_of_required
        dict_of_required.update(dict_of_required_additional)
        if k==0:            
            self.compile_equation(dict_of_required)
            #equation = self.equation    

        
        
        return eval( self.equation , dict_of_required ) # dict_of_required is same as dict of required          
        
   
    def initiate_eq(self, equation_string , dict_of_required):
        '''Now used as a setter of the equation_string and creating the truncated dict_ of req for compiling and calculating'''

        if self.name=="pnis": # "pnis": "##RAND_PINK_NOISE", essentially=1
            equation_string = '1'
        equation_string=equation_string.replace("^", "**")
        self.equation_string = equation_string       
        
        # keep only required variables and functions that actually exist in the eq_string
        self.dict_of_required = {key: value for key, value in dict_of_required.items() if key in equation_string}
        
        self.compile_equation(dict_of_required)


    def __str__(self):
        return self.name

        


class Parameter:    # For constants and parameters or attributes or whatever

    def __init__(self, name, vensim_name=None, name_jl=None, value=None):
        self.name=name
        self.vensim_name=vensim_name
        self.name_jl=name_jl
        self.value=value

    def __getattribute__(self, value=True):
        return self.value    
    