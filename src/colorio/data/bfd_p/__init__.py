"""
C. Alder, K.P. Chaing, T.F. Chong, E. Coates, A.A. Khalili and B. Rigg,
Uniform Chromaticity Scales - New Experimental Data,
Journal of The Society of Dyers and Colourists,
Volume 98 January 1982,
<https://doi.org/10.1111/J.1478-4408.1982.TB03602.X>
"""
import json
import pathlib
from typing import Type

import numpy as np

from ...cs import ColorSpace
from ..helpers import create_cs_class_instance, stress_absolute, stress_relative


class BfdP:
    def __init__(self):
        # surround parameters as used in
        #
        # Melgosa, Huertas, Berns,
        # Performance of recent advanced color-difference formulas using the
        # standardized residual sum of squares index
        # J. Opt. Soc. Am. A/ Vol. 25, No. 7/ July 2008,
        # <https://doi.org/10.1364/JOSAA.25.001828>.
        #
        self.c = 0.69  # average
        self.L_A = 100
        self.Y_b = 20

        self.dv = []
        self.xyz_pairs = []
        self.whitepoints = []

        this_dir = pathlib.Path(__file__).resolve().parent

        for filename in ["bfd-c.json", "bfd-d65.json", "bfd-m.json"]:
            with open(this_dir / filename) as f:
                data = json.load(f)
            xyz = np.asarray(data["xyz"])
            pairs = np.asarray(data["pairs"])
            self.dv.append(data["dv"])
            self.xyz_pairs.append(xyz[pairs])
            self.whitepoints.append(data["reference_white"])

        self.dv = np.concatenate(self.dv)

    def stress(self, cs_class: Type[ColorSpace], variant: str = "absolute"):
        deltas = []
        for xyz, wp in zip(self.xyz_pairs, self.whitepoints):
            cs = create_cs_class_instance(cs_class, wp, self.c, self.Y_b, self.L_A)
            # compute Euclidean distance in the given colorspace
            cs_pairs = cs.from_xyz100(xyz.T).T
            cs_diff = cs_pairs[:, 1] - cs_pairs[:, 0]
            deltas.append(np.sqrt(np.einsum("ij,ij->i", cs_diff, cs_diff)))

        delta = np.concatenate(deltas)

        fun = stress_absolute if variant == "absolute" else stress_relative
        return fun(self.dv, delta)

    # def plot(self, cs: ColorSpace):
    #     import matplotlib.pyplot as plt
    #     return plt
