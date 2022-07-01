#!/usr/bin/env python3

import numpy as np
import math
from ._pair_metric import _PairMetric
from .result import Result
from .registry import register_pair_metric
from itypes import is_numpy, is_torch, convert, uint8


class PSNRYMetric(_PairMetric):
    _name = "PSNRY"
    _has_error_map = False
    _precision = 2

    def compute(self, data, reference, dims="hwc", device=None, compute_map=False):
        if compute_map:
            raise Exception(f"PSNRY cannot provide error map")

        data_bhwc = convert(data, old_dims=dims, new_dims="bhwc", device="numpy", dtype=uint8)
        reference_bhwc = convert(reference, old_dims=dims, new_dims="bhwc", device="numpy", dtype=uint8)

        import cv2

        errors = []
        for i in range(0, data_bhwc.shape[0]):
            data_hwc = data_bhwc[i, ...]
            reference_hwc = reference_bhwc[i, ...]

            data_Y = cv2.cvtColor(data_hwc, cv2.COLOR_RGB2YCrCb)[:, :, 0]
            reference_Y = cv2.cvtColor(reference_hwc, cv2.COLOR_RGB2YCrCb)[:, :, 0]

            mse = np.mean((data_Y - reference_Y)**2)
            if mse == 0:
                error = float('inf')
            error = 20 * math.log10(255.0 / math.sqrt(mse))

            errors.append(error)

        return Result(
            error=sum(errors) / len(errors),
            precision=self._precision
        )

register_pair_metric(PSNRYMetric)