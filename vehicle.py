import math

class Vehicle:
    next_id = 0
    
    def __init__(self, x, y, vehicle_type):
        self.id = Vehicle.next_id
        Vehicle.next_id += 1
        self.position = [x, y]
        self.vehicle_type = vehicle_type

    def check_position(self, x_new, y_new):
        return (x_new - self.position[0]), (abs(x_new - self.position[0]) + abs(y_new - self.position[1]))

    def is_near(self, x, y, threshold=50):
        """
        Check if the new position (x, y) is within a certain threshold distance from the current position.
        """
        distance = math.sqrt((x - self.position[0]) ** 2 + (y - self.position[1]) ** 2)
        return distance < threshold

    def toString(self):
        print(f"Hello my name is {self.vehicle_type} at position {self.position}")
