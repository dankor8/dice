from random import randint, choice
from time import sleep
from math import factorial
from matplotlib.pyplot import subplots, show, legend


def parseCommand():
    while True:
        command = input('> ').split()
        print()
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
                print('''Commands:
Enter (don't input anything) — simulate the next season;
/tutorial                         — view the tutorial that explains how to read commands in detail;
/profile dice full/until{number}? — view the profile of a dice including most recent {number} seasons;
/graph dice1 dice2? ...           — view the full league history of (a) dice;
/hall full/until{number}?         — view the Hall of Fame until position {number}.''')
            case '/tutorial':
                print('''Tutorial:
1. Basics
Inputs consist of commands and arguments.
The command is the first word of the input.
The arguments are all of the words excluding the command, separated by spaces.

Example:
In the input "/graph Noxixo Bolytip" "/graph" is the command, "Noxixo" and "Bolytip" are the arguments.
And in the input "/hall" "/hall" is the command and there are no arguments.
Situations like this can happen too, not all arguments are mandatory.

2. Commands
Commands always begin with a slash (/) and they determine what the input will do.
For example, if you input "/graph Nyhukim" the program will be able to tell that you want to \
see the history graph and not the profile of Nyhukim because the command is "/graph" and not "/profile".

3. Arguments
Arguments are additional to commands and determine what they will do.
Sometimes commands don't require arguments.
For example, if you input "/hall until5" and "/hall", the outcome will be the same.
That's because in the second scenario the program autocompletes the input to "/hall until5".
This happens if a question mark is placed after the argument in the help section ("/help"'s output).

Arguments like that are called optional, and the ones that don't have a question mark after them \
are called mandatory.
For example, if the help section has the following command info: "/profile dice full/until{number}?", \
this means that the "dice" argument is mandatory and the "full/until{number}" one is optional and \
can be skipped.

— "Wait! What is that slash doing between full and until?" — you may ask, however.
That slash separates multiple argument forms ("full" and "until{number}") that may be used \
depending on what you want to pass to the command. In this case passing "full" will \
print every season while passing "until{number}" will only print {number} of the most recent ones.''')
            case '/profile':
                try:
                    if not args:
                        raise Exception('This command requires an argument. You can pass an argument \
like this:\n/command argument')
                    if len(args) > 1:
                        mode = args[1]
                    else:
                        mode = 'until10'
                    find(args[0]).viewProfile(mode)
                except Exception as e:
                    print(e)
            case '/graph':
                try:
                    if season < 2:
                        raise Exception('Please wait until season 2 to use this command.\n\
There is not enough data for it yet.')
                    if not args:
                        raise Exception('This command requires an argument. You can pass an argument \
like this:\n/command argument')
                    ax = subplots()[1]
                    ax.invert_yaxis()
                    ovrCount = 0
                    for divCount, divColor in zip(DICE_COUNT + [0], DIV_COLORS + [ENDING_LINE_COLOR]):
                        ax.plot(range(1, season + 1), [ovrCount + .5 for _ in range(1, season + 1)], \
                                color=divColor, linestyle='dashed')
                        ovrCount += divCount
                    for dice in args:
                        find(dice).plotHistory(ax)
                    legend()
                    show()
                except Exception as e:
                    print(e)
            case '/hall':
                hall = list(filter(lambda x: sum(x.titles), sorted(Dice.instances, key=lambda x: -x.titles[0])))
                if len(args):
                    mode = args[0]
                else:
                    mode = 'until5'
                try:
                    until = int(mode.removeprefix('until'))
                except:
                    until = False
                if until and len(hall) >= until:
                    hall = hall[:until]
                
                data = [['№', 'Dice', 'League', 'G', 'S', 'B']]
                for i, dice in enumerate(hall, 1):
                    data.append([i, dice.name, dice.league.name, dice.titles[0], dice.titles[1], dice.titles[2]])
                printTable(data, [0, 1])
            case '':
                print()
                break
            case _:
                print('Invalid command. Use /help to get a list of valid commands.')
        print()


def find(origTarget):
    target = str(origTarget).lower()
    for obj in Dice.instances:
        if obj.name.lower() == target:
            return obj
    raise Exception(f'Invalid command argument: object "{origTarget}" was not found.')


