from game_defines import DIRECTIONS

def get_next_move(path, debug = False):
    pos_x = path[0][0]
    pos_y = path[0][1]

    next_x = pos_x
    next_y = pos_y

    if len(path) > 1:
        next_x = path[1][0]
        next_y = path[1][1]

    if pos_x < next_x and pos_y < next_y:
        if debug: print "Down Right"
        return DIRECTIONS.DOWNRIGHT

    if pos_x < next_x and pos_y > next_y:
        if debug: print "Up Right"
        return DIRECTIONS.UPRIGHT

    if pos_x < next_x:
        if debug: print "Right"
        return DIRECTIONS.RIGHT

    if pos_x > next_x and pos_y < next_y:
        if debug: print "Down Left"
        return DIRECTIONS.DOWNLEFT

    if pos_x > next_x and pos_y > next_y:
        if debug: print "Up Left"
        return DIRECTIONS.UPLEFT

    if pos_x > next_x:
        if debug: print "LEFT"
        return DIRECTIONS.LEFT

    if pos_y < next_y:
        if debug: print "DOWN"
        return DIRECTIONS.DOWN

    if pos_y > next_y:
        if debug: print "UP"
        return DIRECTIONS.UP

    if debug: print "NO Move"
    return DIRECTIONS.NOMOVE


class Path(object):

    def __init__(self):
        pass

    def update(self, target_x, target_y):
        raise AssertionError("Sub class should override this!")
