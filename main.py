from numpy.lib.function_base import average
import pygame,sys,math,random,os
from pygame.image import load

from tile import *
from perlin import *

SCREEN_WIDTH = 750
SCREEN_HEIGHT = 500

WHITE   =  (255, 255, 255)
ORANGE  =  (255, 127, 0  )
YELLOW  =  (255, 255, 0  )
BLACK   =  (0,   0,   0  )
BLUE    =  (0,   0,   255)
RED     =  (255, 0,   0  )
SKYBLUE =  (135, 206, 235)
SLIVER  =  (192, 192, 192)
camX = 0
camY = 0

class Map:
    def __init__(self) -> None:
        self.tiles = {}
        self.river = {}
        self.riverList = []
    
    def addTile(self,location,tileType,const = None):
        newId = len(self.tiles)
        newTile = Tile(
                newId,
                tileType,
                const,
                location
            )
        self.tiles[tuple(location)] = newTile
    
    def getNearTiles(self, location, option = False):
        result = [None,None,None,None,None,None]
        nearLocations = [
            (-1,  2),
            ( 1,  1),
            ( 2, -1),
            ( 1, -2),
            (-1, -1),
            (-2,  1)
        ]
        for i in range(len(nearLocations)):
            nearLocation = nearLocations[i]
            near = (location[0] + nearLocation[0], location[1] + nearLocation[1])
            if self.tiles.get(near) is not None: result[i] = self.tiles[near] if option else near
        return result
    
    def getFarTiles(self, location, radius, option = False):
        result = [None for i in range(6*radius)]
        nearLocations = [
            ( 2,  1),
            ( 1, -2),
            (-1, -1),
            (-2,  1),
            (-1,  2),
            ( 1,  1)
        ]
        nowLocation = list(location)
        nowLocation[0] -= radius
        nowLocation[1] += 2 * radius
        for i in range(len(nearLocations)):
            nearLocation = nearLocations[i]
            for j in range(radius):
                near = tuple(nowLocation)
                if self.tiles.get(near) is not None: result[i*radius + j] = self.tiles[near] if option else near
                nowLocation[0] += nearLocation[0]
                nowLocation[1] += nearLocation[1]
        return result
    
    def draw(self,screen):
        nearLocations = [
            ( 2,  1),
            ( 1, -2),
            (-1, -1),
            (-2,  1),
            (-1,  2),
            ( 1,  1)
        ]
        for i in range(len(self.tiles.keys())):
            location = list(self.tiles.keys())[i]
            tile = self.tiles[location]
            move = list(location)
            move[0] = location[0] * 25
            move[0] += SCREEN_WIDTH/2 - camX - 25
            move[1] -= location[1] * 25 * c
            move[1] -= location[0] * 12.5 * c
            move[1] += SCREEN_HEIGHT/2 - camY - 25
            rect = pygame.Rect(0,0,0,0).move(move)
            screen.blit(tile.img,rect)
            move[0] -= 10
            move[1] += 26.5
            if tile.resource is not None:
                moveLoc = list(location)
                moveLoc[0] = location[0] * 25
                moveLoc[0] += SCREEN_WIDTH/2 - camX - 10
                moveLoc[1] -= location[1] * 25 * c
                moveLoc[1] -= location[0] * 12.5 * c
                moveLoc[1] += SCREEN_HEIGHT/2 - camY - 10
                rect = pygame.Rect(0,0,0,0).move(moveLoc)
                screen.blit(tile.resource().img,rect)
            if tile.bread:
                move[0] += 20
                rect = pygame.Rect(0,0,0,0).move(move)
                screen.blit(IMAGE[f"{tile.bread}식"],rect)
            if tile.hammer:
                move[0] += 20
                rect = pygame.Rect(0,0,0,0).move(move)
                screen.blit(IMAGE[f"{tile.hammer}망"],rect)
            if tile.science:
                move[0] += 20
                rect = pygame.Rect(0,0,0,0).move(move)
                screen.blit(IMAGE[f"{tile.science}과"],rect)
            if tile.gold:
                move[0] += 20
                rect = pygame.Rect(0,0,0,0).move(move)
                screen.blit(IMAGE[f"{tile.gold}금"],rect)
            
        for i in self.riverList:
            loc1 = list(i)
            loc2 = list(self.river[i])
            x = loc1[0]
            y = loc1[1]
            theta = math.atan2(loc1[0]-loc2[0],loc1[1]-loc2[1])
            loc1[0] = x * 25
            loc1[0] += SCREEN_WIDTH/2 - camX
            loc1[0] += 25 * math.cos(theta + math.pi/2)
            loc1[1] -= y * 25 * c
            loc1[1] -= x * 12.5* c
            loc1[1] += 25 * c * math.sin(theta + math.pi/2)
            loc1[1] += SCREEN_HEIGHT/2 - camY
            x = loc2[0]
            y = loc2[1]
            loc2[0] = x * 25
            loc2[0] += SCREEN_WIDTH/2 - camX
            loc2[0] += 25 * math.cos(theta - math.pi/2)
            loc2[1] -= y * 25 * c
            loc2[1] -= x * 12.5 * c
            loc1[1] += 25 * c * math.sin(theta - math.pi/2)
            loc2[1] += SCREEN_HEIGHT/2 - camY
            pygame.draw.circle(screen,BLUE,((loc1[0]+loc2[0])/2, (loc1[1]+loc2[1])/2),5)

