"""Supplier / Water Filter domain portability contracts."""

from .kernel_adapter_v01 import (
    SupplierWaterFilterKernelAdapterResultV01,
    build_supplier_water_filter_kernel_adapter_result_v01,
    supplier_water_filter_kernel_adapter_result_to_plain_dict_v01,
    validate_supplier_water_filter_kernel_adapter_result_v01,
)

__all__ = (
    "SupplierWaterFilterKernelAdapterResultV01",
    "build_supplier_water_filter_kernel_adapter_result_v01",
    "validate_supplier_water_filter_kernel_adapter_result_v01",
    "supplier_water_filter_kernel_adapter_result_to_plain_dict_v01",
)
