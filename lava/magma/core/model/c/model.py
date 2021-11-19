# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier:  BSD-3-Clause
from abc import ABC, abstractmethod, abstractproperty, ABCMeta

from numpy.distutils.core import setup
from numpy.distutils.misc_util import Configuration, get_info

from importlib import import_module, invalidate_caches

from typing import List, Callable
import os

from lava.magma.core.model.py.model import AbstractPyProcessModel

AbstractCProcessModel = None


class CProcessModelMeta(ABCMeta):
    """
    Compiles the sources specified in the class definition and then generates a type that includes the custom module in its base classes
    """

    def __new__(cls, name, bases, attrs):
        if AbstractCProcessModel and AbstractCProcessModel in bases:

            def configuration(parent_package="", top_path=None):
                config = Configuration("", parent_package, top_path)
                config.add_extension(
                    "custom",
                    attrs["source_files"],
                    extra_info=get_info("npymath"),
                )
                return config

            setup(
                configuration=configuration,
                script_args=[
                    "clean",
                    "--all",
                    "build_ext",
                    "--inplace",
                    "--include-dirs",
                    os.path.dirname(os.path.abspath(__file__)),
                ],
            )
            invalidate_caches()
            module = import_module("custom")
            # from custom import Custom
            bases += (module.Custom, AbstractPyProcessModel)
        return super().__new__(cls, name, bases, attrs)


class AbstractCProcessModel(metaclass=CProcessModelMeta):
    """Abstract interface for a C ProcessModels.

    Example for how variables and ports might be initialized:
        a_in:  LavaCType(CInPort, 'short', precision=16)
        s_out: LavaCType(COutPort, 'short', precision=1)
        u:     LavaCType(array, 'signed long int', precision=24)
        v:     LavaCType(array, 'signed long int, precision=24)
        bias:  LavaCType(array, 'signed short int', precision=12)
        du:    LavaCType(scalar, 'short int', precision=12)
    """

    source_files: List[str] = None