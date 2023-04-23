import math

# Functions
def calculate_angle(coordinates1: tuple, coordinates2: tuple) -> float:
    '''
    Calculates the angle between two points in degrees.
    '''
    x1, y1 = coordinates1
    x2, y2 = coordinates2
    try:
        angle = math.atan((y2 - y1) / (x2 - x1))
    except:
        angle = 0

    rotation = 360 - math.degrees(angle)
    return rotation