import google.genai as genai
import json
import os
import pdfplumber
import datetime
from dotenv import load_dotenv
load_dotenv()


#in order to priorotize assignments later on I need an algorithm to find the most valuable assignment that students need to prepare for.
def find_heaviest(all_assignments):
    heaviest = all_assignments[0]
    for assignment in all_assignments:
        if assignment["grade_weight"] > heaviest["grade_weight"]:
            heaviest = assignment
    return heaviest
    
#Keeping a memory of the files so that it can 
def save_assignments(all_assignments):
    with open("assignments.json", "w") as file:
        json.dump(all_assignments, file)

#Extracting text from each page of the pdf so Gemini can more accurately 
def extract_text(filename):
    text = ""
    with pdfplumber.open(filename) as pdf:
        for page in pdf.pages:
            text = text + page.extract_text()
    return text

def student_choice():
    while True:
        choice = int(input("what would you like to do? Please select an option by number." \
    "\n1. Upload a syllabus"
    "\n2. Manually Add an assignment" \
    "\n3. View Assignments" \
    "\n4. Quit \n"))
        if choice == 1:
            filename = input("Upload Your Syllabus or course schedule")
            text = extract_text(filename)
            result = gemini(text)
            assignment_list = json.loads(result)
            save_assignments(assignment_list)
        elif choice == 2:
            new_assignment = userinput()
            assignment_list = load_assignments()
            assignment_list.append(json.loads(new_assignment))
            save_assignments(assignment_list)
        elif choice == 3:
            all_assignments = load_assignments()
            print(all_assignments)
        elif choice == 4:
            break
        else:
            print("Thats not an option, please select one of 3 options by number."\
            "\n1. Upload a syllabus"\
            "\n2. Manually Add an assignment" \
            "\n3. View Assignments"\
            "\n4. Quit \n")
            


def userinput():
    student_message = input("Good evening, any assignment updates? ")
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    prompt = """You are a student assistant for a productivity app. A student will give you one sentence about an assignment. Extract the structured data and return a single JSON dictionary in exactly this format:
{"name": "Essay", "grade_weight": null, "due_date": "March 5", "completed": false}

Rules:
- name is the assignment name. Infer it from context if not explicitly stated
- grade_weight is an integer percentage if mentioned, otherwise null
- due_date must be in MM/DD/YYYY format. If the student says something like "this friday" or "march 23" convert it to MM/DD/YYYY. If no date is mentioned write null
- completed is always false
- Return only the raw JSON dictionary, no explanation, no markdown, no code blocks"""
    contents = prompt + "\n\nSTUDENT MESSAGE:\n" + student_message
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents
    )
    return response.text

def gemini(text):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    prompt = """You are a syllabus parser for a student productivity app. Your job is to extract every gradeable item from the syllabus provided, even if the information is incomplete.

Return a JSON list of dictionaries in exactly this format:
[{"name": "Essay", "grade_weight": 40, "due_date": "January 5", "completed": false}]

Rules:
- Extract every assignment, exam, project, quiz, or gradeable category you find
- grade_weight must be an integer representing percentage. If you find 32% write 32
- If a due date exists convert it to MM/DD/YYYY format. If no due date is found write null
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


def load_assignments():
    try:
        with open("assignments.json", "r") as file:
            all_assignments = json.load(file)
            return all_assignments
    except FileNotFoundError:
        return []

def priority_score(assignment):
    grade_weight = assignment["grade_weight"]
    due_date = assignment["due_date"]
    

student_choice()