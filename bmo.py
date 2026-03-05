import json
import pdfplumber
import re

all_assignments = [
    {"name": "Essay", "grade_weight": 40, "due_date": "January 5", "completed": False},
    {"name": "Project", "grade_weight": 30, "due_date": "January 10", "completed": False},
    {"name": "Midterm", "grade_weight": 75, "due_date": "January 16", "completed": False},
    {"name": "Group Project", "grade_weight": 20, "due_date": "January 30", "completed": False},
    {"name": "Final Exam", "grade_weight": 100, "due_date": "February 17", "completed": False},
]


def display_assignments(all_assignments):
    for assignment in all_assignments:
        print("You have,", assignment["name"],"which is worth", assignment["grade_weight"], "points, due on", assignment["due_date"] )

def find_heaviest(all_assignments):
    heaviest = all_assignments[0]
    for assignment in all_assignments:
        if assignment["grade_weight"] > heaviest["grade_weight"]:
            heaviest = assignment
    return heaviest
    
def save_assignments(all_assignments):
    with open("assignments.json", "w") as file:
        json.dump(all_assignments, file)

def extract_text(filename):
    with open(filename, "r") as file:
        text = file.read()
        return text

def find_grade_weights(text):
    return re.findall(r"\d+%", text)

   



display_assignments(all_assignments)
result = find_heaviest(all_assignments)
save_assignments(all_assignments)
print("BMO Warning:", result["name"], "is your heaviest assignment at", result["grade_weight"], "points")
extract_text("CMSC131syllabus.pdf")

text = extract_text("CMSC131syllabus.pdf")
weights = find_grade_weights(text)
print(weights)