import numpy as np
#___________________________________________________________ RAMP _________________________________________________________________________________


def ramp(x, slope, startx, endx):
	''' Function definition in Julia:
	ramp(x, slope, startx, endx) = IfElse.ifelse(x > startx, IfElse.ifelse(x < endx, slope * (x - startx), slope * (endx - startx)), 0)
	Description from Julia: 
    `ramp(x, slope, startx, endx)`

	Returns `0` until the `startx` and then slopes upward until `endx` and then holds constant. This function corresponds to the `RAMP` function in the `VENSIM` language.
	
    Example from vensim: 
	{RAMP( "Goal for extra fertility reduction (1)" / Introduction period for policy y , 2022, 2022 + Introduction period for policy y)}_[1]
	
	Coreresponds to:
	ramp(x=k, slope=("Goal for extra fertility reduction (1)" / Introduction period for policy y) , startx=2022, endx=(2022 + Introduction period for policy y))
	'''
		
	if x<=startx:
		return 0
	#if x > startx: 
	if x < endx:
		return slope * (x - startx) # Where slope is some slope or derivative f'(x) of some function f(x), This will give df(x)/dx * delta_x == f(x)
	# If after slope
	return slope * (endx - startx) # Same thing but after the slope has peaked and stagnated. Gives a flat graph after endx. 	



#__________________________________________________________ CLIP __________________________________________________________________________________

def clip(gte_return_value, lt_return_value, input_value, threshold):

	''' Dont yet know where this is used, might be for control only.'''

	'''
	Compares the passed input value and compares it to a given threshold.
	Returns a certain value if the input is greater or equal, and another value if the input is less than the threshold.

	######## Arguments:
	gte_return_value : value to return if the input is greater or equal ,
	lt_return_value : value to return if the input is less than, 
	input_value : value to check,
	threshold : threshold value that the input is compared to
	'''

	''' Function definition in Julia: 
	# `clip(returnifgte, returniflt, inputvalue, threshold)` : 
	# Name explanation: returnifgte : return if greater than or equal , 
	# returniflt : return if less than,
	# inputvalue : value compared, 
	# threshold : value that the input is compared to
	# 
	# Returns `returnifgte` if the value `inputvalue` is greater than (or equal to ) the threshold `threshold`, `returniflt` otherwise. This function corresponds to the `CLIP` (also called `FIFGE`) function in the `DYNAMO` language.
	clip(returnifgte, returniflt, inputvalue, threshold) = IfElse.ifelse(inputvalue ≥ threshold, returnifgte, returniflt)
	
	######### Add description of how it is called and so on
	'''
	
	return gte_return_value if input_value >= threshold else lt_return_value
	
	
#_________________________________________________________ STEP ___________________________________________________________________________________

def step(input_value, gte_return_value, threshold):
	''' Returns a certain value if the input has passed the threshold value (is greater than or equal)
	Otherwise the function returns 0
	
	############ Arguments:
	# gte_return_value : return this value if greater than or equal? , 
	# input_value : value compared, 
	# threshold : value that the input is compared to

	####### Alternative way of defining this function:
	step(inputvalue, returnifgte, threshold) = clip(gte_return_value, 0, input_value, threshold)
	'''
	''' Function definition in Julia: 
	`step(inputvalue, returnifgte, threshold)`
	# Name explanation: 
	# returnifgte : return if greater than or equal, 
	# inputvalue : value compared, 
	# threshold : value that the input is compared to
	
	Returns `0` if the value `inputvalue` is smaller than the threshold `threshold`, `returnifgte` otherwise. This function corresponds to the `STEP` function in the `DYNAMO` language.
	'''
	return gte_return_value if input_value >= threshold else 0

	

#_____________________________________________________ PULSE _______________________________________________________________________________________	
	

def pulse(input_value, start, width):
	'''
	Works as an activation pulse, returns 1 within a given time-interval
	returns 0 at all other times. (Similar to a combination of heavyside-functions: u( k-start ) - u( k-(start+width) ) )
	Creates a behaviour like: 

			|start			|start+width
	________|---------------|____________				# "_" = 0 , "-" = 1
	'''

	""" From Julia:
	`pulse(inputvalue, start, width)`
	Returns 1.0, starting at time start, and lasting for interval width; 0.0 is returned at all other times. If width is passed as 0 it will be treated as though it were the current value of TIME STEP. This function corresponds to the `PULSE` function in the `VENSIM` language.
	pulse(inputvalue, start, width) = IfElse.ifelse(inputvalue >= start, 1, 0) * IfElse.ifelse(inputvalue < (start + width), 1, 0)
	This becomes same as:  if input gte start and input lt start+width -----> return 1 , else return0
	"""
	

	#end= start+width # End of pulse

	'''started= input_value >= start # Should be boolean; True if input value is greater than or equal to start value. ie. pulse started
	not_ended= input_value < start+width # Should be boolean; True if input value is less than start value. ie. pulse not yet ended
	#print("Read pulse ")
	if started and not_ended: # If our input is within the interval of the pulse
		return 1
	else:	# If not within the pulse
		return 0
	'''
	#	   1 if  pulse started 			and not ended, else 0 
	return 1 if start <= input_value < (start + width) else 0
	



