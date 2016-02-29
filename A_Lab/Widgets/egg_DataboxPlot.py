# -*- coding: utf-8 -*-
"""
This object was borrowed from the spinmob project (see https://github.com/Spinmob/spinmob).

@author: jaxankey
@author: jayich

I wrapped it quickly to work with this framework.

@author: AlexBourassa

"""

import spinmob.egg as egg

def egg_DataboxPlot(**kwargs):
    dp = egg.gui.DataboxPlot(**kwargs)
    return dp, dp._widget