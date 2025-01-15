import unittest
import matplotlib.pyplot as plt
from earth4all_4py.utils.e4a_utils import alt_plot_world_variables
from earth4all_4py.earth4all import Earth4All as Earth4All

class TestEarth4PythonModel(unittest.TestCase):
    
    def setUp(self):
        """Setup code for preparing the test environment."""
        print("Setting up the test environment...")
        self.dt = 0.015625  # Default time step for tests
        self.model = None

    def test_running_demo(self):
        """Test the running of the model using the demo configuration."""
        print("_"*20, " Running DEMO test ", "_"*50)
        demo_model = self.run_the_model(demo="DEMO", dt=self.dt)
        
        self.assertIsNotNone(demo_model)
        self.assertGreater(len(demo_model.time), 0, "Demo model should have time data.")
        
    def test_running_full_model(self):
        """Test running the full Earth4All model."""
        e4a_model = self.run_the_model(demo="tltl", var_check=False, dt=self.dt)
        
        self.assertIsNotNone(e4a_model)
        self.assertGreater(len(e4a_model.time), 0, "Earth4All model should have time data.")
        
        print(f"\n{'_'*50}\n\n      Nr of times demo was used: {getattr(e4a_model, 'times_demo_used')}\n{'_'*50}\n")
        
    def test_plotting(self):
        """Test plotting functionality."""
        e4a_model = self.run_the_model(demo="tltl", var_check=False, dt=self.dt)
        self.plot_essentials(e4a_model, demo_model=True)

    def run_the_model(self, demo=False, var_check=False, dt=1):
        """Helper method for running the Earth4All model."""
        all_values = False
        if dt == "all":
            all_values = True
            dt = 1  # Won't be used

        model = Earth4All(demo=demo, dt=dt, all_values=all_values)
        model.init_e4a_constants()
        model.init_earth4all_variables()
        model._run_earth4all(var_check=var_check)

        return model

    def plot_essentials(self, model, demo_model=None):
        """Helper method for plotting model variables."""
        plot_variables = ["pop", 'awbi', 'ow']  # Variables to plot
        title = f"Plot of "
        time = model.time
        var_data = []
        var_names = []
        var_lims = []
        line_styles = []
        line_widths = []

        full_demo_values_dict = getattr(model, "all_sectors_demo_values_dict")

        for var in plot_variables:
            var_values = getattr(model, var)
            var_data.append(var_values)
            var_names.append(var)
            var_lims.append((min(0, min(var_values)) * 1.1, max(var_values) * 1.1))
            title += f" {var} "
            line_styles.append("-")
            line_widths.append(3)

            # Only used if demo values are printed
            if demo_model is not None:
                demo_var_values = full_demo_values_dict[var]
                demo_var_values = demo_var_values.reshape(-1)
                var_lims.append((min(0, min(demo_var_values)) * 1.1, max(demo_var_values) * 1.1))
                var_data.append(demo_var_values)
                var_names.append(var + "_d")
                line_styles.append(":")
                line_widths.append(2)

        attributes_dict = {
            'var_data': var_data,
            'var_names': var_names,
            'var_lims': var_lims,
            'line_styles': line_styles,
            'line_widths': line_widths,
        }

        alt_plot_world_variables(
            time=time,
            **attributes_dict,
            img_background=None,
            title=title,
            figsize=[12, 7],
            dist_spines=0.09,
            grid=True,
        )
        plt.tight_layout()
        plt.show()

    def tearDown(self):
        """Clean up after each test."""
        print("Test completed. Cleaning up...")

if __name__ == "__main__":
    unittest.main()
