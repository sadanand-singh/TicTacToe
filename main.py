# Copyright (C) 2015  aws

# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.

# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.


import os
import random
import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import QSoundEffect

from Dialog import *
from tictactoe_ui import Ui_tictactoe


class Game(QMainWindow, Ui_tictactoe):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # Shows only the close button
        self.setWindowFlags(Qt.WindowCloseButtonHint)

        circleSound = QSoundEffect()
        circleSound.setSource(QUrl.fromLocalFile("circle.wav"))
        circleSound.setVolume(0.25)
        crossSound = QSoundEffect()
        crossSound.setSource(QUrl.fromLocalFile("cross.wav"))
        crossSound.setVolume(0.25)
        winSound = QSoundEffect()
        winSound.setSource(QUrl.fromLocalFile("win.wav"))
        winSound.setVolume(0.25)
        loseSound = QSoundEffect()
        loseSound.setSource(QUrl.fromLocalFile("lose.wav"))
        loseSound.setVolume(0.25)

        self.sounds = dict(circle=circleSound, cross=crossSound, win=winSound,
                           lose=loseSound)

        xIconPath = os.path.join("Icons", "x.png")
        oIconPath = os.path.join("Icons", "o.png")

        self.xIcon = QIcon(xIconPath)
        self.oIcon = QIcon(oIconPath)

        # To make the icons appear in full color while disabled
        self.xIcon.addPixmap(QPixmap(xIconPath), QIcon.Disabled)
        self.oIcon.addPixmap(QPixmap(oIconPath), QIcon.Disabled)

        self.allButtons = self.frame.findChildren(QToolButton)
        self.availabeButtons = self.allButtons[:]
        self.board = list('---------')
        self.defaultPalette = QApplication.palette()

        # connections
        for button in self.allButtons:
            button.clicked.connect(self.button_clicked)

        self.actionNew_Game.triggered.connect(self.new_game)
        self.actionDark_Theme.toggled.connect(self.dark_theme)
        self.action_Exit.triggered.connect(self.close)

        self.setFocus()  # sets the focus to the main window
        self.new_game()  # starts a new game

    def new_game(self):
        self.reset()

    def reset(self):
        self.frame.setEnabled(True)
        self.availabeButtons = self.allButtons[:]
        self.board = list('---------')
        self.statusbar.showMessage("You are X. You play first")

        for button in self.availabeButtons:
            button.setText("")
            button.setIcon(QIcon())
            button.setEnabled(True)

    def end_game(self, state):
        """Ends the game"""

        if state == 1:
            self.sounds["win"].play()
            Dialog(self, state).show()

            for button in self.availabeButtons:
                button.setEnabled(False)
            self.availabeButtons.clear()
            return True

        elif state == 2:
            self.sounds["lose"].play()
            Dialog(self, state).show()

            for button in self.availabeButtons:
                button.setEnabled(False)
            self.availabeButtons.clear()
            return True

        elif state == 3:
            Dialog(self, state).show()

            for button in self.allButtons:
                button.setEnabled(False)
            return True
        return False

    def button_clicked(self):
        button = self.sender()

        buttonName = str(button.objectName())
        buttonIndex = int(buttonName[-1]) - 1

        self.board[buttonIndex] = 'X'

        self.sounds["cross"].play()
        button.setText("1")
        button.setIcon(self.xIcon)
        button.setEnabled(False)
        self.availabeButtons.remove(button)

        winTest = self.check_win('X')
        if winTest != 2:
            if winTest == 1:
                self.end_game(1)
                return
            if winTest == -1:
                self.end_game(2)
                return

            self.end_game(3)
            return

        self.frame.setEnabled(False)
        self.com_play()

    def com_play(self):
        win, buttonIndex = self.nextMove(self.board, '0')

        msg = "This game is headed towards a DRAW!"
        if win is -1:
            msg = "Soon you are going to LOOSE :("
        if win is 1:
            msg = "Soon you are going to WIN :)"
        self.statusbar.showMessage(msg)

        self.board[buttonIndex] = '0'

        for buttonAvail in self.availabeButtons:
            buttonName = str(buttonAvail.objectName())
            buttonIndexNew = int(buttonName[-1]) - 1
            if buttonIndexNew == buttonIndex:
                button = buttonAvail
                self.sounds["circle"].play()
                button.setText("2")
                button.setIcon(self.oIcon)
                button.setEnabled(False)
                self.availabeButtons.remove(button)
                break

        winTest = self.check_win('0')
        if winTest != 2:
            if winTest == 1:
                self.end_game(2)
                return
            if winTest == -1:
                self.end_game(1)
                return

            self.end_game(3)
            return

        self.frame.setEnabled(True)

    def isWin(self, board):
        """
        GIven a board checks if it is in a winning state.

        Arguments:
              board: a list containing X,O or -.

        Return Value:
               True if board in winning state. Else False
        """
        #  check if any of the rows has winning combination
        for i in range(3):
            if (
                    len(set(board[i * 3:i * 3 + 3])) is 1 and
                    board[i * 3] is not '-'
               ):
                return True

        # check if any of the Columns has winning combination
        for i in range(3):
            if (
                    (board[i] is board[i + 3]) and
                    (board[i] is board[i + 6]) and
                    board[i] is not '-'
               ):
                return True

        # 2,4,6 and 0,4,8 cases
        if (
                board[0] is board[4] and
                board[4] is board[8] and
                board[4] is not '-'
           ):
            return True

        if (
                board[2] is board[4] and
                board[4] is board[6] and
                board[4] is not '-'
           ):
            return True

        return False

    def nextMove(self, board, player):
        """
        Computes the next move for a player given the current board state
        and also computes if the player will win or not.

        Arguments:
            board: list containing X,- and O
            player: one character string 'X' or 'O'

        Return Value:
            willwin: 1 if 'X' is in winning state, 0 if the game is draw
            and -1 if 'O' is winning
            nextmove: position where the player can play the next move so
            that the player wins or draws or delays the loss
        """
        if len(set(board)) == 1:
            return 0, 4
        nextplayer = 'X' if player == '0' else '0'
        if self.isWin(board):
            if player is 'X':
                return -1, -1
            else:
                return 1, -1
        res_list = []
        c = board.count('-')
        if c is 0:
            return 0, -1
        _list = []
        for i in range(len(board)):
            if board[i] == '-':
                _list.append(i)
        for i in _list:
            board[i] = player
            ret, move = self.nextMove(board, nextplayer)
            res_list.append(ret)
            board[i] = '-'
        if player is 'X':
            maxele = max(res_list)
            return maxele, _list[res_list.index(maxele)]
        else:
            minele = min(res_list)
            return minele, _list[res_list.index(minele)]

    def check_win(self, player):
        if self.isWin(self.board):
            if player is 'X':
                return -1
            else:
                return 1

        c = self.board.count('-')
        if c is 0:
            return 0
        return 2

    def dark_theme(self):
        """Changes the theme between dark and normal"""
        if self.actionDark_Theme.isChecked():
            QApplication.setStyle(QStyleFactory.create("Fusion"))
            plt = QPalette()
            plt.setColor(QPalette.Window, QColor(53, 53, 53))
            plt.setColor(QPalette.WindowText, Qt.white)
            plt.setColor(QPalette.Base, QColor(15, 15, 15))
            plt.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            plt.setColor(QPalette.ToolTipBase, Qt.white)
            plt.setColor(QPalette.ToolTipText, Qt.white)
            plt.setColor(QPalette.Text, Qt.white)
            plt.setColor(QPalette.Button, QColor(53, 53, 53))
            plt.setColor(QPalette.ButtonText, Qt.white)
            plt.setColor(QPalette.BrightText, Qt.red)
            plt.setColor(QPalette.Highlight, QColor(0, 24, 193).lighter())
            plt.setColor(QPalette.HighlightedText, Qt.black)
            plt.setColor(QPalette.Disabled, QPalette.Text, Qt.darkGray)
            plt.setColor(QPalette.Disabled, QPalette.ButtonText, Qt.darkGray)
            app.setPalette(plt)
            return

        app.setPalette(self.defaultPalette)

app = QApplication(sys.argv)
game = Game()
game.show()
app.exec_()
