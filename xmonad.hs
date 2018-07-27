
module Main where

import XMonad
import XMonad.Hooks.DynamicLog
import XMonad.Hooks.ManageDocks
import XMonad.Util.Run(spawnPipe)
import XMonad.Util.EZConfig
import System.IO
import XMonad.Hooks.EwmhDesktops (ewmh)
import XMonad.Config.Desktop
import System.Taffybar.Hooks.PagerHints (pagerHints)
import qualified Data.Map as M
import Data.Ratio
import XMonad.Hooks.ManageHelpers
import System.Exit

import XMonad.Layout.Circle
import XMonad.Layout.Spiral
import XMonad.Layout.MosaicAlt
import XMonad.Layout.Grid
import XMonad.Layout.TwoPane
import XMonad.Layout.Named
import XMonad.Layout.NoBorders
-- import DBus.Client
-- import System.Taffybar.XMonadLog (dbusLogWithPP, taffybarDefaultPP, taffybarColor, taffybarEscape)
import System.Taffybar.TaffyPager

import XMonad.Actions.RotSlaves
import XMonad.Actions.CycleWindows

import qualified XMonad.StackSet as W
import XMonad.Layout.MultiToggle
import XMonad.Layout.MultiToggle.Instances


workspaceNames = [("1", "im")
                 ,("2", "web")
                 ,("3", "emacs")
                 ,("4", "dev0")
                 ,("5", "dev1")
                 ,("6", "atom")
                 ,("7", "tty7")
                 ,("8", "tty8")
                 ,("9", "play")
                 ,("0", "mp3")]

workspaceKeys :: [(String, X ())]
workspaceKeys = [ (mod ++ "M-" ++ key, action name)
                | (key, name) <- workspaceNames
                , (mod, action) <- [ ("", windows . W.view),
                                    ("S-", windows . W.shift) ] ]


fullscreenWindow :: Window -> X ()
fullscreenWindow id = do
  floats <- gets (W.floating . windowset)
  if id `M.member` floats
    then withFocused (windows . W.sink)
    else withFocused (windows . flip W.float (W.RationalRect 0 0 1 1))

cycleScreen ss = ss { W.current = head ww
                    , W.visible = tail ww }
      where ww = W.visible ss ++ [W.current ss]

myHooks = composeAll
  [ isDialog --> doCenterFloat
  , isFullscreen --> do
      doFullFloat
  , className =? "spotify" --> doShift "mp3"
  , (fmap not isDialog) --> doF lowerToSlave ]


-- W.stack W.workspace W.current x
lowerToSlave = W.shiftMaster . W.focusDown

myKeys =
  -- Restart/quit.
  [ ("M-z", spawn "if type xmonad; then xmonad --recompile && xmonad --restart; else xmessage xmonad not in \\$PATH: \"$PATH\"; fi")
  , ("S-M-z", io exitSuccess)
  -- General screen/window housekeeping.
  , ("M-q", windows cycleScreen)
  , ("M-g", rescreen)
  , ("M-f", withFocused fullscreenWindow)
  , ("M-l", refresh)
  -- General layout.
  , ("M-m", sendMessage $ Toggle MIRROR)
  , ("M-b", sendMessage ToggleStruts)
  , ("M-<Space>", sendMessage NextLayout)
  -- , ("S-M-<Space>", setLayout $ layoutHook conf)
  -- Master management.
  , ("M-<Return>", windows W.focusMaster)
  , ("S-M-<Return>", windows W.swapMaster)
  , ("M-n", sendMessage Shrink)
  , ("M-o", sendMessage Expand)
  , ("M-e", sendMessage (IncMasterN 1))
  , ("M-i", sendMessage (IncMasterN $ -1))
  -- Slave management.
  , ("M-", windows W.swapUp)
  , ("M-", windows W.swapDown)
  , ("M-u", rotSlavesUp)
  , ("M-y", rotSlavesDown)
  , ("S-M-u", rotFocusedUp)
  , ("S-M-y", rotFocusedDown)
  -- Killing & spawning
  , ("M-k", kill)
  , ("M-r", spawn "dmenu_run")
  , ("M-t", spawn "urxvt")
  , ("M-c", spawn "pcmanfm")
  , ("M-s", spawn "sleep 0.5; scrot -s ~/Pictures/'%Y-%m-%d_%H:%M_$wx$h.png'")
  , ("S-M-s", spawn "scrot -u ~/Pictures/'%Y-%m-%d_%H:%M_$wx$h.png'")
  ] ++ workspaceKeys

basicLayout   = named "basic" $ Mirror $ Tall nmaster delta ratio where
    nmaster = 1
    delta   = 3/100
    ratio   = 1/2
singleLayout  = named "single" $ noBorders Full
circleLayout  = named "circle" Circle
twoPaneLayout = named "twopan" $ TwoPane (2/100) (1/2)
mosaicLayout  = named "mosaic" $ MosaicAlt M.empty
gridLayout    = named "grid" Grid
spiralLayout  = named "spiral" $ spiral (3 % 4)

myLayoutHook = smartBorders $ avoidStruts $
  singleLayout ||| mkToggle (single MIRROR) (basicLayout ||| circleLayout ||| twoPaneLayout ||| mosaicLayout ||| gridLayout ||| spiralLayout)

main = xmonad $ docks $ ewmh $ pagerHints $ def
         { modMask = mod4Mask
         , focusFollowsMouse = False
         -- , startupHook = spawn "taffybar"
         , workspaces = map snd workspaceNames
         , layoutHook = myLayoutHook
         , normalBorderColor = "#2a2b2f"
         , focusedBorderColor = "DarkOrange"
         , borderWidth = 3
         , handleEventHook = docksEventHook <+> handleEventHook desktopConfig
         , manageHook = myHooks <+> manageDocks
         -- , logHook = dbusLogWithPP client (taffyPagerN)
         , terminal = "urxvt"
         } `additionalKeysP` myKeys
