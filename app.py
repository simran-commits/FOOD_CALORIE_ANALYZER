from flask import Flask, render_template, request
import json
import difflib
import os

app = Flask(__name__)


# ==========================================
# LOAD KAGGLE FOOD DATA
# ==========================================

DATA_FILE = os.path.join("data", "foods.json")

with open(DATA_FILE, "r", encoding="utf-8") as file:
    food_data = json.load(file)


# ==========================================
# MAKE SURE DATA IS A LIST
# ==========================================

if isinstance(food_data, dict):
    food_data = list(food_data.values())


# ==========================================
# GET FOOD NAME
# ==========================================

def get_food_name(food):

    possible_names = [
        "Dish Name",
        "Food Name",
        "food_name",
        "name",
        "Name",
        "Food"
    ]

    for key in possible_names:

        if key in food:

            value = food[key]

            if value is not None:
                return str(value).strip()

    return "Unknown Food"


# ==========================================
# GET NUTRITION VALUE
# ==========================================

def get_value(food, possible_keys):

    for key in possible_keys:

        if key in food:

            value = food[key]

            try:
                return float(value)

            except (ValueError, TypeError):
                return 0.0

    return 0.0


# ==========================================
# FIND FOOD
# ==========================================

def find_food(food_name):

    food_name = food_name.strip().lower()

    names = [
        get_food_name(food).lower()
        for food in food_data
    ]

    # Exact match
    for index, name in enumerate(names):

        if name == food_name:

            return food_data[index], False


    # Partial match
    for index, name in enumerate(names):

        if food_name in name:

            return food_data[index], True


    # Closest match
    matches = difflib.get_close_matches(
        food_name,
        names,
        n=1,
        cutoff=0.45
    )

    if matches:

        matched_name = matches[0]

        index = names.index(matched_name)

        return food_data[index], True


    return None, False


# ==========================================
# CALCULATE NUTRITION
# ==========================================

def calculate_nutrition(food, quantity):

    # Dataset values are treated as values per 100g

    multiplier = quantity / 100


    calories = get_value(
        food,
        [
            "Calories (kcal)",
            "Calories",
            "calories",
            "Calorie"
        ]
    )


    protein = get_value(
        food,
        [
            "Protein (g)",
            "Protein",
            "protein"
        ]
    )


    carbs = get_value(
        food,
        [
            "Carbohydrates (g)",
            "Carbohydrates",
            "carbs",
            "Carbs",
            "carbohydrates"
        ]
    )


    fat = get_value(
        food,
        [
            "Fats (g)",
            "Fat (g)",
            "Fat",
            "fat",
            "Fats"
        ]
    )


    return {

        "calories": round(
            calories * multiplier,
            2
        ),

        "protein": round(
            protein * multiplier,
            2
        ),

        "carbs": round(
            carbs * multiplier,
            2
        ),

        "fat": round(
            fat * multiplier,
            2
        )

    }


# ==========================================
# HOME
# ==========================================

@app.route("/", methods=["GET", "POST"])
def index():

    result = None
    message = None


    if request.method == "POST":

        food_name = request.form.get(
            "food_name",
            ""
        ).strip()


        quantity_text = request.form.get(
            "quantity",
            "100"
        )


        # ------------------------------
        # CHECK QUANTITY
        # ------------------------------

        try:

            quantity = float(quantity_text)

            if quantity <= 0:
                raise ValueError

        except (ValueError, TypeError):

            message = "Please enter a valid quantity."

            return render_template(
                "index.html",
                result=None,
                message=message
            )


        # ------------------------------
        # CHECK FOOD NAME
        # ------------------------------

        if not food_name:

            message = "Please enter a food name."


        else:

            food, is_closest = find_food(
                food_name
            )


            # ------------------------------
            # FOOD FOUND
            # ------------------------------

            if food:

                nutrition = calculate_nutrition(
                    food,
                    quantity
                )


                result = {

                    "name": get_food_name(food),

                    "quantity": quantity,

                    "calories": nutrition["calories"],

                    "protein": nutrition["protein"],

                    "carbs": nutrition["carbs"],

                    "fat": nutrition["fat"]

                }


                # Closest match message

                if is_closest:

                    message = (
                        "No exact match was found. "
                        "Showing the closest food from the database."
                    )


            # ------------------------------
            # FOOD NOT FOUND
            # ------------------------------

            else:

                message = (
                    "Food item not found in the database. "
                    "Please try another food name."
                )


    return render_template(
        "index.html",
        result=result,
        message=message
    )


# ==========================================
# IMAGE ANALYSIS
# ==========================================

@app.route(
    "/analyse-image",
    methods=["POST"]
)
def analyse_image():

    image = request.files.get(
        "food_image"
    )


    if not image or image.filename == "":

        return render_template(
            "index.html",
            result=None,
            message="Please select a food image."
        )


    # Image AI/API will be connected later.
    # For now, show a proper English message.

    return render_template(
        "index.html",
        result=None,
        message=(
            "Image uploaded successfully. "
            "AI food recognition will be connected in the next step."
        )
    )


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=True
    )