def printTable(data, doubleSep = []):
    if len(data[0]) != len(data[1]):
        raise Exception('printTable(): not enough headers.')
    columnLens = [max(len(str(cell).removeprefix('!c;')) for cell in column) for column in zip(*data)]
    for row in data:
        for i, cell, columnLen in zip(range(len(row)), row, columnLens):
            if i in doubleSep:
                print('| ', end = '')
            elif i:
                print(' ', end = '')
            print(str(cell).removeprefix('!c;').center(columnLen) if data[0][i].find('!c;') != -1 else \
                  str(cell).ljust(columnLen), end = ' |\n' if i == len(row) - 1 else ' |')



class Side:
    def __init__(self, val, i):
        self.val = val
        self.i = i
    
    def __str__(self):
        return str(self.val)
     

class Dice:
    instances = []
    def __init__(self, quality, name = None):
        self.sides = [Side(side, i) for i, side in enumerate(sorted([randint(*quality) for _ in range(6)]), 1)]
        if not name:
            self.getName()
        else:
            self.name = name
        self.getColor()
        self.history = []
        self.titles = [0 for _ in range(DIV_COUNT)]
        self.instances.append(self)
    
    def getName(self):
        while True:
            consonants = 'qwrtypsdfghjklzxcvbnm'
            vowels = 'euioa'
            nextVowel = randint(1, 4) != 1
            self.name = ''
            for i in range(randint(4, 7)):
                if randint(1, 10) != 1:
                    nextVowel = not nextVowel
                self.name += choice(vowels if nextVowel else consonants)
            self.name = self.name.capitalize()
            try:
                find(self.name)
            except:
                break
    
    def getColor(self):
        self.color = '#'
        for _ in range(6):
            self.color += choice('0123456789abcdef')

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

    @property
    def pos(self):
        return self.league.dice.index(self) + 1
    
    @property
    def dpos(self):
        try:
            if self.league.level == self.history[-1]['league'].level:
                result = self.history[-1]['pos'] - self.pos
                if result > 0:
                    return f'{result}↑'
                elif not result:
                    return f'————'
                return f'{result}↓'
            elif self.league.level > self.history[-1]['league'].level:
                return 'Relg'
            return 'Prom'
        except:
            return 'New!'
        
    @classmethod
    def getRanking(self, historySeason):
        ranking = historySeason['pos']
        for i, divCount in enumerate(DICE_COUNT, 1):
            if historySeason['league'].level == i:
                break
            ranking += divCount
        return ranking

    def roll(self):
        return choice(self.sides)
    
    def update(self):
        dxpts = self.dxpts
        bonus = 0
        antibonus = 0

        self.history.append({
            'season': season,
            'sides': self.sides,
            'avr': self.avr,
            'strSides': self.strSides,
            'league': self.league,
            'pos': self.pos,
            'dpos': self.dpos,
            'p': self.p,
            'w': self.w,
            't': self.t,
            'l': self.l,
            'sd': self.sd,
            'tr': self.tr,
            'xpts': self.xpts,
            'dxpts': dxpts,
            'pts': self.pts,
            'apts': self.apts
        })
        if self.pos == 1:
            self.titles[self.league.level - 1] += 1
        
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
        
    def viewProfile(self, mode = f'until10'):
        def formatPos(pos):
            newPos = pos % 10 if not 10 < pos < 14 else 0
            match newPos:
                case 1:
                    return f'{pos}st'
                case 2:
                    return f'{pos}nd'
                case 3:
                    return f'{pos}rd'
            return f'{pos}th'
        
        try:
            until = int(mode.removeprefix('until'))
        except:
            until = False
        if until and len(self.history) >= until:
            history = self.history[-until:]
        else:
            history = self.history

        data = [['№', 'Sides', 'Avr', 'League', 'Pos', '!c;ΔPos', '!c;SiD', 'ToR', 'xPts', 'ΔxPts', 'Pts']]
        for historySeason in history:
            data.append([historySeason['season'], historySeason['strSides'], historySeason['avr'], \
                         historySeason['league'].name, formatPos(historySeason['pos']), historySeason['dpos'], \
                         historySeason['sd'], historySeason['tr'], historySeason['xpts'], historySeason['dxpts'], \
                         historySeason['pts']])

        print(f'''{self.name}'s profile:
League: {self.league.name};
Sides: {self.strSides};
Average: {self.avr};
Color: {self.color};

History{f" (type \"/profile {self.name} full\" to see more)" if until and len(self.history) > 10 else ""}:''')
        printTable(data, [1, 3, 6, 8, 10])

    def plotHistory(self, ax):
        ax.plot([historySeason['season'] for historySeason in self.history], [Dice.getRanking(historySeason) for historySeason in self.history], \
                self.color, marker='o', label=self.name)
   

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
        printIf(f'Odds to win/tie:\n{" " if d1Odds < 10 else ""}{d1Odds}% {self.d1.name} {self.d1.strSides}\n\
                {" " if tieOdds < 10 else ""}{tieOdds}% {"vs".center(12 + max(len(self.d1.name), len(self.d2.name))," ")}\n\
                {" " if d2Odds < 10 else ""}{d2Odds}% {self.d2.name} {self.d2.strSides}\n')
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
        print(f'{d1Fill} {" " if d1Percent < 10 else ""}{d1Percent}% {self.d1.name} {self.d1.strSides}\n{tieFill} \
              {" " if tiePercent < 10 else ""}{tiePercent}% {"vs".center(11 + max(len(self.d1.name), len(self.d2.name))," ")}\n{d2Fill} \
              {" " if d2Percent < 10 else ""}{d2Percent}% {self.d2.name} {self.d2.strSides}\n')
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
            dice.w = 0 # wins
            dice.t = 0 # ties
            dice.l = 0 # losses
            dice.sd = 0 # side difference
            dice.tr = 0 # total rolled
            dice.xpts = 0 # expected points
            dice.matches = []
            for side in dice.sides:
                side.w = 0 # rolls won
                side.t = 0 # rolls tied
                side.l = 0 # rolls lost
            
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
        data = [['№', '!c;ΔPos', 'Dice', 'Sides', 'Avr', 'P', 'W', 'T', 'L', '!c;SiD', 'ToR', 'xPts', 'ΔxPts', 'Pts', 'PPG']]
        for i, dice in enumerate(self.dice, 1):
            addon = ''
            if self.length - PROMOTION_SPOTS[self.level - 1] < i:
                addon = 'R'
            elif self.level - 1 and i <= PROMOTION_SPOTS[self.level - 2]:
                addon = 'P'
            data.append([str(i) + addon, dice.dpos, dice.name, dice.strSides, dice.avr, dice.p, dice.w, dice.t, dice.l, \
                         dice.sd, dice.tr, dice.xpts, dice.dxpts, dice.pts, dice.apts])
        
        print(f'\n\n{self.name} {f"standings after tour {self.matchCount - len(self.matches)}" if self.matches else \
                "final standings"} of season {season}:')
        printTable(data, [0, 2, 5, 9, 11, 13])
        if detail:
            input('Press Enter to continue: ')
        print('\n\n')



