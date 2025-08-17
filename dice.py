from random import randint, choice
from time import sleep
from math import factorial



def parseCommand():
    while True:
        command = input('> ').split()
        if not command:
            command = ''
        elif len(command) == 1:
            command = command[0]
            args = []
        else:
            args = command[1:]
            command = command[0]
    
        match command:
            case '/help':
                print('''/profile — view the profile of a dice.''')
            case '/profile':
                try:
                    find(args[0]).viewProfile()
                except Exception as e:
                    print(e)
            case '':
                break
            case _:
                print('Invalid command.')


def find(origTarget):
    target = str(origTarget).lower()
    for obj in Dice.instances:
        if obj.name.lower() == target:
            return obj
    raise Exception(f'Object "{origTarget}" was not found.')



class Side:
    def __init__(self, val, i):
        self.val = val
        self.i = i
    
    def __str__(self):
        return str(self.val)
     

class Dice:
    instances = []
    def __init__(self, sides, name = None):
        if len(sides) != 6:
            raise Exception(f'Dice object doesn\'t have 6 sides: {sides}.')
        self.instances.append(self)
        self.sides = [Side(side, i) for i, side in enumerate(sides, 1)]
        if not name:
            self.getName()
        else:
            self.name = name
    
    def getName(self):
        consonants = 'qwrtypsdfghjklzxcvbnm'
        vowels = 'euioa'
        nextVowel = randint(1, 4) != 1
        self.name = ''
        for i in range(randint(4, 7)):
            if randint(1, 10) != 1:
                nextVowel = not nextVowel
            self.name += choice(vowels if nextVowel else consonants)
        self.name = self.name.capitalize()  
    
    @property
    def strSides(self):
        return ' '.join(str(side) for side in self.sides)
    
    @property
    def sum(self):
        return sum(side.val for side in self.sides)
    
    @property
    def avr(self):
        return round(self.sum / 6, 1)
    
    @property
    def pts(self):
        return self.w * POINTS_PER_WIN + self.t * POINTS_PER_TIE
        
    @property
    def apts(self):
        return round(self.pts / len(self.matches), 1)
        
    @property
    def p(self):
        return self.w + self.t + self.l
       
    @property
    def dxpts(self):
        return round(self.pts - self.xpts, 1)
        
    def roll(self):
        return choice(self.sides)
    
    def update(self):
        dxpts = self.dxpts
        bonus = 0
        antibonus = 0
        if dxpts > 18:
            bonus += 1
        if dxpts > 11:
            bonus += 1
        if dxpts > 5:
            bonus += 1
        if dxpts < -5:
            antibonus += 1
        if dxpts < -11:
            antibonus += 1
        if dxpts < -18:
            antibonus += 1
        
        for i in range(len(self.sides)):
            if randint(1, 10) == 10:
                self.sides[i] = Side(randint(*DICE_QUALITY[self.league.level - 1]), i)
        
        for _ in range(bonus):
            self.roll().val += 1
        for _ in range(antibonus):
            side = self.roll()
            if side.val > 1:
                side.val -= 1
        self.sides = sorted(self.sides, key = lambda x: x.val)
        
    def viewProfile(self):
        print(f'''{self.name}'s profile:
Sides: {self.strSides};
History (type "/history {self.name}" to see more):
### TODO ###''')

    def plotHistory(self):
        pass
   

