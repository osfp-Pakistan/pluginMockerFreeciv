import json

def name():
    return "tileGoodness"

def ogit_type():
    return "Tile"

def window_slice_size():
    return (5, 5)

def needed_maps():
    return ['map_t', 'map_res','map_spe00_','map_worked']

def needed_rulesets():
    return ['terrain']

def needs_game():
    return True

def calculate(**kwargs):
    result = 1
    return result
