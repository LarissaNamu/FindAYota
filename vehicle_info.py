import json


class Traits:
    def __init__(self, engine_type, drive_train, seats, body, color):
        self.engine_type = engine_type
        self.drive_train = drive_train
        self.seats = seats
        self.body = body
        self.color = color

    def __str__(self):
        return (f"Engine Type: {self.engine_type}\n"
                f"Drive Train: {self.drive_train}\n"
                f"Seats: {self.seats}\n"
                f"Body: {self.body}"
                f"Color: {self.color}")

class Vehicle:
    def __init__(self, id, model, price, traits, mpg):
        self.id = id
        self.model = model
        self.price = price
        self.traits = traits
        self.mpg = mpg

    def __str__(self):
        return (f"Vehicle: {self.id} {self.model}\n"
                f"Price: ${self.price:,.2f}\n"
                f"{self.traits}"
                f"{self.mpg}")

    @staticmethod
    def from_json(json_file):
        #create a list of vehicle object from the json file
        with open(json_file, 'r') as file:
            data = json.load(file)

        vehicles = []
        for entry in data:
            id = entry.get('id')
            model = entry.get('model')
            price = entry.get('price')
            mpg = entry.get('mpg')

            # extract traits from the json file
            traits_data = entry.get('traits', {})
            traits = Traits(
                engine_type = traits_data.get('engine_type'),
                drive_train = traits_data.get('drive_train'),
                seats = traits_data.get('seats'),
                body = traits_data.get('body'),
                color = traits_data.get('color')
            )

            # create a new object for the vehicle
            vehicles.append(Vehicle(id, model, price, traits))

        return vehicles