if __name__ == "__main__":
    filterAdapt = (input("필터 적용?(N : 적용 안함)") != "N")
    pygame.init()
    pygame.display.set_caption("CIVILIZATION SIMULATION")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    print("이미지 세팅 시작...")
    IMAGE = {
        "바다자원"      : load(os.path.join(".","img","바다자원.png")),
        "사막-범람원"   : load(os.path.join(".","img","사막-범람원.png")),
        "사막-언덕"     : load(os.path.join(".","img","사막-언덕.png")),
        "사막"          : load(os.path.join(".","img","사막.png")),
        "산"            : load(os.path.join(".","img","산.png")),
        "산호초"        : load(os.path.join(".","img","산호초.png")),
        "석재"          : load(os.path.join(".","img","석재.png")),
        "숲"            : load(os.path.join(".","img","숲.png")),
        "오아시스"      : load(os.path.join(".","img","오아시스.png")),
        "전략자원"      : load(os.path.join(".","img","전략자원.png")),
        "초원-범람원"   : load(os.path.join(".","img","초원-범람원.png")),
        "초원-습지"     : load(os.path.join(".","img","초원-습지.png")),
        "초원-언덕"     : load(os.path.join(".","img","초원-언덕.png")),
        "초원"          : load(os.path.join(".","img","초원.png")),
        "평원-범람원"   : load(os.path.join(".","img","평원-범람원.png")),
        "평원-언덕"     : load(os.path.join(".","img","평원-언덕.png")),
        "평원-열대우림" : load(os.path.join(".","img","평원-열대우림.png")),
        "평원"          : load(os.path.join(".","img","평원.png")),
        "해안"          : load(os.path.join(".","img","해안.png")),
        "해양"          : load(os.path.join(".","img","해양.png")),
        "호수"          : load(os.path.join(".","img","호수.png")),

        "1과"           : load(os.path.join(".","img","tileBonus","1과.png")),
        "1금"           : load(os.path.join(".","img","tileBonus","1금.png")),
        "1망"           : load(os.path.join(".","img","tileBonus","1망.png")),
        "1문"           : load(os.path.join(".","img","tileBonus","1문.png")),
        "1식"           : load(os.path.join(".","img","tileBonus","1식.png")),
 
        "2과"           : load(os.path.join(".","img","tileBonus","2과.png")),
        "2금"           : load(os.path.join(".","img","tileBonus","2금.png")),
        "2망"           : load(os.path.join(".","img","tileBonus","2망.png")),
        "2문"           : load(os.path.join(".","img","tileBonus","2문.png")),
        "2식"           : load(os.path.join(".","img","tileBonus","2식.png")),
 
        "3과"           : load(os.path.join(".","img","tileBonus","3과.png")),
        "3금"           : load(os.path.join(".","img","tileBonus","3금.png")),
        "3망"           : load(os.path.join(".","img","tileBonus","3망.png")),
        "3문"           : load(os.path.join(".","img","tileBonus","3문.png")),
        "3식"           : load(os.path.join(".","img","tileBonus","3식.png")),
 
        "4과"           : load(os.path.join(".","img","tileBonus","4과.png")),
        "4금"           : load(os.path.join(".","img","tileBonus","4금.png")),
        "4망"           : load(os.path.join(".","img","tileBonus","4망.png")),
        "4문"           : load(os.path.join(".","img","tileBonus","4문.png")),
        "4식"           : load(os.path.join(".","img","tileBonus","4식.png")),
 
        "5과"           : load(os.path.join(".","img","tileBonus","5과.png")),
        "5금"           : load(os.path.join(".","img","tileBonus","5금.png")),
        "5망"           : load(os.path.join(".","img","tileBonus","5망.png")),
        "5문"           : load(os.path.join(".","img","tileBonus","5문.png")),
        "5식"           : load(os.path.join(".","img","tileBonus","5식.png")),
    }

    for i in IMAGE.keys() :
        c = 215/186
        size = 50
        IMAGE[i] = pygame.transform.scale(IMAGE[i], (50, round(50*c)))
        prod = ['1식','1망','1과','1금',
                '2식','2망','2과','2금',
                '3식','3망','3과','3금',
                '4식','4망','4과','4금',
                '5식','5망','5과','5금']
        if i in prod:
            num = int(i[0])
            if num == 1:
                IMAGE[i] = pygame.transform.scale(IMAGE[i], (10, 10))
            elif num == 2:
                IMAGE[i] = pygame.transform.scale(IMAGE[i], (10, 20))
            elif num == 3:
                IMAGE[i] = pygame.transform.scale(IMAGE[i], (20, 20))
            elif num == 4:
                IMAGE[i] = pygame.transform.scale(IMAGE[i], (20, 20))
            elif num == 5:
                IMAGE[i] = pygame.transform.scale(IMAGE[i], (20, 20))
        prod = ['석재','전략자원','바다자원']
        if i in prod:
            IMAGE[i] = pygame.transform.scale(IMAGE[i], (20, round(20 * c)))
    setImage(IMAGE)
    print("이미지 세팅 완료...")
    print("맵 생성 시작...")
    size = 20
    seed = 83825
    #seed = random.randint(0,100000)
    print(seed)
    randomClimate = getPerlin(size,1,seed)
    randomClimate += getPerlin(size,3,seed)
    randomClimate += getPerlin(size,7,seed)
    randomClimate = list(randomClimate)
    averageClimate = average(list(map(lambda x: average(x),randomClimate)))
    randomClimate = list(map(lambda x: list(x),randomClimate))

    randomPlains = getPerlin(size,1,seed)
    randomPlains += getPerlin(size,3,seed)
    randomPlains += getPerlin(size,5,seed)
    randomPlains += getPerlin(size,7,seed)
    randomPlains += getPerlin(size,9,seed)
    randomPlains = list(randomPlains)
    averagePlains = average(list(map(lambda x: average(x),randomPlains)))
    randomPlains = list(map(lambda x: list(x),randomPlains))

    randomMap = getPerlin(size,1,seed)
    randomMap += getPerlin(size,3,seed)
    #randomMap += getPerlin(size,5)
    randomMap = list(getPerlin(size,7,seed))
    averageHeight = average(list(map(lambda x: average(x),randomMap)))
    randomMap = list(map(lambda x: list(x),randomMap))
    hills = []
    coasts = []
    grounds = []
    for y in range(size):
        for x in range(size):
            if randomMap[y][x] < averageHeight - 0.2:
                randomMap[y][x] = Ocean
            elif randomMap[y][x] < averageHeight - 0.1:
                if randomClimate[y][x] < -0.4:
                    randomMap[y][x] = Reef
                else:
                    randomMap[y][x] = Coast
            elif randomMap[y][x] < averageHeight + 0.2:
                if randomClimate[y][x] < averageClimate - 0.8:
                    randomMap[y][x] = Oasis
                elif randomClimate[y][x] < averageClimate - 0.3:
                    randomMap[y][x] = Desert
                elif randomClimate[y][x] > averageClimate + 0.4:
                    if randomPlains[y][x] < averagePlains + 0.1:
                        randomMap[y][x] = Forest
                    else:
                        randomMap[y][x] = Jungle
                else:
                    if randomPlains[y][x] < averagePlains + 0.1:
                        randomMap[y][x] = Glassland
                    else:
                        randomMap[y][x] = Plains
            elif randomMap[y][x] < averageHeight + 0.4:
                if randomClimate[y][x] < averageClimate - 0.2:
                    randomMap[y][x] = DesertHill
                else:
                    if randomPlains[y][x] < averagePlains + 0.1:
                        randomMap[y][x] = GlasslandHill
                    else:
                        randomMap[y][x] = PlainsHill
            else:
                randomMap[y][x] = Mountain
    myMap = Map()
    maker = [-8,12]
    for y in range(size):
        maker[0] = -8 - y%2
        for x in range(size):
            myMap.addTile(tuple(maker),randomMap[y][x])
            hill = [GlasslandHill,PlainsHill,DesertHill]
            flat = [Glassland,Desert,Forest,Jungle]
            if randomMap[y][x] in hill:
                hills.append(tuple(maker))
            if randomMap[y][x] in (hill+flat):
                grounds.append(tuple(maker))
            if randomMap[y][x] == Coast:
                coasts.append(tuple(maker))
            maker[0] += 2
            maker[1] -= 1
        maker[1] += size-2 if y%2 == 1 else size-1
    random.seed(seed)
    riverCount = random.randint(10,15)
    for i in range(riverCount):
        random.seed(seed)
        coast = random.choice(coasts)
        nearGround = {}
        while len(nearGround) < 2: 
            random.seed(seed)
            coast = random.choice(coasts)
            near = myMap.getNearTiles(coast,True)
            ground = [Glassland,Desert,Forest,Jungle,GlasslandHill,PlainsHill,DesertHill]
            nearGround = {}
            for i in near:
                if i is not None:
                    if i.tileType in ground:
                        nearGround[i.location] = i
        nearLocations = [
            ( 2,  1),
            ( 1, -2),
            (-1, -1),
            (-2,  1),
            (-1,  2),
            ( 1,  1)
        ]
        for i in nearGround.keys():
            near = set(myMap.getNearTiles(i))
            for j in near:
                if j in nearGround.keys() and j is not None:
                    myMap.river[i] = j
                    myMap.river[j] = i
                    myMap.riverList.append(i)
                    anotherNear = set(myMap.getNearTiles(j))
                    for k in anotherNear:
                        out = False
                        anotherTile = myMap.getNearTiles(j,True)
                        for p in anotherTile:
                            if p is not None:
                                if not (p.tileType in ground or p.tileType == Mountain):
                                    out = True
                                    break
                        if out:
                            break
                        if i in myMap.getNearTiles(k):
                            myMap.river[j] = k
                            myMap.river[k] = j
                            myMap.riverList.append(j)
                            break
                    break
    
    resoureceCount = 5
    random.seed(seed)
    resourcefulStone = random.sample(grounds,resoureceCount)
    for i in resourcefulStone:
        myMap.tiles[i].hammer += 1
        myMap.tiles[i].resource = Stone
    random.seed(seed)
    resourceful = random.sample(coasts,resoureceCount)
    for i in resourceful:
        myMap.tiles[i].hammer += 1
        myMap.tiles[i].gold += 1
        myMap.tiles[i].resource = SeaResource
    random.seed(seed)
    resourceful = set(random.sample(grounds,resoureceCount)) - set(resourcefulStone)
    for i in resourceful:
        myMap.tiles[i].hammer += 2
        myMap.tiles[i].resource = StrategyResource

    print("맵 생성 완료...")
    print("분석 시작...")
    analyze = {
        "산출량" : {},
        "자원" : {},
        "시설" : {},
        "캠퍼스" : {},
        "성지" : {},
        "항만" : {},
        "상업중심지" : {},
        "산업구역" : {},
        "극장가" : {},
        "담수" : {},
        "교통" : {},
        "최종" : {}
    }
    maxWorkNum = 10
    print(f"산출량 및 자원 분석 시작...(1/{maxWorkNum})")
    for i in range(len(myMap.tiles.keys())):
        loc = list(myMap.tiles.keys())[i]
        analyze["산출량"][loc] = myMap.tiles[loc].bread * 3 + myMap.tiles[loc].hammer * 3 + myMap.tiles[loc].gold
        resourceScore = 0
        if myMap.tiles[loc].resource == Stone:
            resourceScore += 2
        elif myMap.tiles[loc].resource == SeaResource:
            resourceScore += 4
        elif myMap.tiles[loc].resource == StrategyResource:
            resourceScore += 8
        analyze["자원"][loc] = resourceScore
        things = [GlasslandHill,PlainsHill,DesertHill,Plains,Glassland,Forest,Jungle]
        score = 0
        if myMap.tiles[loc].tileType in things:
            score += 2
        elif myMap.tiles[loc].resource == SeaResource:
            score += 2
        analyze["시설"][loc] = score
    print(f"산출량, 자원 및 시설 분석 완료...(1/{maxWorkNum})")
    print(f"캠퍼스 분석 시작...(2/{maxWorkNum})")
    for i in range(len(myMap.tiles.keys())):
        loc = list(myMap.tiles.keys())[i]
        near = myMap.getNearTiles(loc,True)
        score = 0
        jungle = 0
        availAdvanced = 0
        mainAdvanced = False
        for tile in near:
            if tile is not None:
                if str(tile.tileType()) == "열대우림":
                    jungle += 1
                    if not jungle%2:
                        score += 1
                if str(tile.tileType()) == "산":
                    score += 1
                noAdvance = ["산","오아시스","산호초"]
                if not str(tile.tileType()) in noAdvance:
                    if not mainAdvanced:
                        score += 1
                        mainAdvanced = True
                    else:
                        availAdvanced += 1
                        if not availAdvanced%2:
                            score += 1
                if str(tile.tileType()) == "산호초":
                    score += 2
        analyze["캠퍼스"][loc] = score/5
    #print(max(analyze["캠퍼스"].values()))
    print(f"캠퍼스 분석 완료...(2/{maxWorkNum})")
    print(f"성지 분석 시작...(3/{maxWorkNum})")
    for i in range(len(myMap.tiles.keys())):
        loc = list(myMap.tiles.keys())[i]
        near = myMap.getNearTiles(loc,True)
        score = 0
        forest = 0
        availAdvanced = 0
        mainAdvanced = False
        for tile in near:
            if tile is not None:
                if str(tile.tileType()) == "숲":
                    forest += 1
                    if not forest%2:
                        score += 1
                if str(tile.tileType()) == "산":
                    score += 1
                noAdvance = ["산","오아시스","산호초"]
                if not str(tile.tileType()) in noAdvance:
                    if not mainAdvanced:
                        score += 1
                        mainAdvanced = True
                    else:
                        availAdvanced += 1
                        if not availAdvanced%2:
                            score += 1
        analyze["성지"][loc] = score/3
    print(f"성지 분석 완료...(3/{maxWorkNum})")
    print(f"항만 분석 시작...(4/{maxWorkNum})")
    for i in range(len(myMap.tiles.keys())):
        loc = list(myMap.tiles.keys())[i]
        near = myMap.getNearTiles(loc,True)
        score = 0
        availAdvanced = 0
        mainAdvanced = False
        notGround = [Mountain,Oasis,Coast,Ocean,Lake]
        for tile in near:
            if tile is not None:
                if not tile.tileType in notGround:
                    score += 2
                    break
        for tile in near:
            if tile is not None:
                noAdvance = ["산","오아시스","산호초"]
                if not str(tile.tileType()) in noAdvance:
                    if not mainAdvanced:
                        score += 1
                        mainAdvanced = True
                    else:
                        availAdvanced += 1
                        if not availAdvanced%2:
                            score += 1
                if tile.resource == SeaResource:
                    score+=1
        analyze["항만"][loc] = score/3.5
    print(f"항만 분석 완료...(4/{maxWorkNum})")
    print(f"상업중심지 분석 시작...(5/{maxWorkNum})")
    for i in range(len(myMap.tiles.keys())):
        loc = list(myMap.tiles.keys())[i]
        near = myMap.getNearTiles(loc,True)
        score = 0
        availAdvanced = 0
        mainAdvanced = False
        notGround = [Coast,Ocean,Lake]
        harbor = 0
        for tile in near:
            if tile is not None:
                if not tile.tileType in notGround:
                    harbor += 1
                    if harbor %2 :
                        score += 2
                noAdvance = ["산","오아시스","산호초"]
                if not str(tile.tileType()) in noAdvance:
                    if not mainAdvanced:
                        score += 1
                        mainAdvanced = True
                    else:
                        availAdvanced += 1
                        if not availAdvanced%2:
                            score += 1
                if myMap.river.get(tile.location) is not None:
                    score+=2
        analyze["상업중심지"][loc] = score/4
    print(f"상업중심지 분석 완료...(5/{maxWorkNum})")
    print(f"산업구역 분석 시작...(6/{maxWorkNum})")
    for i in range(len(myMap.tiles.keys())):
        loc = list(myMap.tiles.keys())[i]
        near = myMap.getNearTiles(loc,True)
        score = 0
        availAdvanced = 0
        mainAdvanced = False
        notGround = [Coast,Ocean,Lake]
        mine = 0
        forest = 0
        for tile in near:
            if tile is not None:
                if tile.tileType in hills:
                    mine += 1
                    if mine %2 :
                        score += 1
                if str(tile.tileType()) == '숲' or str(tile.tileType()) == '평원-열대우림':
                    forest += 1
                    if forest %2 :
                        score += 1
                noAdvance = ["산","오아시스","산호초"]
                if not str(tile.tileType()) in noAdvance:
                    if not mainAdvanced:
                        score += 1
                        mainAdvanced = True
                    else:
                        availAdvanced += 1
                        if not availAdvanced%2:
                            score += 1
                around = myMap.getNearTiles(tile.location,True) + myMap.getFarTiles(tile.location,2,True)
                for i in around:
                    if i is not None:
                        if str(i.tileType()) == "산" or str(i.tileType()) == "오아시스":
                            score += 2
                            break
                if tile.resource == StrategyResource:
                    score+=1
                if tile.resource == Stone:
                    score+=1
        analyze["산업구역"][loc] = score/6.5
    print(f"산업구역 분석 완료...(6/{maxWorkNum})")
    print(f"극장가 분석 시작...(7/{maxWorkNum})")
    for i in range(len(myMap.tiles.keys())):
        loc = list(myMap.tiles.keys())[i]
        near = myMap.getNearTiles(loc,True)
        score = 0
        availAdvanced = 0
        mainAdvanced = False
        entertain = False
        forest = 0
        for tile in near:
            if tile is not None:
                noAdvance = ["산","오아시스","산호초"]
                if not str(tile.tileType()) in noAdvance:
                    if not mainAdvanced:
                        score += 1
                        mainAdvanced = True
                    elif not entertain:
                        score += 2
                        entertain = True
                    else:
                        availAdvanced += 1
                        if not availAdvanced%2:
                            score += 1
        analyze["극장가"][loc] = score/3.5
    print(f"극장가 분석 완료...(7/{maxWorkNum})")
    print(f"담수 분석 시작...(8/{maxWorkNum})")
    for i in range(len(myMap.tiles.keys())):
        loc = list(myMap.tiles.keys())[i]
        near = myMap.getNearTiles(loc,True)
        score = 0
        for tile in near:
            if tile is not None:
                if myMap.river.get(tile.location) is not None:
                    score = 4
                    break
                else:
                    nearOfNear = myMap.getNearTiles(tile.location)
                    for i in nearOfNear:
                        if myMap.river.get(i) is not None:
                            score = 2
                            break
                        if i is not None:
                            if myMap.tiles[i].tileType == Coast:
                                score = 2
                                break
        analyze["담수"][loc] = score
    print(f"담수 분석 완료...(8/{maxWorkNum})")
    print(f"교통 분석 시작...(9/{maxWorkNum})")
    for i in range(len(myMap.tiles.keys())):
        loc = list(myMap.tiles.keys())[i]
        tile = myMap.tiles[loc]
        score = 0
        if str(tile.tileType()) == "산":
            score = 6
        if str(tile.tileType()) in ["사막-언덕","초원-언덕","평원-언덕","숲","평원-열대우림","오아시스","산호초"]:
            if myMap.river.get(tile.location) is not None:
                score += 2
        analyze["교통"][loc] = score
    print(f"교통 분석 완료...(9/{maxWorkNum})")
    print(f"최종 분석 시작...(10/{maxWorkNum})")
    for i in range(len(myMap.tiles.keys())):
        if True:#myMap.tiles[loc].tileType in [Desert, Forest, Jungle, Plains, Glassland, PlainsHill, GlasslandHill, DesertHill]:
            loc = list(myMap.tiles.keys())[i]
            score = [0,0,0,0,0]
            level_1 = myMap.getNearTiles(loc)
            level_2 = myMap.getFarTiles(loc,2)
            level_3 = myMap.getFarTiles(loc,3)
            level_4 = myMap.getFarTiles(loc,4)
            level_5 = myMap.getFarTiles(loc,5)
            bias = {
                "산출량" : 1,
                "캠퍼스" : 1,
                "성지" : 1,
                "시설" : 9,
                "항만" : 1,
                "상업중심지" : 1,
                "극장가" : 1,
                "산업구역" : 1,
                "담수" : 1,
                "자원" : 1,
                "교통" : -1
            }
            for i in level_1:
                if not None in list(map(lambda x : analyze[x].get(i),analyze.keys())):
                    analyzeTarget = dict(map(lambda x : (x, analyze[x].get(i)),analyze.keys()))
                    layer = analyzeTarget["산출량"] * bias["산출량"] + analyzeTarget["캠퍼스"] * bias["캠퍼스"] + analyzeTarget["성지"] * bias["성지"] + analyzeTarget["시설"] * bias["시설"] + analyzeTarget["항만"] * bias["항만"] + analyzeTarget["상업중심지"] * bias["상업중심지"] + analyzeTarget["극장가"] * bias["극장가"] + analyzeTarget["산업구역"] * bias["산업구역"] + analyzeTarget["담수"] * bias["담수"] + analyzeTarget["자원"] * bias["자원"] + analyzeTarget["교통"] * bias["교통"]
                    score[0] += layer * 25
            for i in level_2:
                if not None in list(map(lambda x : analyze[x].get(i),analyze.keys())):
                    analyzeTarget = dict(map(lambda x : (x, analyze[x].get(i)),analyze.keys()))
                    layer = analyzeTarget["산출량"] * bias["산출량"] + analyzeTarget["캠퍼스"] * bias["캠퍼스"] + analyzeTarget["성지"] * bias["성지"] + analyzeTarget["시설"] * bias["시설"] + analyzeTarget["항만"] * bias["항만"] + analyzeTarget["상업중심지"] * bias["상업중심지"] + analyzeTarget["극장가"] * bias["극장가"] + analyzeTarget["산업구역"] * bias["산업구역"] + analyzeTarget["담수"] * bias["담수"] + analyzeTarget["자원"] * bias["자원"] + analyzeTarget["교통"] * bias["교통"]
                    score[1] += layer * 16
            for i in level_3:
                if not None in list(map(lambda x : analyze[x].get(i),analyze.keys())):
                    analyzeTarget = dict(map(lambda x : (x, analyze[x].get(i)),analyze.keys()))
                    layer = analyzeTarget["산출량"] * bias["산출량"] + analyzeTarget["캠퍼스"] * bias["캠퍼스"] + analyzeTarget["성지"] * bias["성지"] + analyzeTarget["시설"] * bias["시설"] + analyzeTarget["항만"] * bias["항만"] + analyzeTarget["상업중심지"] * bias["상업중심지"] + analyzeTarget["극장가"] * bias["극장가"] + analyzeTarget["산업구역"] * bias["산업구역"] + analyzeTarget["담수"] * bias["담수"] + analyzeTarget["자원"] * bias["자원"] + analyzeTarget["교통"] * bias["교통"]
                    score[2] += layer * 9

            bias = {
                "산출량" : 0,
                "캠퍼스" : 1,
                "성지" : 1,
                "시설" : 1,
                "항만" : 1,
                "상업중심지" : 1,
                "극장가" : 1,
                "산업구역" : 1,
                "담수" : 1,
                "자원" : 1,
                "교통" : -1
            }

            for i in level_4:
                if not None in list(map(lambda x : analyze[x].get(i),analyze.keys())):
                    analyzeTarget = dict(map(lambda x : (x, analyze[x].get(i)),analyze.keys()))
                    layer = analyzeTarget["산출량"] * bias["산출량"] + analyzeTarget["캠퍼스"] * bias["캠퍼스"] + analyzeTarget["성지"] * bias["성지"] + analyzeTarget["시설"] * bias["시설"] + analyzeTarget["항만"] * bias["항만"] + analyzeTarget["상업중심지"] * bias["상업중심지"] + analyzeTarget["극장가"] * bias["극장가"] + analyzeTarget["산업구역"] * bias["산업구역"] + analyzeTarget["담수"] * bias["담수"] + analyzeTarget["자원"] * bias["자원"] + analyzeTarget["교통"] * bias["교통"]
                    score[3] += layer * 4

            for i in level_5:
                if not None in list(map(lambda x : analyze[x].get(i),analyze.keys())):
                    analyzeTarget = dict(map(lambda x : (x, analyze[x].get(i)),analyze.keys()))
                    layer = analyzeTarget["산출량"] * bias["산출량"] + analyzeTarget["캠퍼스"] * bias["캠퍼스"] + analyzeTarget["성지"] * bias["성지"] + analyzeTarget["시설"] * bias["시설"] + analyzeTarget["항만"] * bias["항만"] + analyzeTarget["상업중심지"] * bias["상업중심지"] + analyzeTarget["극장가"] * bias["극장가"] + analyzeTarget["산업구역"] * bias["산업구역"] + analyzeTarget["담수"] * bias["담수"] + analyzeTarget["자원"] * bias["자원"] + analyzeTarget["교통"] * bias["교통"]
                    score[4] += layer * 1
            tile = myMap.tiles[loc]
            score = sum(score)
            analyze["최종"][loc] = score
    print(f"최종 분석 완료...(10/{maxWorkNum})")
    result = sorted(analyze["최종"].items(),key = lambda x: x[1],reverse=True)
    def fill(surface, color):
        """Fill all pixels of the surface with color, preserve transparency."""
        w, h = surface.get_size()
        r, g, b, _ = color
        for x in range(w):
            for y in range(h):
                a = surface.get_at((x, y))[3]
                surface.set_at((x, y), pygame.Color(r, g, b, a))
    maxValue = result[0][1]
    minValue = result[-1][1]
    for i in range(len(result)):
        if filterAdapt :
            if round(255 * result[i][1]/maxValue) >= 0:
                fill(myMap.tiles[result[i][0]].img,(0,round(255 * result[i][1]/maxValue),0,0))
            else:
                fill(myMap.tiles[result[i][0]].img,(round(255 * result[i][1]/minValue),0,0,0))

    clock = pygame.time.Clock()
    while True:
        clock.tick(100)
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[pygame.K_UP]:
            camY -= 3
        if pressed_keys[pygame.K_DOWN]:
            camY += 3
        if pressed_keys[pygame.K_LEFT]:
            camX -= 3
        if pressed_keys[pygame.K_RIGHT]:
            camX += 3

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        screen.fill(WHITE)
        myMap.draw(screen)
        maxPos = list(result[0][0])
        x = maxPos[0]
        y = maxPos[1]
        maxPos[0] = x * 25
        maxPos[0] += SCREEN_WIDTH/2 - camX
        maxPos[1] -= y * 25 * c
        maxPos[1] -= x * 12.5 * c
        maxPos[1] += SCREEN_HEIGHT/2 - camY
        pygame.draw.circle(screen,RED,maxPos,10)
            #print(list(map(lambda x : myMap.tiles[x].tileType,myMap.tiles)))
        pygame.display.update()