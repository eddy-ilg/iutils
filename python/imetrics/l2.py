#!/usr/bin/env python3

import torch
from ._pair_metric import _PairMetric
from .result import Result
from .registry import register_pair_metric
from itypes import is_numpy, is_torch, convert


class L2Metric(_PairMetric):
    _name = "L2"
    _has_error_map = True
    _precision = 3

    def compute(self, data, reference, dims="hwc", device=None, compute_map=False, crop_boundary=None):
        if is_torch(data) and device is None: device = data.device
        if device is None:                    device = torch.device("cpu")

        data_bhwc = convert(data, old_dims=dims, new_dims="bhwc", device=device)
        reference_hhwc = convert(reference, old_dims=dims, new_dims="bhwc", device=device)

        spatial_error_bhwc = torch.sqrt(torch.pow(data_bhwc - reference_hhwc, 2).sum(dim=3, keepdims=True))

        if crop_boundary is not None and crop_boundary > 0:
            c = crop_boundary
            error = spatial_error_bhwc[:, c:-c, c:-c, :].mean().item()
        else:
            error = spatial_error_bhwc.mean().item()

        return Result(
            error=error,
            error_map=spatial_error_bhwc if compute_map else None,
            precision=self._precision
        )

register_pair_metric(L2Metric)