"""
Functions for this project.
"""

import numpy as np


def randomDelay(min=5, max=20):
    """
    Generates random integers.
    """
    integer = np.random.random_integers(low=min, high=max)
    return integer
