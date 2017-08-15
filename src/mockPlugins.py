import glob
import random
import re
import os
import sys


input = []
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

mapToArago = {'a':'e',
    'd':'f',
    'f':'g',
    'p':'l',
    'g':'h',
    ':':'d',
    'h':'i',
    'j':'j',
    '+':'b',
    'm':'k',
    ' ':'c',
    's':'m',
    't':'n',
    '.':'.'}
    
class Tile:
    
    def can_be_irrigated(self):
        if self.aragoTile in ['e', 'd', 'g', 'j', 'b', 'k', 'c', 'm']:
            return False
        return True
    
    def set_mask(self, k, v):
        self.mask[k] = v

    def get_mask(self, k):
        if k not in self.mask:
            return "."
        return self.mask[k]
        
    def __init__(self, baseTile):
        self.baseTile = baseTile
        self.aragoTile = mapToArago[baseTile]
        self.mask = {}
#        self.irrigated = "0"
#        self.ressource = ' '
#        if (self.can_be_irrigated()):
#            if (random.randint(0, 100) < 20):
#                self.irrigated = "1"
#                
    
    
    def _get_char(self):
        return self.baseTile

    def _get_arago_char(self):
        return self.aragoTile

class NullTile(Tile):
    def __init__(self):
        Tile.__init__(self, '.')
        
class Line:
    def __init__(self, tileLine):
        self.cContainer = []
        for t in tileLine:
            self.append_tile(Tile(t))
        
    def append_mask(self, maskname, maskline):
        for k, v in zip(self.cContainer, maskline):
            k.set_mask(maskname, v)
    
    def append_tile(self, newtile):
        self.cContainer.append(newtile)
        
    def get_slice(self, start, length):
        helpcontainer = []
        start = int(start)
        tail = []
        while (start < 0):
            helpcontainer.append(NullTile())
            start += 1
            length -= 1
        while (start + length > len(self.cContainer)):
            tail.append(NullTile())
            length -= 1
        return helpcontainer + self.cContainer[start:start + length] + tail
        
    def length(self):
        return len(self.cContainer)
        
    def _get_char(self, y):
        return self.cContainer[y]._get_char()
    
class NullLine(Line):
    def __init__(self, length):
        Line.__init__(self, "." * length)

    
class Block:
    def __init__(self, x, y, size):
        self.lines = list(range(size))
        offset = (size -1) / 2
        for i in range(size):
            useLine = NullLine(input[0].length())
            ui = int(x + i -offset)
            if ((ui >= 0) and (ui < len(input))):
                useLine = input[ui]
            self.lines[i] = useLine.get_slice(y-offset, size)

    
    def get_center_block(self):
        p = int((len(self.lines) -1) / 2)
        return self.lines[p][p]

    def get_line(self, maps_needed):
        fullstring = ""       
        mapC = []
        for m in maps_needed:
            mStr = ""
            for l in self.lines:
                for o in list(l):
                    fullstring += o.get_mask(m)+","
                    mStr += o.get_mask(m)+","
            mapC.append(mStr[:-1])
        return (fullstring[:-1],mapC)

def convert_map(coreData):
    mapM = []
    for s in zip(*coreData.values()):
        for k, v in zip(coreData.keys(), s):
            if (k == "map_t"):
                myLine = Line(v)
                mapM.append(myLine)
            
            myLine.append_mask(k, v)
    return mapM
  
  
def generate_new_block(x, y, tileSize): 
    return Block(x, y, tileSize)
     
def generate_dataset(tileSize):
    container = []
    i = 0
    for k in input:
        for l in range(k.length()):
            container.append(generate_new_block(i, l, tileSize))
        i += 1 
    return container




def read_data(fname):
    sData = {}
    with open(fname, "r") as f:
        str = f.read()
    f.close()
    cpSlice = False;
    for k in str.split("\n"):
        if cpSlice:
            if (not k.startswith("label")):
                m = re.search('(.*_)(\d*)=\"(.*)\"', k)
                if (m != None):
                    id = "map_" + m.group(1)
                    if id not in sData:
                        sData[id] = []
                    sData[id].append(m.group(3))
                else:
                    m = re.search('(\D*)(\d*)=\"(.*)\"', k)
                    if (m != None):
                        id = "map_" + m.group(1)
                        if id not in sData:
                            sData[id] = []
                        sData[id].append(m.group(3))
            
        if (k == "[map]"):
            cpSlice = True
        if (k == "[players]"):
            cpSlice = False
    return sData
# Read map / save
print("Load sources...")
sys.path.insert(0, os.path.abspath(r'plugins'))
for fname in glob.iglob('data/*'):
    print("Use: " + fname)
    coreData = read_data(fname)
    input = convert_map(coreData)
    for pname in glob.iglob('plugins/*.py'):
        print("   on: " + os.path.basename(pname))
        cPar = {}
        modName = os.path.splitext(os.path.basename(pname))[0]
        aktMod = __import__(modName)
        size = 3
        if (hasattr(aktMod, 'window_slice_size')):
            size = aktMod.window_slice_size()[0] #quad only!
        wantedSet = coreData.keys()
        if (hasattr(aktMod, 'needed_maps')):
            wantedSet = aktMod.needed_maps()
            
        res = generate_dataset(size)
        #Apply data now
        storeName = os.path.basename(fname)+"_"+modName+"_full.csv"
        f = open(storeName,"w")
        for u in res:
            full,cPar["maps"] = u.get_line(wantedSet)
            answer = aktMod.calculate(**cPar)
            f.write(full+","+str(answer)+"\n")
        f.close()
        

print("done")