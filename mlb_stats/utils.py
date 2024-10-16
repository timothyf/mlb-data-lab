import json
import numpy as np
import os


class Utils:

    @staticmethod
    def ensure_directory_exists(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

    @staticmethod
    def dump_json(json_str):
        return json.dumps(json_str, indent=4, cls=Utils.NumpyEncoder)

    @staticmethod
    class NumpyEncoder(json.JSONEncoder):
        """ Custom encoder to convert NumPy data types to native Python types """
        def default(self, obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()  # Convert NumPy arrays to lists
            else:
                return super(Utils.NumpyEncoder, self).default(obj)
            
    @staticmethod
    def format_stat(value, format_spec: str = None):
        """Function to apply appropriate formatting to a stat."""

        if format_spec is None:
            return value
            
        # Check if the format_spec is a function (e.g., lambda)
        if callable(format_spec):
            return format_spec(value)  # Call the function to format the value

        # Check for percent formatting
        if format_spec == 'percent':
            return f"{value * 100:.1f}%"
        
        # Custom formatting for removing leading zero before the decimal
        if isinstance(format_spec, str) and 'no_leading_zero' in format_spec:
            formatted_value = f"{value:.3f}"  # Format with three decimal places
            return formatted_value.lstrip('0')  # Remove leading zero if present
        
        # Ensure format_spec is a string before using format()
        if isinstance(format_spec, str):
            return format(value, format_spec)
        
        # If format_spec is not a string, raise an error or handle appropriately
        raise TypeError(f"Invalid format_spec: {format_spec}. Expected a string or callable.")
