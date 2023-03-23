/**
 * Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import React, { ReactElement, ReactNode, useEffect, useState } from "react"
import { ScriptRunState } from "src/lib/ScriptRunState"
import { WidgetStateManager } from "src/lib/WidgetStateManager"
import * as SharedModal from "src/components/shared/Modal"
import StreamlitMarkdown from "src/components/shared/StreamlitMarkdown/index"

export interface Props {
  formId: string
  clearOnSubmit: boolean
  hasSubmitButton: boolean
  scriptRunState: ScriptRunState
  children?: ReactNode
  widgetMgr: WidgetStateManager
  openModalId?: string | null
  closeModal: (() => void) | null | undefined
  icon?: string
  body?: string | null
  title?: string | null
  unsafeAllowHTML?: boolean | null
  canBeClosed?: boolean | null
}

export const MISSING_SUBMIT_BUTTON_WARNING =
  "**Missing Submit Button**" +
  "\n\nThis form has no submit button, which means that user interactions will " +
  "never be sent to your Streamlit app." +
  "\n\nTo create a submit button, use the `st.form_submit_button()` function." +
  "\n\nFor more information, refer to the " +
  "[documentation for forms](https://docs.streamlit.io/library/api-reference/control-flow/st.form)."

export function Modal(props: Props): ReactElement {
  const {
    body,
    formId,
    widgetMgr,
    hasSubmitButton,
    children,
    scriptRunState,
    clearOnSubmit,
    openModalId,
    closeModal,
    title,
    icon,
    unsafeAllowHTML,
    canBeClosed,
  } = props

  // Tell WidgetStateManager if this form is `clearOnSubmit` so that it can
  // do the right thing when the form is submitted.
  useEffect(() => {
    widgetMgr.setFormClearOnSubmit(formId, clearOnSubmit)
  }, [widgetMgr, formId, clearOnSubmit])

  // Determine if we need to show the "missing submit button" warning.
  // If we have a submit button, we don't show the warning, of course.
  // If we *don't* have a submit button, then we only mutate the showWarning
  // flag when our scriptRunState is NOT_RUNNING. (If the script is still
  // running, there might be an incoming SubmitButton delta that we just
  // haven't seen yet.)
  const [showWarning, setShowWarning] = useState(false)

  if (hasSubmitButton && showWarning) {
    setShowWarning(false)
  } else if (
    !hasSubmitButton &&
    !showWarning &&
    scriptRunState === ScriptRunState.NOT_RUNNING
  ) {
    setShowWarning(true)
  }

  const isOpen = formId === openModalId
  const isTitle = title && title?.length > 0
  const showModalHeader = !(!isTitle || !canBeClosed)
  return (
    <SharedModal.default
      data-testid="stModal"
      isOpen={isOpen}
      onClose={
        closeModal as (a: {
          closeSource?: "closeButton" | "backdrop" | "escape" | undefined
        }) => unknown
      }
      closeable={false}
      overrides={{
        Root: {
          style: {
            backdropFilter: canBeClosed ? "none" : "blur(8px)",
          },
        },
      }}
    >
      {showModalHeader ? (
        <SharedModal.ModalHeader>{title ? title : ""}</SharedModal.ModalHeader>
      ) : null}
      <SharedModal.ModalBody noPadding={false}>
        {children}
      </SharedModal.ModalBody>
    </SharedModal.default>
  )
}