GAME_LENGTH = 5
DUPE_MATCHES = 2
POINTS_PER_WIN = 3
POINTS_PER_TIE = 1

DIV_COUNT = 3
DIV_NAMES = ['DiceRolls Gold League', 'DiceRolls Silver League', 'DiceRolls Bronze League']
DICE_QUALITY = [[2, 6], [2, 5], [1, 5], [1, 4]]
DICE_COUNT = [16, 20, 20]
DIV_COLORS = ["#a08010", "#909090", "#e07010"]
ENDING_LINE_COLOR = '#000000'
PROMOTION_SPOTS = [3, 4, 1]

VIEW_STANDINGS_EACH_TOUR = False
DETAIL = False

season = 0
divs = []
for j in range(DIV_COUNT):
    divs.append([Dice(DICE_QUALITY[j]) for _ in range(1, DICE_COUNT[j] + 1)])

while True:
    season += 1
    for i, div in enumerate(divs):
        divs[i] = League(i + 1, div, DIV_NAMES[i]).sim(DETAIL).dice
    parseCommand()

    for i in range(DIV_COUNT):
        if i == DIV_COUNT - 1:
            divs[i] = divs[i][:-PROMOTION_SPOTS[i]] + [Dice(DICE_QUALITY[-1]) for _ in range(PROMOTION_SPOTS[i])]
            continue
        divs[i], divs[i + 1] = divs[i][:-PROMOTION_SPOTS[i]] + divs[i + 1][:PROMOTION_SPOTS[i]], \
                               divs[i][-PROMOTION_SPOTS[i]:] + divs[i + 1][PROMOTION_SPOTS[i]:]
    