class Match:
    def __init__(self, d1, d2):
        self.d1 = d1
        self.d2 = d2
        self.bye = not d1 or not d2
        if self.d1:
            self.d1.matches.append(self)
        if self.d2:
            self.d2.matches.append(self)
        
    def play(self, detail = False, fast = False):
        d1Score = 0
        d2Score = 0
        
        def printIf(text, time = 0):
            if detail:
                print(text)
                if not fast and time:
                    sleep(time)
        
        if detail:
            self.printCompare()
        d1Odds, tieOdds, d2Odds = self.odds()
        printIf(f'Odds to win/tie:\n{" " if d1Odds < 10 else ""}{d1Odds}% {self.d1.name} {self.d1.strSides}\n{" " if tieOdds < 10 else ""}{tieOdds}% {"vs".center(12 + max(len(self.d1.name), len(self.d2.name))," ")}\n{" " if d2Odds < 10 else ""}{d2Odds}% {self.d2.name} {self.d2.strSides}\n')
        if detail:
            input('Press Enter to begin the match: ')
            
        for i in range(1, GAME_LENGTH + 1):
            printIf(f'\nCurrent score: {d1Score}–{d2Score}.\nRoll {i}:', 2)
            d1Roll = self.d1.roll()
            d2Roll = self.d2.roll()
            if d1Roll.val > d2Roll.val:
                result = f'{d1Roll} > {d2Roll}, so {self.d1.name} wins.'
                d1Score += 1
                d1Roll.w += 1
                d2Roll.l += 1
            elif d1Roll.val == d2Roll.val:
                result = f'{d1Roll} = {d2Roll}, so this is a tie.'
                d1Roll.t += 1
                d2Roll.t += 1
            else:
                result = f'{d1Roll} < {d2Roll}, so {self.d2.name} wins.'
                d2Score += 1
                d1Roll.l += 1
                d2Roll.w += 1
            printIf(f'{self.d1.name}: {d1Roll}.', 1)
            printIf(f'{self.d2.name}: {d2Roll}.', 1)
            printIf(result)
        if d1Score > d2Score:
            gameResult = f'{self.d1.name} wins.'
            self.d1.w += 1
            self.d2.l += 1
        elif d1Score < d2Score:
            gameResult = f'{self.d2.name} wins.'
            self.d1.l += 1
            self.d2.w += 1
        else:
            gameResult = 'This is a tie.'
            self.d1.t += 1
            self.d2.t += 1
            
        self.d1.sd += d1Score - d2Score
        self.d2.sd += d2Score - d1Score
        self.d1.tr += d1Score
        self.d2.tr += d2Score
        odds = self.odds()
        self.d1.xpts += odds[0] * POINTS_PER_WIN / 100 + odds[1] * POINTS_PER_TIE / 100
        self.d2.xpts += odds[1] * POINTS_PER_TIE / 100 + odds[2] * POINTS_PER_WIN / 100
        self.d1.xpts = round(self.d1.xpts, 1)
        self.d2.xpts = round(self.d2.xpts, 1)
        
        printIf(f'\n\nFinal score: {d1Score}–{d2Score}.')
        printIf(gameResult)
        if detail:
            input('\n\nPress Enter to finish the match: ')
        
    def compare(self, d1Fill = 1, d2Fill = 2, tieFill = 0, oneD = False):
        result = []
        for s1 in self.d1.sides:
            result.append([])
            for s2 in self.d2.sides:
                if s1.val > s2.val:
                    result[-1].append(d1Fill)
                elif s1.val == s2.val:
                    result[-1].append(tieFill)
                else:
                    result[-1].append(d2Fill)
        if oneD:
            return [res for line in result for res in line]
        return result
    
    def comparePercent(self):
        comp = self.compare(oneD = True)
        d1Percent = round(comp.count(1) / 36 * 100)
        d2Percent = round(comp.count(2) / 36 * 100)
        tiePercent = 100 - d1Percent - d2Percent
        return [d1Percent, tiePercent, d2Percent]
    
    def printCompare(self, d1Fill = '1', d2Fill = '2', tieFill = '—'):
        result = self.compare(d1Fill, d2Fill, tieFill)
        d1Percent, tiePercent, d2Percent = self.comparePercent()
        "".join(["—" for _ in range(len(self.d2.strSides) * 2)])
        print('Dice comparison per roll:')
        print(f'{d1Fill} {" " if d1Percent < 10 else ""}{d1Percent}% {self.d1.name} {self.d1.strSides}\n{tieFill} {" " if tiePercent < 10 else ""}{tiePercent}% {"vs".center(11 + max(len(self.d1.name), len(self.d2.name))," ")}\n{d2Fill} {" " if d2Percent < 10 else ""}{d2Percent}% {self.d2.name} {self.d2.strSides}\n')
        print(f'  | {" ".join(str(side) for side in self.d2.sides)}\n{"".join(["—" for _ in range(3 + len(self.d2.sides)*2)])}')
        for side, line in zip(self.d1.sides, result):
            print(f'{side} | {' '.join(line)}')
        print('\n')
     
    def odds(self):
        d1Percent, tiePercent, d2Percent = self.comparePercent()
        d1Prob = d1Percent / 100
        tieProb = tiePercent / 100
        d2Prob = d2Percent / 100
    
        def binomial(p1, p2, p3, k1, k2, k3):
            total = k1 + k2 + k3
            return (factorial(total) / (factorial(k1) * factorial(k2) * factorial(k3))) * (p1**k1) * (p2**k2) * (p3**k3)
    
        d1Win = 0
        tie = 0
        d2Win = 0
    
        for k1 in range(GAME_LENGTH + 1):
            for k2 in range(GAME_LENGTH + 1 - k1):
                k3 = GAME_LENGTH - k1 - k2
                prob = binomial(d1Prob, tieProb, d2Prob, k1, k2, k3)
                if k1 > k3:
                    d1Win += prob
                elif k1 == k3:
                    tie += prob
                else:
                    d2Win += prob
   
        return [round(d1Win * 100), 100 - round(d1Win * 100) - round(d2Win * 100), round(d2Win * 100)]


