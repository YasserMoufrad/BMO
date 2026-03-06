import google.genai as genai
import json
import os
from dotenv import load_dotenv
load_dotenv()


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

def gemini(text):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    prompt = """You are a syllabus parser for a student productivity app. Your job is to extract every gradeable item from the syllabus provided, even if the information is incomplete.

Return a JSON list of dictionaries in exactly this format:
[{"name": "Essay", "grade_weight": 40, "due_date": "January 5", "completed": false}]

Rules:
- Extract every assignment, exam, project, quiz, or gradeable category you find
- grade_weight must be an integer representing percentage. If you find 32% write 32
- If a due date exists write it exactly as it appears. If no due date is found write null
- If a grade weight exists write it as an integer. If no grade weight is found write null
- completed is always false
- If you find a category like Projects worth 32% with no specific due date, still include it with null for due_date
- Make reasonable inferences about assignment names from context but flag nothing — just include everything you find
- Return only the raw JSON list, nothing else
- No explanation, no markdown, no code blocks, no extra text before or after the JSON"""
    contents = prompt + "\n\nSYLLABUS TEXT:\n" + text
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents
    )
    print(response.text)
    return response.text
    





text = extract_text("CMSC131syllabus.pdf")
result = gemini(text)
assignments_from_syllabus = json.loads(result)
print(assignments_from_syllabus)