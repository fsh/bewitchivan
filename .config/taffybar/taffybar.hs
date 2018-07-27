import System.Taffybar

import System.Taffybar.Systray
import System.Taffybar.TaffyPager
import System.Taffybar.SimpleClock
import System.Taffybar.FreedesktopNotifications
import System.Taffybar.Weather
import System.Taffybar.MPRIS

import System.Taffybar.Widgets.PollingBar
import System.Taffybar.Widgets.PollingGraph

import System.Information.Memory
import System.Information.CPU
import Graphics.UI.Gtk (escapeMarkup)

memCallback = do
  mi <- parseMeminfo
  return [memoryUsedRatio mi]

cpuCallback = do
  (userLoad, systemLoad, totalLoad) <- cpuLoad
  return [totalLoad, systemLoad]

span_ sz fg bg s = concat ["<span", sz', fg', bg', ">", escapeMarkup s, "</span>"]
  where
    sz' = if null sz then "" else concat [" size=\"", sz, "\""]
    fg' = if null fg then "" else concat [" fgcolor=\"", fg, "\""]
    bg' = if null bg then "" else concat [" bgcolor=\"", bg, "\""]

shorten_ n = take n

myPager = defaultPagerConfig
  { activeWindow = span_ "xx-large" "bisque" "" . shorten_ 100
  , activeLayout = span_ "large" "navajo white" ""
  , activeWorkspace = span_ "xx-large" "goldenrod" "midnight blue"
  , visibleWorkspace = span_ "xx-large" "dark goldenrod" "navy"
  , urgentWorkspace = span_ "x-large" "orange red" ""
  , hiddenWorkspace = span_ "large" "silver" ""
  , emptyWorkspace = span_ "" "grey" ""
  , widgetSep = " : "
}

main = do
  let memCfg = defaultGraphConfig { graphDataColors = [(1, 0, 0, 1)]
                                  , graphLabel = Just "mem"
                                  }
      cpuCfg = defaultGraphConfig { graphDataColors = [ (0, 1, 0, 1)
                                                      , (1, 0, 1, 0.5)
                                                      ]
                                  , graphLabel = Just "cpu"
                                  }
  let clock = textClockNew Nothing "<span size=\"xx-large\" fgcolor='orange'>%Y-%b-%d [%a] %H:%M</span>" 1
      pager = taffyPagerNew myPager
      note = notifyAreaNew defaultNotificationConfig
      mpris = mprisNew defaultMPRISConfig
      mem = pollingGraphNew memCfg 2.0 memCallback
      cpu = pollingGraphNew cpuCfg 1.0 cpuCallback
      tray = systrayNew
  defaultTaffybar defaultTaffybarConfig { startWidgets = [ pager, note ]
                                        , endWidgets = [ tray, clock, mem, cpu, mpris ]
                                        , barPosition = Bottom
                                        , monitorNumber = 2
                                        }
