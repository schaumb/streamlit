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

import React from "react"
import { BaseProvider } from "baseui"
import { Global } from "@emotion/react"
import { CustomThemeConfig } from "src/autogen/proto"
import { sendMessageToHost } from "src/hocs/withHostCommunication"
import SnowsightFonts from "src/components/core/SnowsightFonts"

import ThemeProvider from "src/components/core/ThemeProvider"
import {
  AUTO_THEME_NAME,
  SNOWSIGHT_LIGHT_THEME_NAME,
  createAutoTheme,
  createPresetThemes,
  getDefaultTheme,
  globalStyles,
  isPresetTheme,
  removeCachedTheme,
  setCachedTheme,
  ThemeConfig,
  createTheme,
} from "src/theme"

import AppWithScreencast from "./App"
import { StyledDataFrameOverlay } from "./styled-components"

const ThemedApp = (): JSX.Element => {
  const defaultTheme = getDefaultTheme()

  const [theme, setTheme] = React.useState<ThemeConfig>(defaultTheme)
  const [fontURLs, setFontURLs] = React.useState<string>()
  const [availableThemes, setAvailableThemes] = React.useState<ThemeConfig[]>([
    ...createPresetThemes(),
    ...(isPresetTheme(defaultTheme) ? [] : [defaultTheme]),
  ])

  const addThemes = (themeConfigs: ThemeConfig[]): void => {
    setAvailableThemes([...createPresetThemes(), ...themeConfigs])
  }

  const updateTheme = (newTheme: ThemeConfig): void => {
    if (newTheme !== theme) {
      setTheme(newTheme)

      // Only save to localStorage if it is not Auto since auto is the default.
      // Important to not save since it can change depending on time of day.
      if (newTheme.name === AUTO_THEME_NAME) {
        removeCachedTheme()
      } else {
        setCachedTheme(newTheme)
      }
    }
  }

  const updateAutoTheme = (): void => {
    if (theme.name === AUTO_THEME_NAME) {
      updateTheme(createAutoTheme())
    }
    const constantThemes = availableThemes.filter(
      theme => theme.name !== AUTO_THEME_NAME
    )
    setAvailableThemes([createAutoTheme(), ...constantThemes])
  }

  const setImportedTheme = (themeConfig: CustomThemeConfig): void => {
    // TODO: Depending on the preferred Host->Guest API for setting custom themes,
    // we may need to create the customThemeConfig proto here.
    //
    // For example:
    // const customThemeConfig = new CustomThemeConfig()
    // customThemeConfig.primaryColor = '#FAFAFA'

    // If fonts are coming from a URL, they need to be imported through the SnowsightFonts component.
    // So let's store them in state so we can pass them as props
    if (themeConfig.fontURLs) setFontURLs(JSON.stringify(themeConfig.fontURLs))

    // Theme creation mechanism
    const customTheme = createTheme(SNOWSIGHT_LIGHT_THEME_NAME, themeConfig)
    updateTheme(customTheme)
  }

  React.useEffect(() => {
    const mediaMatch = window.matchMedia("(prefers-color-scheme: dark)")
    mediaMatch.addEventListener("change", updateAutoTheme)

    // WIP: Mocking the host communication to update sis theme here to try things out.
    // TODO: Remove after we've tested everything.
    if (theme.name !== SNOWSIGHT_LIGHT_THEME_NAME) {
      sendMessageToHost({
        type: "SET_CUSTOM_THEME_CONFIG",
        theme: {
          primaryColor: "#1A6CE7",
          backgroundColor: "#FFFFFF",
          secondaryBackgroundColor: "#F2F2F2",
          textColor: "#1A1D21",
          widgetBackgroundColor: "#FFFFFF",
          widgetBorderColor: "#D3DAE8",
          font: 0,
          base: 0,
          bodyFont: '"Inter", "Source Sans Pro", sans-serif',
          codeFont: '"Apercu Mono", "Source Code Pro", monospace',
          fontURLs: [
            {
              family: "Inter",
              url: "https://rsms.me/inter/font-files/Inter-Regular.woff2?v=3.19",
              weight: 400,
            },
            {
              family: "Inter",
              url: "https://rsms.me/inter/font-files/Inter-SemiBold.woff2?v=3.19",
              weight: 600,
            },
            {
              family: "Inter",
              url: "https://rsms.me/inter/font-files/Inter-Bold.woff2?v=3.19",
              weight: 700,
            },
            {
              family: "Apercu Mono",
              url: "https://app.snowflake.com/static/2c4863733dec5a69523e.woff2",
              weight: 400,
            },
            {
              family: "Apercu Mono",
              url: "https://app.snowflake.com/static/e903ae189d31a97e231e.woff2",
              weight: 500,
            },
            {
              family: "Apercu Mono",
              url: "https://app.snowflake.com/static/32447307374154c88bc0.woff2",
              weight: 700,
            },
          ],
          customFontSizes: JSON.stringify({
            twoSm: "10px",
            sm: "12px",
            md: ".8rem",
            mdLg: "1rem",
            lg: "1.125rem",
            xl: "1.25rem",
            twoXL: "1.5rem",
            threeXL: "2rem",
            fourXL: "2.5rem",

            twoSmPx: 10,
            smPx: 12,
            mdPx: 14,
          }),
        },
      })
    }

    return () => mediaMatch.removeEventListener("change", updateAutoTheme)
  }, [theme, availableThemes])

  return (
    <BaseProvider
      theme={theme.baseweb}
      zIndex={theme.emotion.zIndices.popupMenu}
    >
      <ThemeProvider theme={theme.emotion} baseuiTheme={theme.basewebTheme}>
        <Global styles={globalStyles} />
        {/* If we're using snowsight's theme, load their fonts globally through the provided URLs */}
        {theme.name === SNOWSIGHT_LIGHT_THEME_NAME && fontURLs && (
          <SnowsightFonts fontURLs={JSON.parse(fontURLs)} />
        )}
        <AppWithScreencast
          theme={{
            setTheme: updateTheme,
            activeTheme: theme,
            addThemes,
            availableThemes,
            setImportedTheme,
          }}
        />
        {/* The data grid requires one root level portal element for rendering cell overlays */}
        <StyledDataFrameOverlay id="portal" />
      </ThemeProvider>
    </BaseProvider>
  )
}

export default ThemedApp