class League:
    def __init__(self, level, dice, name):
        self.level = level
        self.dice = dice
        for dice in self.dice:
            dice.league = self
            dice.w = 0 #wins
            dice.t = 0 #ties
            dice.l = 0 #losses
            dice.sd = 0 #side difference
            dice.tr = 0 #points won
            dice.xpts = 0 #expected points
            dice.matches = []
            for side in dice.sides:
                side.w = 0 #rolls won
                side.t = 0 #rolls tied
                side.l = 0 #rolls lost
            
        self.length = len(self.dice)
        self.name = name

        self.matches = []
        if self.length % 2:
            
            origTeams = list(self.dice) + [None]
        else:
            origTeams = list(self.dice)
        teams = list(origTeams)
        
        for split in range(DUPE_MATCHES):
            for round in range(self.length - 1):
                round = []
                for i in range(self.length // 2):
                    match = Match(teams[i], teams[self.length - 1 - i])
                    if not match.bye:
                        round.append(match)
                self.matches.append(round)
            
                teams.insert(1, teams.pop())
            origTeams.reverse()
            teams = origTeams
        self.matchCount = len(self.matches)
    
    def sim(self, detail = False):
        for i in range(len(self.matches)):
            self.simDay(detail)
            if detail or VIEW_STANDINGS_EACH_TOUR:
                self.viewTable()
        if not detail and not VIEW_STANDINGS_EACH_TOUR:
            self.viewTable(detail)
        
        for dice in self.dice:
            dice.update()
        return self
    
    def simDay(self, detail):
        for match in self.matches.pop():
            match.play(detail, True)

    def viewTable(self, detail):
        self.dice = sorted(self.dice, key=lambda dice: -dice.pts * 1000000 - dice.sd * 1000 - dice.tr)
        data = [['№', 'Dice', 'Sides', 'Avr', 'P', 'W', 'T', 'L', 'SD', 'TR', 'xPts', 'ΔxPts', 'Pts', 'PPG']]
        # Avr - average value of dice's sides
        # 
        sepAfter = [0, 1, 4, 8, 10, 12]
        for i, dice in enumerate(self.dice, 1):
            addon = ''
            if self.level != DIV_COUNT and self.length - PROMOTION_SPOTS[self.level - 1] < i:
                addon = 'R'
            elif self.level - 1 and i <= PROMOTION_SPOTS[self.level - 2]:
                addon = 'P'
            data.append([str(i) + addon, dice.name, dice.strSides, dice.avr, dice.p, dice.w, dice.t, dice.l, dice.sd, dice.tr, dice.xpts, dice.dxpts, dice.pts, dice.apts])
        
        print(f'\n\n{self.name} {f"standings after tour {self.matchCount - len(self.matches)}" if self.matches else "final standings"} of season {season}:')
        columnLens = [max(len(str(cell).removeprefix('!c;')) for cell in column) for column in zip(*data)]
        for row in data:
            for i, cell, columnLen in zip(range(len(row)), row, columnLens):
                if i in sepAfter:
                    print('| ', end = '')
                elif i:
                    print(' ', end = '')
                print(str(cell).removeprefix('!c;').center(columnLen) if data[0][i].find('!c;') != -1 else str(cell).ljust(columnLen), end = ' |\n' if i == len(row) - 1 else ' |')
        if detail or self.level == DIV_COUNT:
            parseCommand()
        print('\n\n')



GAME_LENGTH = 5
DUPE_MATCHES = 2
POINTS_PER_WIN = 3
POINTS_PER_TIE = 1

NAME_LETTER_COUNT = 2
NAME_NUMBER_COUNT = 2

DIV_COUNT = 3
DIV_NAMES = ['DiceRolls Gold League', 'DiceRolls Silver League', 'DiceRolls Bronze League']
DICE_QUALITY = [[2, 6], [2, 5], [1, 5]]
DICE_COUNT = [16, 20, 20]
PROMOTION_SPOTS = [3, 4]
VIEW_STANDINGS_EACH_TOUR = False
DETAIL = False

season = 0
divs = []
for j in range(DIV_COUNT):
    divs.append([Dice(sorted([randint(*DICE_QUALITY[j]) for _ in range(6)])) for i in range(1, DICE_COUNT[j] + 1)])

while True:
    season += 1
    for i, div in enumerate(divs):
        divs[i] = League(i + 1, div, DIV_NAMES[i]).sim(DETAIL).dice
        
    for i in range(len(divs) - 1):
        divs[i], divs[i + 1] = divs[i][:-PROMOTION_SPOTS[i]] + divs[i + 1][:PROMOTION_SPOTS[i]], divs[i][-PROMOTION_SPOTS[i]:] + divs[i + 1][PROMOTION_SPOTS[i]:]
