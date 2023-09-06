import tkinter as tk
from PIL import ImageTk
from board import Board
from _thread import start_new_thread
from time import sleep
from numpy.random import choice
from numpy import argmax

MAX_SCORE = 10000000000
MIN_SCORE = -1 * MAX_SCORE
depth = 6


# -------------------------------------------------------------------------------
def cm_to_px(cm):
    return round(37.79527559055118 * cm)


def drawtriangle(x, y, canvas):
    return canvas.create_polygon(
        cm_to_px(x - 0.5),
        cm_to_px(y),
        cm_to_px(x + 0.5),
        cm_to_px(y),
        cm_to_px(x),
        cm_to_px(y + 0.5),
        cm_to_px(x - 0.5),
        cm_to_px(y),
        fill="white",
    )


def copyboard(board):
    copy = Board()
    copy.turn = board.turn
    copy.move = board.move
    for k in range(0, 6):
        for l in range(0, 8):
            copy.boxmatrix[k][l] = board.boxmatrix[k][l]
    return copy


# -------------------------------------------------------------------------------
def forcedturn(board):
    for j in range(8):
        copy = copyboard(board)
        copy.nextturn()
        row = copy.dropstone(j)
        if copy.checkwin(row, j) == copy.turn:
            return j
    return -1


def playhumanturn(board, col):
    return board.dropstone(col), col


def playdumbturn(board):
    sleep(1)
    col = forcedturn(board)
    if col != -1:
        sleep(1)
        return board.dropstone(col), col
    col = choice(range(0, 8))
    while board.boxmatrix[0][col] != -1:
        sleep(1)  # nog ff nadenken....
        col = choice(range(0, 7))
    return board.dropstone(col), col


def dumbvsdumb(copy, row, col):
    while copy.checkwin(row, col) == -1:
        copy.nextturn()
        col = choice(range(0, 8))
        while copy.boxmatrix[0][col] != -1:
            col = choice(range(0, 8))
        row = copy.dropstone(col)
    return copy.checkwin(row, col)


def playmediumturn(board):
    col = forcedturn(board)
    if col != -1:
        return board.dropstone(col), col
    score = [0, 0, 0, 0, 0, 0, 0, 0]
    for j in range(0, 8):
        if board.boxmatrix[0][j] == -1:
            for game in range(0, 1000):
                copy = copyboard(board)
                row = copy.dropstone(j)
                victor = dumbvsdumb(copy, row, j)
                if victor == (board.turn + 1) % 2:
                    score[j] -= 1
                if j > 0 and score[j] < max(score[0:j]):
                    break
        else:
            score[j] = -2000
    return board.dropstone(argmax(score)), argmax(score)


def minimax(board, currentdepth, maximizing, player, alpha, beta):
    win = board.winner()
    if win == player:
        return MAX_SCORE - currentdepth
    if win != -1:
        return MIN_SCORE + currentdepth
    if currentdepth == depth:
        other = (player + 1) % 2
        return board.eval(player) - board.eval(other)

    board.nextturn()
    if not maximizing:
        score = MAX_SCORE
        for j in range(8):
            if board.boxmatrix[0][j] == -1:
                copy = copyboard(board)
                copy.dropstone(j)
                score = min(
                    score, minimax(copy, currentdepth + 1, True, player, alpha, beta)
                )
                beta = min(beta, score)
                if alpha >= beta:
                    break
        return score

    else:
        score = MIN_SCORE
        for j in range(8):
            if board.boxmatrix[0][j] == -1:
                copy = copyboard(board)
                copy.dropstone(j)
                score = max(
                    score, minimax(copy, currentdepth + 1, False, player, alpha, beta)
                )
                alpha = max(alpha, score)
                if alpha >= beta:
                    break
        return score


def minimaxstarter(board):
    record = MIN_SCORE
    bestmove = 0
    while board.boxmatrix[0][bestmove] != -1:
        bestmove += 1
    for j in range(8):
        if board.boxmatrix[0][j] == -1:
            copy = copyboard(board)
            copy.dropstone(j)
            score = minimax(copy, 1, False, board.turn, MIN_SCORE, MAX_SCORE)
            if score > record:
                record = score
                bestmove = j
    return bestmove


def playcleverturn(board):
    if board.move == 1:
        col = 3
    else:
        col = forcedturn(board)
        if col == -1:
            col = minimaxstarter(board)
    return board.dropstone(col), col


# ---------------------The App---------------------------------------------------
class MyCanvas(tk.Canvas):
    def __init__(self, parent):
        tk.Canvas.__init__(self, parent, width=458, height=524, bg="light grey")
        self.image = ImageTk.PhotoImage(file="canvasbg.png")
        self.create_image(0, 0, image=self.image, anchor=tk.NW)
        self.boxes = [[None for j in range(8)] for i in range(6)]
        self.triangle = [None for i in range(8)]
        for i in range(8):
            self.triangle[i] = drawtriangle(2.55 + i, 4.9, self)
        self.itemconfigure(self.triangle[0], fill="yellow")
        for i in range(6):
            rowtop = cm_to_px(5.9 + i)
            rowbottom = rowtop + cm_to_px(0.8)
            for j in range(8):
                colleft = cm_to_px(2.15 + j)
                colright = colleft + cm_to_px(0.8)
                self.boxes[i][j] = self.create_oval(
                    colleft, rowtop, colright, rowbottom, fill="white", outline="blue"
                )
        self.text = self.create_text(
            458 // 2, 50, text=" ", fill="black", font=("Purisa", 12, "bold")
        )

    def reset(self):
        for i in range(6):
            for j in range(8):
                self.itemconfigure(self.boxes[i][j], fill="white")
        self.itemconfigure(self.text, text=" ")
        self.update_idletasks()


