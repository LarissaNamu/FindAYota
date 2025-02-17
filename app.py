from flask import Flask, render_template, request, jsonify
import json
from finance import Finance
from utils.data_parser import parse_vehicles
from vehicle_info import Vehicle

app = Flask(__name__)

# make a function that instantiates a hashmap from json file
# { "corolla" : point }
def create_map():
    vehicle_point_map = {}
    with open("data/vehicles.json") as v:
        car_info = json.load(v)
    car_real_info = car_info.get("vehicles", [])
    # print(car_real_info)
    car_list = parse_vehicles(car_real_info)  # list of cars
    
    
    # Standardize the car model names to lowercase and strip any extra spaces
    for car in car_list:
        model_name = car.get_model().lower().strip()  # normalize the model name
        vehicle_point_map.update({model_name: 0})
    # print(vehicle_point_map)
    return vehicle_point_map

# with open("data/vehicles.json") as v:
#         car_info = json.load(v)
#         car_real_info = car_info.get("vehicles", [])
# # print(car_real_info)
# car_list = parse_vehicles(car_real_info)

def create_car_list():
    with open("data/vehicles.json") as d:
        vehicles = json.load(d)
        car_real_info = vehicles.get("vehicles", [])

    car_list = parse_vehicles(car_real_info)
    return car_list


# Create the global vehicle_point_map variable


traits_to_ask = ["body_style", "drivetrain", "engine"]

@app.route("/")
def home():
    return render_template("home.html", title="FindAYota - Home")

@app.route("/finance/<int:car_id>", methods=["GET", "POST"])
def finance(car_id):
    car_list = create_car_list()
    car = next((car for car in car_list if car.id == car_id), None)

    if request.method == "POST":
        data = request.get_json()
        cash_down = int(data.get("cash_down", 0))
        credit_score = int(data.get("credit_score", 300))
        trade_in = float(data.get("trade_in", 0))
        loan_term = int(data.get("loan_term", 24))

        finance = Finance(
            credit_score=credit_score,
            down_payment=cash_down,
            loan_term=loan_term,
            trade_in=trade_in,
            vehicle_price=car.price
        )

        apr = finance.calc_apr()
        monthly_payment = finance.monthly_pay(apr)

        return jsonify({
            'monthly_payment': monthly_payment,
            'apr': apr
        })

    return render_template("finance.html", car=car)

@app.route("/catalog")
def catalog():
    with open("data/vehicles.json") as d:
            vehicles = json.load(d)
            car_real_info = vehicles.get("vehicles", [])
    car_list = parse_vehicles(car_real_info)

    return render_template("catalog.html", cars=car_list)

    
    
@app.route("/form", methods=["GET", "POST"])
def form():
    global vehicle_point_map  # Declare vehicle_point_map as global to modify it
   
    if request.method == "POST":  # user clicks submit
        user_data = request.form.to_dict()  # Collect user data
        
        vehicle_point_map = create_map()
        # Load data from the JSON file
        with open("data/vehicles.json") as d:
            vehicles = json.load(d)
            car_real_info = vehicles.get("vehicles", [])
        car_list = parse_vehicles(car_real_info)
        # print("CARLIST")
        # print(car_list)
        # Compute points (this will update the global vehicle_point_map)
        vehicle_point_map = compute_points(user_data, vehicle_point_map, car_list)  # dict with computed points for each model

        # Get top-matched cars
        top_cars = get_top_percents(vehicle_point_map)
        print(top_cars)
        car_mapping = {car.get_model().lower(): car for car in car_list}
        matched_cars = [
            (car_mapping[car_name.lower()], percentage)
            for car_name, percentage in top_cars.items()
            if car_name.lower() in car_mapping
        ]

        return render_template("results.html", matches=matched_cars, cars=car_list)

    return render_template("form.html", traits=traits_to_ask)  # will be an array


# code in compute vehicle points function here
# hierarchy
# Engine -> Body -> DriveTrain -> MPG
# 50 -> 25 -> 10 -> 5
def compute_points(u_data, v_map, cars):
    # print("THE CARS")
    # print(cars) -- 'vehicles' big list
    hierarchy = {
        "engine": 30,
        "body_style": 90,
        "drivetrain": 10
    } #SUV FWD Hybrid

    for v_name, current_pts in v_map.items():
        # Normalize the car name to lowercase to avoid KeyError
        v_name_normalized = v_name.lower().strip()  # Normalize to lower case and strip spaces
        # if v_name_normalized not in cars:
        #     print(f"Warning: {v_name_normalized} not found in cars")
        #     continue
        vehicle = None
        for ca in cars:
            if ca.get_model().lower().strip() == v_name_normalized:
                vehicle = ca
                break
        # vehicle_traits = cars[v_name_normalized]  # Get the vehicle traits using the normalized name

        for trait, pts in hierarchy.items():
            if trait in u_data:
                user_val = u_data[trait]
                vehicle_val = getattr(vehicle,trait,None)
                # print("AHAHAHAH")
                # print(vehicle_val)

                if isinstance(vehicle_val, list):
                    if user_val.lower().strip() in [val.lower().strip() for val in vehicle_val]:
                        v_map[v_name] += pts
                elif vehicle_val and vehicle_val.lower().strip() == user_val.lower().strip():
                    v_map[v_name] += pts
                # if vehicle_val and vehicle_val.lower().strip() == user_val.lower().strip():
                    
                #     v_map[v_name] += pts

    # print(v_map)
    return v_map

# {
# Corolla : 90
# Cross: 5
# RAV4 : 5
# }

def get_top_percents(v_map):  # return dictionary with top 3 cars and their percentage
    # Sort cars by points in descending order
    sort_cars = sorted(v_map.items(), key=lambda x: x[1], reverse=True)
    
    # Take the top 3 cars, or fewer if there are less than 3
    top_3 = sort_cars[:3]
    
    # Sum the points of the top 3 cars
    sum_top_3 = sum(points for c, points in top_3)
    # print(top_3)
    # print(sum_top_3)
    # Prevent division by zero if there are no points
    if sum_top_3 == 0:
        top_3 = [("Corolla Sedan",0), ("RAV4 Hybrid",0), ("Tacoma",0)]
        top_3_map = {
        car: round((points / 1) * 100, 2)
        for car, points in top_3
        }
    else:
        # Calculate the percentage for each car in the top 3
        top_3_map = {
            car: round((points / sum_top_3) * 100, 2)
            for car, points in top_3
        }
    
    

    return top_3_map

if __name__ == "__main__":
    app.run(debug=True)