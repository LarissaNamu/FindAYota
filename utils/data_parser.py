from vehicle_info import Vehicle

def parse_vehicles(car_data):
    car_list = []
    for c in car_data:
        #print(type(c["model"]))
        temp_car = Vehicle(c['id'],c['model'].lower().strip(),c['price'],c['body_style'],c['drivetrain'], c['mpg'], c['engine'], c["image_path"])
        #print(temp_car.get_model())
        car_list.append(temp_car)

    #print(car_list)
    return car_list