class Application:
    def __init__(self, parent):
        self.turnentered = False
        self.parent = parent
        self.frame = tk.Frame(self.parent)
        self.frame.grid(row=0)
        self.canvas = MyCanvas(self.frame)
        self.canvas.bind("<Key>", self.keypress)
        self.canvas.grid(row=0, columnspan=2, rowspan=50)
        self.startbutton = tk.Button(
            self.frame,
            text="Start New Game",
            bg="green",
            command=lambda: start_new_thread(self.playgame, ()),
        )
        self.startbutton.grid(
            row=0, column=2, rowspan=5, sticky=tk.N + tk.S + tk.W + tk.E
        )
        # --------------
        playernames = ["Human", "DumbBot", "MediumBot", "CleverBot"]
        self.p1label = tk.Label(self.frame, text="Player 1 is a ....")
        self.p1label.grid(row=5, column=2, sticky=tk.N + tk.S + tk.W + tk.E)
        self.playertypes = [tk.IntVar(), tk.IntVar()]
        self.playertypes[0].set(1)
        self.playertypes[1].set(2)
        self.P1buttons = [None for i in range(4)]
        for i in range(4):
            self.P1buttons[i] = tk.Radiobutton(
                self.frame,
                text=playernames[i],
                variable=self.playertypes[0],
                value=i + 1,
                anchor=tk.W,
            )
            self.P1buttons[i].grid(
                row=6 + i, column=2, sticky=tk.N + tk.S + tk.W + tk.E
            )
        self.p2label = tk.Label(self.frame, text="Player 2 is a ....")
        self.p2label.grid(row=11, column=2, sticky=tk.N + tk.S + tk.W + tk.E)
        self.P2buttons = [None for i in range(4)]
        for i in range(4):
            self.P2buttons[i] = tk.Radiobutton(
                self.frame,
                text=playernames[i],
                variable=self.playertypes[1],
                value=i + 1,
                anchor=tk.W,
            )
            self.P2buttons[i].grid(
                row=12 + i, column=2, sticky=tk.N + tk.S + tk.W + tk.E
            )
        # ---------------
        self.selected = 0
        self.board = Board()
        self.turncolour = ["yellow", "red"]

    def reset(self):
        self.canvas.reset()
        self.board.reset()
        self.canvas.itemconfigure(
            self.canvas.triangle[self.selected], fill=self.turncolour[0]
        )
        for i in range(4):
            self.P1buttons[i].configure(state=tk.NORMAL)
            self.P2buttons[i].configure(state=tk.NORMAL)
        self.startbutton.configure(state=tk.NORMAL)

    def playgame(self):
        self.startbutton.configure(state=tk.DISABLED)
        for i in range(4):
            self.P1buttons[i].configure(state=tk.DISABLED)
            self.P2buttons[i].configure(state=tk.DISABLED)
        done = False
        while not done:
            playertype = self.playertypes[self.board.turn].get()
            if playertype == 1:
                self.canvas.focus_set()
                while not self.turnentered:
                    sleep(0.1)
                row, col = playhumanturn(self.board, self.selected)
                self.turnentered = False
                self.frame.focus_set()
            elif playertype == 2:
                row, col = playdumbturn(self.board)
            elif playertype == 3:
                row, col = playmediumturn(self.board)
            elif playertype == 4:
                row, col = playcleverturn(self.board)
            self.canvas.itemconfigure(
                self.canvas.boxes[row][col], fill=self.turncolour[self.board.turn]
            )
            winner = self.board.checkwin(row, col)
            if winner > -1:
                if winner != 2:
                    self.canvas.itemconfigure(
                        self.canvas.text, text="Player " + str(winner + 1) + " has won"
                    )
                else:
                    self.canvas.itemconfigure(self.canvas.text, text="Issa draw")
                done = True
            self.board.nextturn()
            self.canvas.itemconfigure(self.canvas.triangle[self.selected], fill="white")
            self.selected = col
            self.canvas.itemconfigure(
                self.canvas.triangle[self.selected],
                fill=self.turncolour[self.board.turn],
            )
            self.canvas.update_idletasks()
        sleep(5)
        self.reset()

    def keypress(self, event):
        keypressed = event.char
        if keypressed == "6":
            self.canvas.itemconfigure(self.canvas.triangle[self.selected], fill="white")
            self.selected = (self.selected + 1) % 8
            self.canvas.itemconfigure(
                self.canvas.triangle[self.selected],
                fill=self.turncolour[self.board.turn],
            )
        elif keypressed == "4":
            self.canvas.itemconfigure(self.canvas.triangle[self.selected], fill="white")
            self.selected = (self.selected - 1) % 8
            self.canvas.itemconfigure(
                self.canvas.triangle[self.selected],
                fill=self.turncolour[self.board.turn],
            )
        elif keypressed == " ":
            if self.board.boxmatrix[0][self.selected] == -1:
                self.turnentered = True


# -------------------------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Four in a row")
    app = Application(root)
    root.mainloop()
