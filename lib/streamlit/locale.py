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
import logging
from gettext import translation
from typing import Callable, Optional

from streamlit.file_util import get_app_locale_dir
from streamlit.runtime.scriptrunner import get_script_run_ctx

APP_LOCALE_DOMAIN = "messages"


def fail_silently(func: Callable[[str], str]):
    """Decorator which returns message if any exception occurs."""

    def gettext(message: str):
        try:
            return func(message)
        except Exception as e:
            logging.warning(f"Gettext for {message} failed with exception {e}.")
            return message

    return gettext


def get_session_language() -> Optional[str]:
    ctx = get_script_run_ctx()
    if not ctx:
        return None
    return ctx.session_state.language


@fail_silently
def gettext(message: str) -> str:
    """Translates message and returns it as a string."""
    locales_dir = get_app_locale_dir()
    session_language = get_session_language()
    if not locales_dir or not session_language:
        return message
    return translation(
        APP_LOCALE_DOMAIN,
        localedir=locales_dir,
        languages=[
            session_language,
        ],
    ).gettext(message)
