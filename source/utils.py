


class Utils:

    def __init__(self):
        pass

    @staticmethod
    def format_stat(value, format_spec):
        """Function to apply appropriate formatting to a stat."""
        if format_spec == 'percent':
            return f"{value * 100:.1f}%"
        else:
            return format(value, format_spec)


    
    
