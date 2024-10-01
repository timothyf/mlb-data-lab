from dataclasses import dataclass, field
from typing import Dict


@dataclass
class FontConfig:
    default_family: str = 'DejaVu Sans'
    default_size: int = 12
    title_size: int = 20
    axes_size: int = 16
    
    font_properties: dict = field(init=False)
    
    def __post_init__(self):
        # Setup the font properties for easy access
        self.font_properties = {
            'default': {'family': self.default_family, 'size': self.default_size},
            'titles': {'family': self.default_family, 'size': self.title_size, 'fontweight': 'bold'},
            'axes': {'family': self.default_family, 'size': self.axes_size},
        }




