from functools import wraps
import matplotlib.pyplot as plt
from matplotlib.ticker import EngFormatter
from matplotlib.image import imread
from scipy.interpolate import interp1d
import json
import numpy as np
from importlib.resources import open_text
import pandas

def fetch_all_demo_values_from_df(demo_run_type , sector ):
    ''' Meant for getting values into demo dict'''
    file_name = str(sector)+".csv"
    with open_text(f'earth4all_4py.vensim_var_outputs.dataframes.{str(demo_run_type)}', file_name ) as csv_file: # open file
        data_frame = pandas.read_csv(csv_file)    

    if 'Unnamed: 0' in data_frame.columns:
        data_frame = data_frame.drop(['Unnamed: 0'] , axis = 1) 
    
    years = data_frame['time (year)'].astype(float).to_numpy() 
    year_min =years[0] 
    year_max =years[-1]     
    
    n = int( len(list(years)) ) # Generate n value <-> Same as k_max+1             
    years = np.linspace(year_min, year_max, n )       # Defines the actual time-space, creates a linspace covering all timesteps with correct dt        
    data_frame = data_frame.drop(['time (year)'] , axis = 1)
    dict_data = {column: data_frame[column].to_numpy() for column in data_frame.columns}    # Store columns in dictionary    
    
    return dict_data , years # Returns dict of variablenames: values array , as well as time array

def demo_values_df(sector, run="tltl" , dt=1, time=np.nan , all_values =False):        
    '''Fetched data from pandas dataframe and stores values corresponding to the time used, via interpolation.'''                
    var_name_values_dict, demo_years = fetch_all_demo_values_from_df(demo_run_type = run , sector = sector) #* If all already placed in .csv file (after 20th nov 2024)        

    for variable_name, values_array in var_name_values_dict.items(): # Goes through each variable                                    
        #----------------------------------- Create continous function by interpolating ---------------------------------                    
        demo_values_function = interp1d(x= demo_years, y= values_array,  kind='linear', axis=-1, copy=True, bounds_error=None, fill_value=np.nan, assume_sorted=True)    
        #---------------------------------#---------------------------------#---------------------------------#                        
        interpolated_values = demo_values_function(time) # Vectorized interpolation                        
        var_name_values_dict[variable_name] = interpolated_values # Replace with interpolated values                

    return var_name_values_dict #Returns dict of dicts per var    
            

def requires( outputs=None, inputs=None, check_at_init=True, check_after_init=True): # Generate decorator
    #This function is first called, but returns the decorator 
    """
    Decorator generator to reschedule all updates of current loop, if all
    required inputs of the current update are not known.
    outputs - means the variable to be computed
    inputs - the required variables

    called via: @requires

    """
    
    def requires_decorator(updater): #Meant to wrap a variable updater to check a requirement
        '''The decorator called via: @requires()'''        
        
        @wraps(updater) # functools.wraps() used to maintain the right name and doc of the wrapped func (metadata)
        def requires_and_update(self, variable, inputs, *args, req_met=True, state_variable=False): #wrapped updater, check req and if redo loop , unknown nr of args (*)            
		    # This function will be the updater func but with wrapped req functionality		    
		    # where requires returns the function requires_and_update(self, *args)
            #*args means that it can take any amount, args[0] will be k             
            k = args[0]
                        
            inputs_req_dict = {} # NOTE Tried passing all values immediately
            if inputs==[None]:
                #print(f"Inputs used in requires is: {inputs}, Means that we pass")
                pass
            elif (inputs is not None): # If there is a requirement                                                
                
                for input_ in inputs:
                    input_ =input_.lower()#*testing

                    if input_ == variable.name: # State variable requires its own previous value (always fulfilled requirement) 
                        continue

                    input_val = getattr(self, input_ )[k] #Fetches the array with given variable name, self here is self from where updater is called                    

                    if np.isnan(input_val): #Checks if the required value has been computed , true if not
                        
                        self.redo_loop = True # Req not met, loop again
                        req_met=False
                        # Return without going into the updater
                        return False # Indicates unsuccessful update
                    inputs_req_dict[input_] =input_val
                                            
            return updater(self, variable, inputs_req_dict, *args, req_met, variable.state_variable) # Runs the updater with given args and returns #its output (likely is no) 

        return requires_and_update #Returns the wrapped/decorated function

    return requires_decorator # Returns the decorator function, from the decorator generator 

def get_eqs_from_json( sector):        
        
        file_name=f"{sector}_var_equations.json" # Define filename
        #------------                        
        with open_text('earth4all_4py.vensim_model_files.json_eq_files', file_name ) as eq_file: # open file
            return json.load(eq_file)


