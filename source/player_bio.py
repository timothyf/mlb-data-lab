
class PlayerBio:
    def __init__(self, name, age, height, weight, pitcher_hand, position):
        self.name = name
        self.age = age
        self.height = height
        self.weight = weight
        self.position = position
        self.pitcher_hand = pitcher_hand

    def get_name(self):
        return self.name

    def get_age(self):
        return self.age

    def get_height(self):
        return self.height

    def get_weight(self):
        return self.weight

    def get_position(self):
        return self.position

    def get_bio(self):
        return f"{self.name} is {self.age} years old, {self.height} tall, {self.weight} lbs, and plays {self.position}."