#________________________________ IF THEN ELSE ____________________________________________________________________________________________________________

def if_then_else(condition, true_value, else_value ): 
	'''Evaluates a condition and returns one value if true, another if false. If neither it raises an error'''
	'''if condition:#==True:
		return true_value
	elif not condition:#==False:
		return else_value
	else:
		raise TypeError()'''
	
	return true_value if condition else else_value	



#______________________________________________________ INTEG ______________________________________________________________________________________




def integ( x, dx_dt, dt , initial_value):#def integ(x, input, delay_time):
	'''
	x = previous state 
	dx_dt = rate of change of x with respect to t
	dt = the delta t step of the simulation

	initial_value= x[k=0]= x[t_0]

	next state = current state + integration( dx_dt * dt )    |t0<t<t0+dt


	'''
	initial_value="0"	

	#try:
	if initial_value is None or initial_value=="0":
		initial_value=x
	

	return initial_value + dx_dt * dt


#______________________________________________________ SMOOTH ______________________________________________________________________________________

def smooth(x, input_value, delay_time, dt):
	''' Exponential smoothing
	x = previous state 
	input_value = real input to be smoothed out to make up for delay_time
	dt = the delta t step of the simulation

	initial_value= x[k=0]= x[t_0]

	next state = current state + integration( dx_dt * dt )    |t0<t<t0+dt

	According definition in Vensim language:
		The SMOOTH function is commonly used to take time averages and represent expectations.  It is different from LN, EXP and IF THEN ELSE in that it has time behavior built into it.  That is, if you know what value x takes on then you can compute EXP(x), but just knowing x does not tell you the value of SMOOTH(x,4), you also need to know what value the SMOOTH previously had.  This is because the SMOOTH function has a level implicitly built into it.
		We will write the equation
		expected demand=SMOOTH(demand, time to form expectations)
		This equation is exactly the same as:
		expected demand =INTEG((demand-expected demand)/ time to form expectations,demand)

	'''
	# ______________________________ This is according to definition by VensimPLE ______________________________
	# If delay_time < dt -> we will get a too large rate of change and end up with oscillation instead of smoothing.
	# in that case we use dt as the smoothing delay_time
	delay_time = max( delay_time , dt )
	# ______________________________

	#previous_state = x
	rate_of_change= ( (input_value - x) / delay_time )# Defines the derivative of x with resepect to t. A constant because the rate is constant at a given time
	

	#next_state_of_x=integ( x, rate_of_change, dt , x ) #dx_dt=rate_of_change 
	return integ( x, rate_of_change, dt , x ) #dx_dt=rate_of_change 




#______________________________________________________ SMOOTHI ______________________________________________________________________________________


def smoothi(x, input, delay_time, initial_value, dt):
	'''I believe that this will work the same currently 
	because we dont work with inital values as separate parameters
	They are always initiated in init_e4a_variables anyway'''
	#if np.isnan(input):
	#	raise 

	if  np.isnan(x):
		#print("Init value from external variable: ",  initial_value, " , x= ", x)
		x=input		
	return smooth(x, input, delay_time, dt)




#______________________________________________________ WITH LOOKUP ______________________________________________________________________________________	

def with_lookup( x_input, values ):
	'''
	called like this:
	with_lookup( x_input, ( [min_max_values] ,  (x_1, y_1) , (x_2, y_2) , ... , (x_n, y_n)   ) )
	'''	

	# Gets min and max values
	(x_min, y_min), (x_max, y_max) = values[0]

	#min_max_pairs = values[0] #[min_max_values]
	#min_values, max_values = min_max_pairs
	#x_min , y_min = min_values
	#x_max , y_max = max_values

	#left, right = y_min , y_max #( to return left if x_input = 0 , and right if in = -1)

	values=np.array(values[1:], dtype=np.float64) # remove inits

	#x_values=values[ : , 0]
	#y_values=values[ : , 1]

	

	#x_values=np.empty((len(values), 1))
	#y_values=np.empty((len(values), 1))
	#x_values=[]	
	#y_values=[]	
	x_values, y_values = values[:, 0], values[:, 1]	

	#for x_y_pair in values:
	#	x, y= x_y_pair
	#	x_values.append(x)
	#	y_values.append(y)

	#evaluates f(x) at x= x_input
	# does so by linearly interpolating between given value_pairs
	result=np.interp(x_input, xp=x_values, fp=y_values, left=y_min, right=y_max)

	return result



