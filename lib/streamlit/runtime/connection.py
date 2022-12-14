# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import importlib

import streamlit as st
from streamlit.runtime.caching import singleton


def _import_adapter(adapter_path: str):
    module_path = adapter_path.split(".")
    module_name = ".".join(module_path[0:-1])
    class_name = module_path[-1]

    module = importlib.import_module(module_name)
    Adapter = getattr(module, class_name)
    return Adapter


@singleton
def _get_connection(connection_name, **kwargs):
    secret_values = getattr(st.secrets.connection, connection_name)
    Adapter = _import_adapter(secret_values.adapter)

    adapter_kwargs = {
        i: kwargs.get(i, secret_values[i]) for i in secret_values if i != "adapter"
    }

    # Providing the streamlit module for access to the plugin interface
    import streamlit

    adapter_instance = Adapter(streamlit)
    adapter_output = adapter_instance.connect(**adapter_kwargs)

    return adapter_instance, adapter_output


@singleton
def dataframe_conversion_mapping():
    return {}


def register_data_type(from_type: str, to_type: str, conversion_func):
    mapping = dataframe_conversion_mapping()
    mapping[from_type] = mapping.get(from_type, {})
    mapping[from_type][to_type] = conversion_func


def classname(obj) -> str:
    cls = type(obj)
    module = cls.__module__
    name = cls.__qualname__
    if module is not None and module != "__builtin__":
        name = module + "." + name
    return name


def _is_dataframe_conversion_available(data) -> bool:
    mapping = dataframe_conversion_mapping()
    print(classname(data))
    if mapping.get(classname(data), None) is None:
        return False
    return True


def try_convert_to_dataframe(data):
    mapping = dataframe_conversion_mapping()
    conversion_func = mapping.get(classname(data), {}).get(
        "pandas.core.frame.DataFrame", None
    )

    if conversion_func is None:
        return None
    else:
        return conversion_func(data)


def connection(connection_name: str, **kwargs):
    adapter, adapter_output = _get_connection(connection_name, **kwargs)

    if not adapter.is_connected(adapter_output):
        _get_connection.clear()
        dataframe_conversion_mapping.clear()
        adapter, adapter_output = _get_connection(connection_name, **kwargs)

    return adapter_output
