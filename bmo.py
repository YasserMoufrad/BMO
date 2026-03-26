from datetime import datetime
import google.genai as genai
import json
import os
import pdfplumber
from dotenv import load_dotenv

load_dotenv()


# ── File I/O ──────────────────────────────────────────────────────────────────

def load_assignments():
    """Load assignments from disk. Returns empty list if no file exists yet."""
    try:
        with open("assignments.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_assignments(all_assignments):
    """Persist the full assignments list to disk."""
    with open("assignments.json", "w") as file:
        json.dump(all_assignments, file)


# ── PDF Parsing ───────────────────────────────────────────────────────────────

def extract_text(filename):
    """Extract raw text from every page of a PDF."""
    text = ""
    with pdfplumber.open(filename) as pdf:
        for page in pdf.pages:
            text = text + page.extract_text()
    return text


# ── Gemini API ────────────────────────────────────────────────────────────────

today = datetime.today().strftime("%m/%d/%Y")
def gemini(text):
    """Send syllabus text to Gemini and return a JSON list of assignments."""
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    prompt = f"""You are a syllabus parser for a student productivity app. Your job is to extract every gradeable item from the syllabus provided, even if the information is incomplete.

Return a JSON list of dictionaries in exactly this format:
[{{"name": "Essay", "grade_weight": 40, "due_date": "01/05/2026", "completed": false}}]

Rules:
- Extract every assignment, exam, project, quiz, or gradeable category you find
- grade_weight must be an integer representing percentage. If you find 32% write 32
- - due_date MUST be in MM/DD/YYYY format. Convert ALL dates to this format. Example: "March 18" becomes "03/18/2026". If no due date is found write null
- Today's date is {today}. Use this to convert relative dates like "this friday" or "next monday" to MM/DD/YYYY
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
    return response.text

def userinput():
    """Ask the student about an assignment in plain English and parse it with Gemini."""
    student_message = input("Good evening, any assignment updates? ")
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    prompt = """You are a student assistant for a productivity app. A student will give you one sentence about an assignment. Extract the structured data and return a single JSON dictionary in exactly this format:
{"name": "Essay", "grade_weight": null, "due_date": "03/05/2026", "completed": false}

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


# ── Priority Engine ───────────────────────────────────────────────────────────

def priority_score(assignment):
    """Calculate urgency score: higher grade weight + fewer days = higher score."""
    grade_weight = assignment["grade_weight"]
    due_date = assignment["due_date"]
    due_date_obj = datetime.strptime(due_date, "%m/%d/%Y")
    days_until_due = due_date_obj - datetime.today()
    score = grade_weight / days_until_due.days
    return score

def priority_list(all_assignments):
    """Return the top 5 assignments ranked by priority score."""
    assignment_list = []
    for assignment in all_assignments:
        if assignment["grade_weight"] is None or assignment["due_date"] is None:
            continue
        assignment_weight = priority_score(assignment)
        assignment_list.append((assignment_weight, assignment))

    sorted_list = sorted(assignment_list, reverse=True)
    return sorted_list[:5]


# ── Main Menu ─────────────────────────────────────────────────────────────────

def student_choice():
    while True:
        choice = int(input(
            "\nWhat would you like to do? Please select an option by number."
            "\n1. Upload a syllabus"
            "\n2. Manually add an assignment"
            "\n3. View assignments"
            "\n4. Quit\n"
        ))
        if choice == 1:
            filename = input("Enter the filename of your syllabus or course schedule: ")
            text = extract_text(filename)
            result = gemini(text)
            assignment_list = json.loads(result)
            save_assignments(assignment_list)
            print(f"Upload complete! {len(assignment_list)} assignments saved.")
        elif choice == 2:
            new_assignment = userinput()
            assignment_list = load_assignments()
            assignment_list.append(json.loads(new_assignment))
            save_assignments(assignment_list)
            print(f"Done! that puts us at {len(assignment_list)} assignments saved.")
        elif choice == 3:
            all_assignments = load_assignments()
            print(all_assignments)
            print(f"Exactly {len(all_assignments)} assignments!")
        elif choice == 4:
            break
        else:
            print(
                "That's not an option. Please select one of the following:"
                "\n1. Upload a syllabus"
                "\n2. Manually add an assignment"
                "\n3. View assignments"
                "\n4. Quit"
            )


student_choice()