import pandas as pd
import json

df = pd.read_csv("data/foods.csv")

df = df.fillna("")

data = df.to_dict(orient="records")

with open("data/foods.json", "w", encoding="utf-8") as file:
    json.dump(data, file, indent=4, ensure_ascii=False)

print("CSV successfully converted to JSON!")
print(f"Total food items: {len(data)}")