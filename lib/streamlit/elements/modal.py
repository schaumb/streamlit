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

from typing import TYPE_CHECKING, Optional, cast

from streamlit.elements import form
from streamlit.errors import StreamlitAPIException
from streamlit.proto import Block_pb2
from streamlit.runtime.app_session import create_update_open_modal_id_modal_event
from streamlit.runtime.metrics_util import gather_metrics
from streamlit.runtime.scriptrunner import get_script_run_ctx
from streamlit.runtime.state import WidgetArgs, WidgetCallback, WidgetKwargs

if TYPE_CHECKING:
    from streamlit.delta_generator import DeltaGenerator
    from streamlit.type_util import SupportsStr


def build_modal_proto(
    form_id: str,
    clear_on_submit: bool,
    title: str,
    can_be_closed: bool,
    icon: str = "",
    body: "SupportsStr" = "",
    unsafe_allow_html: bool = False,
):
    return Block_pb2.Block(
        modal=Block_pb2.Block.Modal(
            form_id=form_id,
            clear_on_submit=clear_on_submit,
            title=title,
            can_be_closed=can_be_closed,
            icon=icon,
            body=str(body),
            unsafe_allow_html=unsafe_allow_html,
        )
    )


class ModalMixin:
    @gather_metrics("dialog")
    def dialog(
        self,
        key: str,
        clear_on_submit: bool = False,
        title: str = "",
        on_close_button_clicked: Optional[WidgetCallback] = None,
        args: Optional[WidgetArgs] = None,
        kwargs: Optional[WidgetKwargs] = None,
        *,  # keyword-only args:
        can_be_closed: bool = True,
    ):
        """Create a modal form that batches elements together with a "Submit" button.

        A modal is a container that groups other elements and widgets together,
        in a way similar to the form, but these elements ale displayed in a modal
         instead of the main container, similiary as form it contains a Submit button.
         When the modal's Submit button is pressed, all widget values inside the modal will be
        sent to Streamlit in a batch.

        To add elements to a modal object, you can use "with" notation
        (preferred) or just call methods directly on the form. See
        examples below.

        Forms have a few constraints:

        * Every modal must contain a ``st.modal_submit_button``.
        * Modal can appear anywhere in your app (sidebar, columns, etc),
          but they cannot be embedded inside other modals or forms.

        Parameters
        ----------
        key : str
            A string that identifies the modal. Each modal must have its own
            key. (This key is not displayed to the user in the interface.)
        clear_on_submit : bool
            If True, all widgets inside the modal will be reset to their default
            values after the user presses the Submit button. Defaults to False.
            (Note that Custom Components are unaffected by this flag, and
            will not be reset to their defaults on modal submission.)
        title : str
            Modal Title to be displayed in header.
            Title is an empty string "" by default, which results in no string inside modal header.
        on_close_button_clicked : callable
            An optional callback invoked when this button is clicked.
            When provided remember to close the modal manually using modal.close() method.
        args : tuple
            An optional tuple of args to pass to the callback.
        kwargs : dict
            An optional dict of kwargs to pass to the callback.
        can_be_closed : bool
            If True close button on the modal alert will appear,
            the click on the button will close the modal or call on_close_button_clicked if provided.

        Examples
        --------
        Inserting elements using "with" notation:

        >>> import streamlit as st
        >>>
        >>> dialog = st.dialog("my_dialog")
        >>>
        >>> def cta_callback():
        ...     st.write(f"Hey {st.session_state.first_name} {st.session_state.last_name}!")
        ...     st.write(f"Your preferences are saved")
        ...     dialog.close()
        >>>
        >>> with dialog:
        ...    st.text_input("First name", key="first_name")
        ...    st.text_input("Last name", key="last_name")
        ...    st.checkbox("I accept cookies", key="cookies")
        ...    st.form_submit_button("OK", on_click=cta_callback)
        ...
        >>>
        >>> if st.button("Open modal"):
        ...     dialog.open()
        >>>
        """
        # Import this here to avoid circular imports.
        from streamlit.elements.utils import check_session_state_rules

        if form.is_in_form(self.dg):
            raise StreamlitAPIException("Forms cannot be nested in other forms.")

        check_session_state_rules(default_value=None, key=key, writes_allowed=False)

        form_id = form.build_form_id(key)

        modal_proto = build_modal_proto(
            title=title,
            form_id=form_id,
            clear_on_submit=clear_on_submit,
            can_be_closed=can_be_closed,
        )
        block_dg = self.dg._block(modal_proto)

        # Attach the modal's button info to the newly-created block's
        # DeltaGenerator.
        block_dg._form_data = form.FormData(form_id)

        self._add_close_button_to_modal(
            block_dg,
            can_be_closed=can_be_closed,
            modal_title=title,
            on_close_button_clicked=on_close_button_clicked,
            args=args,
            kwargs=kwargs,
        )
        return block_dg

    def open(self):
        # use get_script_run_ctx instead of ctx, because context is dynamic and can change
        ctx = get_script_run_ctx()
        if ctx:
            ctx.enqueue(
                create_update_open_modal_id_modal_event(
                    open_modal_id=form.current_form_id(self.dg)
                )
            )

    def close(self):
        # use get_script_run_ctx instead of ctx, because context is dynamic and can change
        ctx = get_script_run_ctx()
        if ctx:
            # empty open_modal_id, should effectively close the modal
            ctx.enqueue(create_update_open_modal_id_modal_event(open_modal_id=""))

    def _add_close_button_to_modal(
        self,
        block_dg: "DeltaGenerator",
        can_be_closed: bool,
        on_close_button_clicked: Optional[WidgetCallback],
        args: Optional[WidgetArgs],
        kwargs: Optional[WidgetKwargs],
        modal_title: str = "",
    ):
        """Adds modal close button to modal delta generator if can be closed is True.
        Otherwise does not add close button, which results in user being unable to close the modal.
        """
        ctx = get_script_run_ctx()
        if can_be_closed and on_close_button_clicked:
            block_dg._form_submit_button(
                "",
                on_click=on_close_button_clicked,
                args=args,
                kwargs=kwargs,
                is_modal_close_button=True,
                can_modal_be_closed=can_be_closed,
                modal_title=modal_title,
                ctx=ctx,
            )
        else:
            block_dg._form_submit_button(
                "",
                on_click=self.close,
                is_modal_close_button=True,
                can_modal_be_closed=can_be_closed,
                modal_title=modal_title,
                ctx=ctx,
            )

    @property
    def dg(self) -> "DeltaGenerator":
        """Get our DeltaGenerator."""
        return cast(DeltaGenerator, self)
