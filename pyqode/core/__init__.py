#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013 Colin Duquesnoy
#
# This file is part of pyQode.
#
# pyQode is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# pyQode is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with pyQode. If not, see http://www.gnu.org/licenses/.
#
"""
This package contains the core classes of pyqode and an example of a generic
code editor widget
"""
#
# exposes public core api
#
from glob import glob
import os
import sys
from pyqode.core import constants
from pyqode.core import logger
from pyqode.core.constants import PanelPosition
from pyqode.core.decoration import TextDecoration
from pyqode.core.editor import QCodeEdit
from pyqode.core.syntax_highlighter import SyntaxHighlighter
from pyqode.core.syntax_highlighter import FoldDetector
from pyqode.core.syntax_highlighter import IndentBasedFoldDetector
from pyqode.core.syntax_highlighter import CharBasedFoldDetector
from pyqode.core.mode import Mode
from pyqode.core.modes import AutoIndentMode
from pyqode.core.modes import CaretLineHighlighterMode
from pyqode.core.modes import CheckerMode, CheckerMessage
from pyqode.core.modes import MSG_STATUS_ERROR
from pyqode.core.modes import MSG_STATUS_INFO
from pyqode.core.modes import MSG_STATUS_WARNING
from pyqode.core.modes import CHECK_TRIGGER_TXT_CHANGED
from pyqode.core.modes import CHECK_TRIGGER_TXT_SAVED
from pyqode.core.modes import CodeCompletionMode
from pyqode.core.modes import CompletionProvider
from pyqode.core.modes import Completion
from pyqode.core.modes import DocumentWordCompletionProvider
from pyqode.core.modes import FileWatcherMode
from pyqode.core.modes import IndenterMode
from pyqode.core.panel import Panel
from pyqode.core.modes import PygmentsSyntaxHighlighter, PYGMENTS_STYLES
from pyqode.core.modes import RightMarginMode
from pyqode.core.modes import SymbolMatcherMode
from pyqode.core.modes import ZoomMode
from pyqode.core.panels import FoldingPanel
from pyqode.core.panels import LineNumberPanel
from pyqode.core.panels import MarkerPanel, Marker
from pyqode.core.panels import SearchAndReplacePanel
from pyqode.core.properties import PropertyRegistry
from pyqode.core.system import indexByName
from pyqode.core.system import indexMatching
from pyqode.core.system import TextStyle
from pyqode.core.system import JobRunner
from pyqode.core.system import DelayJobRunner
from pyqode.core.system import SubprocessServer
from pyqode.core.system import memoized


#: pyqode-core version
__version__ = "1.0b"


# def getUiDirectory():
#     """
#     Gets the pyqode-core ui directory
#     """
#     return os.path.join(os.path.dirname(__file__), "ui")
#
#
# def getRcDirectory():
#     """
#     Gets the pyqode-core rc directory
#     """
#     return os.path.join(os.path.abspath(os.path.join(__file__, "..")), "ui",
#                         "rc")
#
# # import the core rc modules
# if os.environ["QT_API"] == "PyQt":
#     from pyqode.core.ui import rc_pyqode_core
# else:
#     from pyqode.core.ui import pyqode_icons_pyside_rc


# def cxFreeze_getDataFiles():
#     """
#     Returns the core package's data files in a format suitable for cx_freeze.
#     """
#     uiDir = os.path.join(os.path.dirname(__file__), "ui")
#     dataFiles = []
#     for f in glob(os.path.join(uiDir, "*.ui")):
#         assert os.path.exists(f)
#         dataFiles += [tuple((f, os.path.join("pyqode_ui/",
#                                             os.path.split(f)[1])))]
#     return dataFiles

#
# Example of a generic code editor widgey
#
class QGenericCodeEdit(QCodeEdit):
    """
    Extends QCodeEdit with a hardcoded set of modes and panels.

    **Panels:**
        * line number panel
        * search and replace panel

    **Modes:**
        * document word completion
        * generic syntax highlighter (pygments)
    """
    def __init__(self, parent=None):
        QCodeEdit.__init__(self, parent)
        self.setLineWrapMode(self.NoWrap)
        self.setWindowTitle("pyQode - Generic Editor")
        self.installPanel(FoldingPanel(), PanelPosition.LEFT)
        self.installPanel(LineNumberPanel(), PanelPosition.LEFT)
        self.installPanel(SearchAndReplacePanel(), PanelPosition.BOTTOM)
        self.installMode(FileWatcherMode())
        self.installMode(CaretLineHighlighterMode())
        self.installMode(RightMarginMode())
        self.installMode(PygmentsSyntaxHighlighter(self.document()))
        self.installMode(ZoomMode())
        self.installMode(AutoIndentMode())
        self.installMode(CodeCompletionMode())
        self.installMode(IndenterMode())
        self.codeCompletionMode.addCompletionProvider(
            DocumentWordCompletionProvider())
        self.installMode(SymbolMatcherMode())


__all__ = ["__version__", "constants", "logger", "Mode", "Panel", "QCodeEdit",
           "SyntaxHighlighter",
           "LineNumberPanel", "MarkerPanel", "Marker", "FoldingPanel",
           "SearchAndReplacePanel", "CaretLineHighlighterMode", "CheckerMode",
           "CheckerMessage", "MSG_STATUS_INFO", "MSG_STATUS_ERROR",
           "MSG_STATUS_WARNING", "FoldDetector", "IndentBasedFoldDetector",
           "CharBasedFoldDetector",
           "CHECK_TRIGGER_TXT_CHANGED", "CHECK_TRIGGER_TXT_SAVED",
           "CodeCompletionMode", "CompletionProvider", "Completion",
           "DocumentWordCompletionProvider", "FileWatcherMode",
           "RightMarginMode", "ZoomMode", "PygmentsSyntaxHighlighter",
           "AutoIndentMode", "PanelPosition", "TextDecoration", "IndenterMode",
           "PropertyRegistry", "TextStyle", "QGenericCodeEdit", "JobRunner",
           "DelayJobRunner", "getUiDirectory", "getRcDirectory",
           "PYGMENTS_STYLES", "indexByName", "indexMatching", "memoized",
           "SubprocessServer", "SymbolMatcherMode"]

if sys.platform == "win32":
    __all__ += ["cxFreeze_getDataFiles"]
