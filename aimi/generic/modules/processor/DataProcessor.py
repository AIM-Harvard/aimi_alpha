"""
-------------------------------------------------
AIMI beta - Data Processor Base Module
-------------------------------------------------

-------------------------------------------------
Author: Leonard Nürnberg
Email:  leonard.nuernberg@maastrichtuniversity.nl
-------------------------------------------------
"""

from aimi.generic.Config import Instance
from aimi.generic.modules.convert.DataConverter import DataConverter

class DataProcessor(DataConverter):
    """
    Processor Module.
    Special conversion module that is ment to convert and modify the input data.
    """

    def convert(self, instance: Instance):
        return super().convert(instance)
