class Board:
    def __init__(self):
        self.turn = 0
        self.boxmatrix = [[-1 for j in range(8)] for i in range(6)]
        self.move = 1

    def nextturn(self):
        self.turn = (self.turn + 1) % 2
        self.move += 1

    def reset(self):
        self.turn = 0
        self.move = 1
        for i in range(6):
            for j in range(8):
                self.boxmatrix[i][j] = -1

    def series(self, i, j, direction):
        result = 1
        if direction == "horizontal":
            while j > 0 and self.boxmatrix[i][j - 1] == self.turn:
                j -= 1
            while j < 7 and self.boxmatrix[i][j + 1] == self.turn:
                result += 1
                j += 1
        elif direction == "vertical":
            while i > 0 and self.boxmatrix[i - 1][j] == self.turn:
                i -= 1
            while i < 5 and self.boxmatrix[i + 1][j] == self.turn:
                result += 1
                i += 1
        elif direction == "nwdiag":
            while i > 0 and j > 0 and self.boxmatrix[i - 1][j - 1] == self.turn:
                i -= 1
                j -= 1
            while i < 5 and j < 7 and self.boxmatrix[i + 1][j + 1] == self.turn:
                result += 1
                i += 1
                j += 1
        elif direction == "nediag":
            while i > 0 and j < 7 and self.boxmatrix[i - 1][j + 1] == self.turn:
                i -= 1
                j += 1
            while i < 5 and j > 0 and self.boxmatrix[i + 1][j - 1] == self.turn:
                result += 1
                i += 1
                j -= 1
        return result

    def checkwin(self, row, column):
        if self.series(row, column, "horizontal") >= 4:
            return self.turn
        elif self.series(row, column, "vertical") >= 4:
            return self.turn
        elif self.series(row, column, "nwdiag") >= 4:
            return self.turn
        elif self.series(row, column, "nediag") >= 4:
            return self.turn
        for j in range(0, 8):
            if self.boxmatrix[0][j] == -1:
                return -1
        return 2

    def winner(self):
        for player in range(2):
            for i in range(6):
                for j in range(8):
                    if self.boxmatrix[i][j] == player:
                        if (
                            j < 5
                            and self.boxmatrix[i][j + 1] == player
                            and self.boxmatrix[i][j + 2] == player
                            and self.boxmatrix[i][j + 3] == player
                        ):
                            return player
                        if (
                            i < 3
                            and self.boxmatrix[i + 1][j] == player
                            and self.boxmatrix[i + 2][j] == player
                            and self.boxmatrix[i + 3][j] == player
                        ):
                            return player
                        if (
                            j < 5
                            and i < 3
                            and self.boxmatrix[i + 1][j + 1] == player
                            and self.boxmatrix[i + 2][j + 2] == player
                            and self.boxmatrix[i + 3][j + 3] == player
                        ):
                            return player
                        if (
                            j < 5
                            and i > 2
                            and self.boxmatrix[i - 1][j + 1] == player
                            and self.boxmatrix[i - 2][j + 2] == player
                            and self.boxmatrix[i - 3][j + 3] == player
                        ):
                            return player
        return -1

    def dropstone(self, column):
        row = 5
        while self.boxmatrix[row][column] != -1 and row >= 0:
            row -= 1
        if row < 0:
            return -1
        self.boxmatrix[row][column] = self.turn
        return row

    def eval(self, player):
        underattack = set()
        threesum = 0
        twosum = 0
        uatower = 0  # number of times two under-attack-cells on top of each other

        uabytwo = set()  # under attack by two
        for i in range(6):
            for j in range(8):
                if i < 4:
                    # check vertical
                    allowed = set([player, -1])
                    aux = None
                    n = 3 if i == 3 else 4
                    for x in range(n):
                        if self.boxmatrix[i + x][j] in allowed:
                            if self.boxmatrix[i + x][j] == -1:
                                allowed.remove(-1)
                                aux = (i + x, j)
                        else:
                            x = x - 1
                            break
                    if x == 3:
                        threesum += 1
                        underattack.add(aux)
                    elif x == 2 and aux != None:
                        twosum += 1
                        uabytwo.add(aux)

                if j < 6:
                    # check horizontal
                    allowed = set([player, -1])
                    aux != None
                    n = 3 if j == 5 else 4
                    for x in range(n):
                        if self.boxmatrix[i][j + x] in allowed:
                            if self.boxmatrix[i][j + x] == -1:
                                allowed.remove(-1)
                                aux = (i, j + x)
                        else:
                            x = x - 1
                            break
                    if x == 3:
                        threesum += 1
                        underattack.add(aux)
                    elif x == 2 and aux != None and aux not in underattack:
                        twosum += 1
                        uabytwo.add(aux)

                if i < 4 and j < 6:
                    # check diagonal NorthWest -- SothEeast
                    allowed = set([player, -1])
                    aux = None
                    n = 3 if (i == 3 or j == 5) else 4
                    for x in range(n):
                        if self.boxmatrix[i + x][j + x] in allowed:
                            if self.boxmatrix[i + x][j + x] == -1:
                                allowed.remove(-1)
                                aux = (i + x, j + x)
                        else:
                            x = x - 1
                            break
                    if x == 3:
                        threesum += 1
                        if aux in uabytwo:
                            twosum -= 1
                            uabytwo.remove(aux)
                        underattack.add(aux)
                    elif x == 2 and aux != None and aux not in underattack:
                        twosum += 1
                        uabytwo.add(aux)

                if i > 1 and j < 6:
                    # check diagonal SouthWest -- NorthEast
                    allowed = set([player, -1])
                    aux = None
                    n = 3 if (i == 2 or j == 5) else 4
                    for x in range(n):
                        if self.boxmatrix[i - x][j + x] in allowed:
                            if self.boxmatrix[i - x][j + x] == -1:
                                allowed.remove(-1)
                                aux = (i - x, j + x)
                        else:
                            x = x - 1
                            break
                    if x == 3:
                        threesum += 1
                        if aux in uabytwo:
                            twosum -= 1
                            uabytwo.remove(aux)
                        underattack.add(aux)
                    elif x == 2 and aux != None and aux not in underattack:
                        twosum += 1
                        uabytwo.add(aux)

        for ua in underattack:
            if ua[0] > 0 and (ua[0] - 1, ua[1]) in underattack:
                uatower += 1

        return twosum + 10 * threesum + 50 * len(underattack) + 100 * uatower
