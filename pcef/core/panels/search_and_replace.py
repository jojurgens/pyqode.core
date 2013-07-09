#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# PCEF - Python/Qt Code Editing Framework
# Copyright 2013, Colin Duquesnoy <colin.duquesnoy@gmail.com>
#
# This software is released under the LGPLv3 license.
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
"""
This module contains the search and replace panel
"""
import sys
import os
usePyQt4 = os.environ['QT_API'] == "PyQt"
usePySide = os.environ['QT_API'] == "PySide"
from pcef.qt import QtCore, QtGui
from pcef.core import constants
from pcef.core.decoration import TextDecoration
from pcef.core.system import DelayJobRunner
from pcef.core.panel import Panel


if sys.version_info[0] == 3:
    if usePyQt4:
        from pcef.core.ui.search_panel_ui3_pyqt import Ui_SearchPanel
    elif usePySide:
        from pcef.core.ui.search_panel_ui3_pyside import Ui_SearchPanel
else:
    if usePyQt4:
        from pcef.core.ui.search_panel_ui_pyqt import Ui_SearchPanel
    elif usePySide:
        from pcef.core.ui.search_panel_ui_pyside import Ui_SearchPanel


class SearchAndReplacePanel(Panel, Ui_SearchPanel, DelayJobRunner):
    """
    Search (& replace) Panel. Allow the user to search for content in the editor

    All occurrences are highlighted using text decorations.

    The occurrence under the cursor is selected using the find method of the
    plain text edit. User can go backward and forward.

    The Panel add a few actions to the editor menu(search, replace, next,
    previous, replace, replace all)

    The Panel is shown with ctrl-f for a search, ctrl-r for a search and
    replace.

    The Panel is hidden with ESC or by using the close button (white cross).

    .. note:: The widget use a custom ui designed in Qt Designer
    """
    IDENTIFIER = "searchAndReplacePanel"
    DESCRIPTION = "Search and replace text in the editor"

    #: Stylesheet
    STYLESHEET = """QWidget
    {
        background-color: %(bck)s;
        color: %(color)s;
    }

    QLineEdit
    {
        background-color: %(txt_bck)s;
        border: 1px solid %(highlight)s;
        border-radius: 3px;
    }

    QLineEdit:hover, QLineEdit:focus
    {
        border: 1px solid %(color)s;
        border-radius: 3px;
    }

    QPushButton
    {
        background-color: transparent;
        padding: 5px;
        border: none;
    }

    QPushButton:hover
    {
        background-color: %(highlight)s;
        border: none;
        border-radius: 5px;
        color: %(color)s;
    }

    QPushButton:pressed, QCheckBox:pressed
    {
        border: 1px solid %(bck)s;
    }

    QPushButton:disabled
    {
        color: %(highlight)s;
    }

    QCheckBox
    {
        padding: 4px;
    }

    QCheckBox:hover
    {
            background-color: %(highlight)s;
            color: %(color)s;
            border-radius: 5px;
    }
    """
    _KEYS = ["panelBackground", "background", "foreground", "panelHighlight"]

    __updateLabeMatchesRequested = QtCore.Signal(int)

    def __init__(self):
        Panel.__init__(self)
        DelayJobRunner.__init__(self, self, nbThreadsMax=1, delay=500)
        Ui_SearchPanel.__init__(self)
        self.setupUi(self)
        self.__separator = None
        self._decorations = []
        self.__updateLabeMatchesRequested.connect(self.__updateLabelMatches)

    def install(self, editor):
        Panel.install(self, editor)
        self.resetStylesheet()
        self.hide()

    def resetStylesheet(self):
        stylesheet = self.STYLESHEET % {
            "bck": self.editor.style.value(self._KEYS[0]).name(),
            "txt_bck": self.editor.style.value(self._KEYS[1]).name(),
            "color": self.editor.style.value(self._KEYS[2]).name(),
            "highlight": self.editor.style.value(self._KEYS[3]).name()}
        self.setStyleSheet(stylesheet)

    def onStyleChanged(self, section, key, value):
        if key in self._KEYS:
            self.resetStylesheet()

    def onStateChanged(self, state):
        if state:
            self.__separator = self.editor.contextMenu.addSeparator()
            self.editor.contextMenu.addAction(self.actionSearch)
            self.editor.contextMenu.addAction(self.actionActionSearchAndReplace)
            self.editor.textChanged.connect(self.requestSearch)
            self.lineEditSearch.textChanged.connect(self.requestSearch)
            self.checkBoxCase.stateChanged.connect(self.requestSearch)
            self.checkBoxWholeWords.stateChanged.connect(self.requestSearch)
        else:
            if self.__separator:
                self.editor.contextMenu.removeAction(self.__separator)
            self.editor.contextMenu.removeAction(self.actionSearch)
            self.editor.contextMenu.removeAction(
                self.actionActionSearchAndReplace)
            self.editor.textChanged.disconnect(self.requestSearch)
            self.lineEditSearch.textChanged.disconnect(self.requestSearch)
            self.checkBoxCase.stateChanged.disconnect(self.requestSearch)
            self.checkBoxWholeWords.stateChanged.disconnect(self.requestSearch)

    @QtCore.Slot()
    def on_pushButtonClose_clicked(self):
        self.hide()

    @QtCore.Slot()
    def on_actionSearch_triggered(self):
        self.widgetSearch.show()
        self.widgetReplace.hide()
        self.show()
        self.lineEditSearch.setText(self.editor.selectedText())
        self.lineEditSearch.selectAll()
        self.lineEditSearch.setFocus()

    @QtCore.Slot()
    def on_actionActionSearchAndReplace_triggered(self):
        self.widgetSearch.show()
        self.widgetReplace.show()
        self.show()
        self.lineEditSearch.setText(self.editor.selectedText())
        self.lineEditReplace.setText(self.editor.selectedText())
        self.lineEditReplace.selectAll()
        self.lineEditReplace.setFocus()

    @QtCore.Slot(str)
    def requestSearch(self, txt=""):
        self.requestJob(self.search, text=self.lineEditSearch.text())

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Enter:
            event.accept()
            pass  # go next
        if event.key() == QtCore.Qt.Key_Escape:
            self.hide()

    def getUserSearchFlag(self):
        """ Returns the user search flag """
        searchFlag = QtGui.QTextDocument.FindFlags(0)
        if self.checkBoxCase.isChecked():
            searchFlag |= QtGui.QTextDocument.FindCaseSensitively
        if self.checkBoxWholeWords.isChecked():
            searchFlag |= QtGui.QTextDocument.FindWholeWords
        return searchFlag

    def __createDecoration(self, tc):
        """ Creates the text occurences decoration """
        deco = TextDecoration(tc)
        deco.setBackground(QtGui.QBrush(QtGui.QColor("#FFFF00")))
        deco.setForeground(QtGui.QBrush(QtGui.QColor("#000000")))
        return deco

    def clearDecorations(self):
        """ Remove all decorations """
        pos = self.editor.textCursor().position()
        for deco in self._decorations:
            self.editor.removeDecoration(deco)
        self._decorations[:] = []
        self.editor.textCursor().setPosition(pos)

    def search(self, text=""):
        self.clearDecorations()
        if text:
            searchFlag = self.getUserSearchFlag()
            tc = self.editor.textCursor()
            doc = self.editor.document()
            tc.movePosition(QtGui.QTextCursor.Start)
            cptMatches = 0
            tc = doc.find(text, tc, searchFlag)
            while not tc.isNull():
                deco = self.__createDecoration(tc)
                self._decorations.append(deco)
                self.editor.addDecoration(deco)
                tc.setPosition(tc.position() + 1)
                tc = doc.find(text, tc, searchFlag)
                cptMatches += 1
            self.__updateLabeMatchesRequested.emit(cptMatches)

    def __updateLabelMatches(self, cptMatches):
        self.labelMatches.setText("{0} matches".format(cptMatches))
        color = "#DD0000"
        if cptMatches:
            color = "#00DD00"
        self.labelMatches.setStyleSheet("color: %s" % color)
