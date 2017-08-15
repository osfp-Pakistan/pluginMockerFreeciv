
size = 5
mapSelector = ['map_t', 'map_b00_', 'map_r00_', 'map_spe00_', 'map_spe01_', 'map_res', 'map_owner', 'map_worked']

aragoKeys = {'a': 'terrain_inaccesible',
    'c': 'terrain_ocean',
    'b': 'terrain_lake',
    'e': 'terrain_glacier',
    'd': 'terrain_deep_ocean',
    'g': 'terrain_forest',
    'f': 'terrain_desert',
    'i': 'terrain_hills',
    'h': 'terrain_grassland',
    'k': 'terrain_mountains',
    'j': 'terrain_jungle',
    'm': 'terrain_swamp',
    'l': 'terrain_plains',
    'n': 'terrain_tundra'}
    
def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]
    
class Block:
    def __init__(self):
        self.innerHash = {}
        
    def draw_mask(self, mask='map_t'):
        for l in self.innerHash[mask]:
            s = ""
            for t in l:
                s += t + " "
            print(s)
        
    def set_mask(self, k, s):
        self.innerHash[k] = list(chunks(s.split(','), size))
    
    def get_tile(self, x, y, mask='map_t'):
        return self.innerHash[mask][x][y]


def can_be_irrigated(tile):
    return tile in ['f', 'h', 'i', 'l', 'n']

def is_under_city(did):
    return did != '-'

def is_water_supply(tile):
    return tile in ['d', 'c']

def has_river(tile):
    if tile == ".":
        return False
    return int(tile) in [4, 5, 7]

def is_irrigated(tile):
    if tile == ".":
        return False
    return int(tile) % 2 == 1

##Interface functions

def name():
    return "scoreIrrogation"

def ogit_type():
    return "Tile"

def window_slice_size():
    return (size, size)

def needed_maps():
    return mapSelector

def needed_rulesets():
    return []

def needs_game():
    return True

def calculate( ** kwargs):
    actScore = 1.0
    mapHash = {}
    
    for k, v in zip(mapSelector, kwargs['maps']):
        mapHash[k] = v
    
    b = Block()
    [b.set_mask(k, mapHash[k]) for k in mapSelector]
    c = (size // 2)
    center = b.get_tile(c, c)
    
    cOwn = b.get_tile(c, c, mask='map_owner')
    if cOwn != "0":
        return 0.0 #we don own this city
    
    if not can_be_irrigated(center):
        return 0.0 #Can't be irrigated
    
    if is_under_city('-'):
        #MOCK!!!!
        return 0.0 #Don't irrigate cities
    
    cIrri = b.get_tile(c, c, mask='map_spe00_')
    if int(cIrri) % 2 == 1:
        return 0.0 # already irrigated
    
    cRoad = b.get_tile(c, c, mask='map_r00_')
    if int(cRoad) in [4, 7]:
        return 0.0 #Rivers are ignored !?
    
    #Check water supply
    
    hasWater = False
    
    for i in [-1, 1]:
        hasWater |= is_water_supply(b.get_tile(c + i, c, mask='map_t'))
        hasWater |= is_water_supply(b.get_tile(c, c + i, mask='map_t'))
        hasWater |= has_river(b.get_tile(c + i, c, mask='map_r00_')) 
        hasWater |= has_river(b.get_tile(c, c + i, mask='map_r00_'))
        hasWater |= is_irrigated(b.get_tile(c + i, c, mask='map_spe00_'))
        hasWater |= is_irrigated(b.get_tile(c, c + i, mask='map_spe00_'))
        
    
    if not hasWater:
        return 0.0 # no water next
    
    # From now on irrogation is possible
    
    #Ressources to be preffered
    cRes = b.get_tile(c, c, mask='map_res')
    if cRes == ".":
        actScore *= 0.8
        
    cWork = b.get_tile(c, c, mask='map_worked')
    if cWork == "-":
        actScore *= 0.5
        
    return actScore