def alt_plot_world_variables(
    time,
    var_data,
    var_names,
    var_lims,
    img_background=None,
    title=None,
    figsize=None,
    dist_spines=0.09,
    grid=False,
    line_styles=["-"],  # New parameter for line styles
    line_widths=1
):
    """
    Plots a set of variables across the simulation span with optional customization.
    Parameters:
        time (array-like): Time values.
        var_data (list of array-like): Data for each variable.
        var_names (list of str): Names of the variables.
        var_lims (list of tuple, optional): Y-axis limits for each variable.
        img_background (str, optional): Path to background image.
        title (str, optional): Plot title.
        figsize (tuple, optional): Figure size.
        dist_spines (float, optional): Distance between y-axis spines.
        grid (bool, optional): Enable grid for the first subplot.
        line_styles (list, optional): Line styles for each variable.
        line_widths (float or list, optional): Line widths for each variable.
    """
    # Determine the number of variables
    var_number = len(var_data)

    cmap = plt.get_cmap("tab10")  # Get the specified colormap -> palette (str): Matplotlib colormap name (e.g., 'tab10', 'viridis').
    colors = [cmap(i / var_number) for i in range(var_number)]  # Generate distinct colors
    
    # Create subplots with shared x-axis and multiple y-axes
    fig, host = plt.subplots(figsize=figsize)
    axs = [
        host,
    ]

    for i in range(var_number - 1):        
        axs.append(host.twinx())

    # Adjust spacing between subplots
    fig.subplots_adjust(left=dist_spines * 1)
    for i, ax in enumerate(axs[1:]):
        ax.spines["left"].set_position(("axes", -(i + 1) * dist_spines))
        ax.spines["left"].set_visible(True)
        ax.yaxis.set_label_position("left")
        ax.yaxis.set_ticks_position("left")

    # Add background image if provided
    if img_background is not None:
        im = imread(img_background)
        axs[0].imshow(
            im,
            aspect="auto",
            extent=[time[0], time[-1], var_lims[0][0], var_lims[0][1]],
            cmap="gray",
        )

    # Plot data for each variable
    ps = []
    for i, [label, ydata, color, line_style, line_width] in enumerate(zip( var_names, var_data, colors, line_styles, line_widths) ): #Added line styles+ widths
        
        # Calculate the index of the axis to plot on
        ax_index = i % len(axs)
        ax = axs[ax_index]
        # Plot augmented lines with decided line style and widths
        ps.append(ax.plot(time, ydata, label=label, color=color, linestyle=line_style, linewidth=line_width)[0])
    axs[0].grid(grid)
    axs[0].set_xlim(time[0], time[-1])

    # Set y-axis limits for each subplot
    for ax, lim in zip(axs, var_lims):
        if lim is not None:
            ax.set_ylim(lim[0], lim[1])

    # Format y-axis labels and ticks
    for ax_ in axs:
        formatter_ = EngFormatter(places=0, sep="\N{THIN SPACE}")   # Define formatter for y-axis labels with engineering notation and no decimal places
        ax_.tick_params(axis="y", rotation=90)  # Rotate y-axis labels by 90 degrees for better readability
        ax_.yaxis.set_major_locator(plt.MaxNLocator(3))#5 # Set the major locator for y-axis to ensure a maximum of x ticks
        ax_.yaxis.set_major_formatter(formatter_)   # Apply the formatter to the y-axis labels for engineering notation

    # Format x-axis labels and ticks
    tkw = dict(size=1, width=1.5)#1.5)               # Define tick parameters for x-axis and y axis
    axs[0].set_xlabel("time [years]")           # Set the label for x-axis
    axs[0].tick_params(axis="x", **tkw)         # Apply tick parameters to x-axis
    for i, (ax, p) in enumerate(zip(axs, ps)):          # Set the y-axis label, color, and position for each subplot
        ax.set_ylabel(p.get_label(), rotation=45)#60)      # Set y-axis label
        ax.yaxis.label.set_color(p.get_color())                  # Set y-axis label color
        ax.tick_params(axis="y", colors=p.get_color(), **tkw, pad=-3)    # Apply tick parameters to y-axis
        ax.yaxis.set_label_coords(-i * dist_spines  ,1.01)#+(0.05-i*0.05) #+ (0.05 -i*0.01 ) , 1.01)        # Adjust y-axis label position      #Added for horizontals move
    
    # Add title if provided
    if title is not None:
        fig.suptitle(title, x=0.9,y=0.85, ha="right", fontsize=8)

    # Adjust layout for better visualization
    #plt.tight_layout()
    #fig.tight_layout()