#______________________________________________________ DELAY ______________________________________________________________________________________	

class Delay_Nth_order:
	'''Implements DELAY N function.
		Parameters
		----------
		delay_input: callable
			Input of the delay.
		delay_time: callable
			Delay time.
		initial_value: callable
			Initial value.
		order: callable
			Delay order.
		tsetp: callable
			The time step of the model.
		py_name: str
			Python name to identify the object.
		Attributes
		----------
		state: numpy.array or xarray.DataArray
			Current state of the object. Array of the delays values multiplied
			by their corresponding average time.

		times: numpy.array or xarray.DataArray
			Array of delay times used for computing the delay output.
			If delay_time is constant, this array will be constant and
			DelayN will behave ad Delay.
		'''
	
	
	'''
	Example of Vensim call: ( DELAY N(input,delay time, initial value, order) 		#	N'th order exponential delay )

	'Passing 20 Mp/y'==={DELAY N("Births Mp/y", 20, "Passing 20 in 1980 Mp/y", Order)}_[y]'''
	
	# Needs to be called when initiating the model, then when calling the delay function, it should only call the __call__
	#   Called to create the delayfunction for the variable that uses this delay
	def __init__(self, varname, initial_value=0, delay_time=None,input_var=None, order_N=3 , dt=1, method="euler"):
		self.input_variable = input_var  # Input signal used, in call we can send specific value instead
		delay_time = max(dt , delay_time) # If using very big dt, shouldnt be used
		self.delay_time = delay_time    # total delay time, often a constant 20, sometimes a variable , could be a variable name, must be bigger than order
		self.initial_value = initial_value # Will always be a constant param i believe
		self.order_N = order_N                      # Number of stages <=> order, can not change
		self.dt = dt                    # Simulation time step
		self.method=method
		self.delays_current_k = -1


		self.times= np.full(order_N, delay_time) # Needed if our delay_time can change


		self.varname = varname
		# Initialize vector of N stages,	example of N = 4 and initial value= 0: 
		#	stages=   | x1[k] |   =   | 0 |		
		#		      | x2[k] |   =   | 0 |
		#		      | x3[k] |   =   | 0 |
		#		      | x4[k] |   =   | 0 |
		#	updated via:
		# 		      | dx1[k] / dt |   =   | (input - x1 ) / (delay_time/4) | 
		#		      | dx2[k] / dt |   =   | (  x1  - x2 ) / (delay_time/4) | 
		#		      | dx3[k] / dt |   =   | (  x2  - x3 ) / (delay_time/4) | 
		#		      | dx4[k] / dt |   =   | (  x3  - x4 ) / (delay_time/4) | 
		# Returns the last derivative dx4[k] / dt, to compute the first step towards the goal value of the input. 
		# Either of these:		
		self.states = np.full(order_N, initial_value)  # Initialize the N states to the initial value    # Creates: [ init_val  , init_val  , init_val  , init_val ]
		self.init_delay() # initialize according to init value

	def init_delay(self, initial_value=None): # Probably not needed
		'''This method initializes the state variables and delay times, 
		setting the initial state of the delay system based on the delay order and delay time.'''				
		# Order is already assigned	

		# We want the first outflow to be the initial value 
		#			  | dx1[k] / dt |   =   | (input - x1 ) / (delay_time/4) | 
		#		      | dx2[k] / dt |   =   | (  x1  - x2 ) / (delay_time/4) | 
		#		      | dx3[k] / dt |   =   | (  x2  - x3 ) / (delay_time/4) | 
		#		      | dx4[k] / dt |   =   | (  x3  - x4 ) / (delay_time/4) | 
		# meaning x4 / (delay_time/N) = 20
		# means x4 = 20 * (delay_time/N)
		
		if initial_value is None: # If no inital value, calculate inital values based on initial der function
			init_state_value = self.initial_value * (self.delay_time / self.order_N) # initial_value * delay_time

		else:
			init_state_value = initial_value * (self.delay_time / self.order_N) # Same thing but with initialize arg
		self.states = np.array( [init_state_value] * self.order_N ) # Create vector of the states at the different stages; x1[k], x2[k] ...
		
	
	def __call__(self, k, input_value,  delay_time,  *args ):#current_value=None ): # Passes args, not needed, just dont want to remove them from function call
		'''This method allows the object to be called like a function. 
		When called, it returns the final output of the delay.
		
		the current state plus the derivative becomes the next state of the delay, last outflow is the returned output
		update the state after the call '''		

		#--------------------------------- Get the final outflow to return
		# Given this: | dx4[k] / dt |  =  | (  x3  - x4 ) / (delay_time) | * N	 
		# The outflow is (x4 / delay_time)*N		
		final_outflow = (self.states[-1] / self.times[-1]) * self.order_N # FIXME (unsure about how times works, but to me this index seems more logical)				
		
		# Update the derivatives once at each step k: # update based on current state
		derivatives = self.ddt(input_at_k = input_value, delay_time_at_k = delay_time)  # calculate and get the derivatives
		self.update_delay_state(derivatives=derivatives) # Use the derivatives to update the delay levels
		
		return final_outflow , self # return the last outflow (delayed input)
	
	def update_delay_state(self, derivatives):
		'''
		Takes in a vector of all the derivatives of the levels on the form: '''
		# Derivatives:
		#  | dx1[k] / dt |  =  | input - ( x1 /(delay_time) ) | * N	 	
		#  | dx2[k] / dt |  =  | (  x1  - x2 ) / (delay_time) | * N	 	    
		#  | dx3[k] / dt |  =  | (  x2  - x3 ) / (delay_time) | * N	 	    
		#  | dx4[k] / dt |  =  | (  x3  - x4 ) / (delay_time) | * N	 	 
		
		# Update levels via:
		#  | x1 | =   |x1| + | dx1[k] / dt | * dt
		#  | x2 | =   |x2| + | dx2[k] / dt | * dt   
		#  | x3 | =   |x3| + | dx3[k] / dt | * dt   
		#  | x4 | =   |x4| + | dx4[k] / dt | * dt

		current_state = self.states # Gets vector of current state of all delay levels - first column in above eq.

		#   x_(i+1) = | x_i + (dx_i / dt)*dt | # General for any i
		updated_state = current_state + derivatives * self.dt

		self.states = updated_state # Asser new state as current state


	
	def ddt(self, input_at_k, delay_time_at_k):
		'''This method calculates the rate of change (derivative) of the delayed state variables.'''

		#Roll array elements along a given axis.
		
		# Update delay times __________
		#Elements that roll beyond the last position are re-introduced at the first.
		self.times = np.roll(self.times, 1, axis=0) # Move along delay times, last is thrown away in next step

		# Update the first time step with the current delay time.
		self.times[0] = delay_time_at_k # In this implementation, the delay_time remains the same except for deaths (takes in LE at 60)
		# Updated delay times __________												
		
		############# Calculate the derivatives according to this function:
		# for example: | dx2[k] / dt |   =   | (  x1  - x2 ) / (delay_time/order_N) |
		
		# Calculate outflows: divide the state by the corresponding time steps. (state likely is the vector x1, x2, and so on til xN)
		# Gives -> vector outflows: 			(T_D <-> delay_time)
		#	| x1 / T_D | * N
		#	| x2 / T_D | * N
		#	| x3 / T_D | * N and so on... for  N
		outflows = (self.states / self.times )* self.order_N # What flows forward and out from each level of the delay state

		#Previous state:
		#	| x1 |
		#	| x2 |
		#	| x3 |
		#previous_state = self.states
		 
		# Calculate inflows: shift the outflows forward by one step using numpy's roll. Outflows from x_i is inflow at x_(i+1).
		# Gives -> vector: 			
		#	| x3 / T_D |* N
		#	| x1 / T_D |* N
		#	| x2 / T_D |* N and so on... for 
		inflows = np.roll(outflows, 1, axis=0) # Previous state rolled divided by times

		# Set the first inflow to be the input function value, representing the new input into the delay system.
		# Gives -> vector: 					
		#	|   input  |
		#	| x1 / T_D |* N
		#	| x2 / T_D |* N and so on... for 
		inflows[0] = input_at_k # self.input_func() # Asserts the input as inflow to the first level

		rate_of_change = inflows - outflows

		# Return the difference between inflows and outflows, multiplied by the order of the delay.
		# This gives the rate of change of the delay system.
		# Gives -> vector: 									
		#   | input - ( x1 /(delay_time) )* N |   	= 	| dx1[k] / dt | 
		#   | (  x1  - x2 ) / (delay_time)    | * N	= 	| dx2[k] / dt |    
		#   | (  x2  - x3 ) / (delay_time)    | * N	= 	| dx3[k] / dt |    
		#   | (  x3  - x4 ) / (delay_time)    | * N	= 	| dx4[k] / dt |   
		
		
		return rate_of_change # returns the derivative of each delay level
	
	def __str__(self):		
		return ""

