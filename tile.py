import pygame,os,copy
IMAGE = {}
def setImage(image):
    global IMAGE
    IMAGE = image
BONUS_RESOURCE = 0
LUXURY_RESOURCE = 1
STRATEGY_RESOURCE = 2

class Resource:
    def __init__(self, type) -> None:
        self.type = type
    
class SeaResource(Resource):
    def __init__(self) -> None:
        super().__init__(LUXURY_RESOURCE)
        self.img = copy.copy(IMAGE["바다자원"])

class StrategyResource(Resource):
    def __init__(self) -> None:
        super().__init__(STRATEGY_RESOURCE)
        self.img = copy.copy(IMAGE["전략자원"])

class Stone(Resource):
    def __init__(self) -> None:
        super().__init__(BONUS_RESOURCE)
        self.img = copy.copy(IMAGE["석재"])

#==================================================

class TileType:
    def __init__(self, bread, hammer, gold, science, name, resource = None) -> None:
        self.bread = bread
        self.hammer = hammer
        self.gold = gold
        self.science = science
        self.resource = resource
        self.name = name
    
    def __repr__(self) -> str:
        return self.name
    def __str__(self) -> str:
        return self.name

class Glassland(TileType):
    def __init__(self) -> None:
        super().__init__(2, 0, 0, 0, "초원")
        self.img = copy.copy(IMAGE[self.name])

class Plains(TileType):
    def __init__(self) -> None:
        super().__init__(1, 1, 0, 0,"평원")
        self.img = copy.copy(IMAGE[self.name])

class Desert(TileType):
    def __init__(self) -> None:
        super().__init__(0, 0, 0, 0,"사막")
        self.img = copy.copy(IMAGE[self.name])

class Mountain(TileType):
    def __init__(self) -> None:
        super().__init__(0, 0, 0, 0,"산")
        self.img = copy.copy(IMAGE[self.name])

class Coast(TileType):
    def __init__(self) -> None:
        super().__init__(1, 0, 1, 0,"해안")
        self.img = copy.copy(IMAGE[self.name])

class Lake(TileType):
    def __init__(self) -> None:
        super().__init__(1, 0, 1, 0,"호수")
        self.img = copy.copy(IMAGE[self.name])

class Ocean(TileType):
    def __init__(self) -> None:
        super().__init__(1, 0, 0, 0,"해양")
        self.img = copy.copy(IMAGE[self.name])

#==================================================

class GlasslandHill(Glassland):
    def __init__(self) -> None:
        super().__init__()
        self.hammer += 1
        self.name = "초원-언덕"
        self.img = copy.copy(IMAGE[self.name])

class PlainsHill(Plains):
    def __init__(self) -> None:
        super().__init__()
        self.hammer += 1
        self.name = "평원-언덕"
        self.img = copy.copy(IMAGE[self.name])

class DesertHill(Desert):
    def __init__(self) -> None:
        super().__init__()
        self.hammer += 1
        self.name = "사막-언덕"
        self.img = copy.copy(IMAGE[self.name])

class GlasslandFlood(Glassland):
    def __init__(self) -> None:
        super().__init__()
        self.hammer += 1
        self.name = "초원-범람원"
        self.img = copy.copy(IMAGE[self.name])

class Oasis(Desert):
    def __init__(self) -> None:
        super().__init__()
        self.bread += 3
        self.gold += 1
        self.name = "오아시스"
        self.img = copy.copy(IMAGE[self.name])

class Forest(Glassland):
    def __init__(self) -> None:
        super().__init__()
        self.hammer += 1
        self.name = "숲"
        self.img = copy.copy(IMAGE[self.name])

class Jungle(Glassland):
    def __init__(self) -> None:
        super().__init__()
        self.bread += 1
        self.name = "평원-열대우림"
        self.img = copy.copy(IMAGE[self.name])

class Reef(Coast):
    def __init__(self) -> None:
        super().__init__()
        self.bread += 1
        self.hammer += 1
        self.name = "산호초"
        self.img = copy.copy(IMAGE[self.name])

class Tile:
    def __init__(self, tileId, tileType, const, location) -> None:
        self.tileId = tileId
        self.tileType = tileType
        self.bread = tileType().bread
        self.hammer = tileType().hammer
        self.science = tileType().science
        self.gold = tileType().gold
        self.const = const
        self.location = location
        self.img = tileType().img
        self.resource = None