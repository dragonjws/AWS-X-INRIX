import re
import boto3
import pandas as pd
import os
from dotenv import load_dotenv
import json
import ratemyprof_info

# === Load AWS credentials ===
load_dotenv()
access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")

# === S3 setup ===
bucket_name = 'schedulebuildertool'
s3_key = 'classes/SCU_Find_Course_Sections.xlsx'
local_file = 'SCU_Find_Course_Sections.xlsx'

s3_client = boto3.client(
    's3',
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_access_key,
    region_name="us-east-1"
)

# === Download and read Excel ===
print("Downloading Excel file from S3...")
s3_client.download_file(bucket_name, s3_key, local_file)
print("File downloaded successfully.\n")

# === Read relevant data ===
df = pd.read_excel(local_file)
columns_of_interest = [
    "Course Section",
    "All Instructors",
    "Section Status",
    "Enrolled/Capacity",
    "Meeting Patterns",
    "Locations"
]

# Only keep valid columns
df = df[[c for c in columns_of_interest if c in df.columns]]
print(f"Loaded {len(df)} total rows with columns:")
print(df.columns.tolist(), "\n")

# === Collect user preferences ===
print("="*50)
print("SCHEDULE GENERATION PREFERENCES")
print("="*50)

preferred_times = input("Preferred time range (e.g., 'morning', 'afternoon', 'any'): ").strip()
specific_courses = input("Specific courses you must take? (e.g., 'PSYC 51, MATH 30'): ").strip()
avoid_conflicts = input("Avoid back-to-back classes? (y/n): ").strip().lower()
teacher_preference = input("What do you want in a teacher: ").strip()

# === Filter for user-specified courses (exact match with section numbers) ===
if specific_courses:
    course_keywords = [c.strip() for c in specific_courses.split(',')]
    mask = pd.Series(False, index=df.index)
    
    for keyword in course_keywords:
        # Match pattern like "SOCI 1-" to get SOCI 1-2, SOCI 1-3, etc.
        # This prevents matching SOCI 11, SOCI 100, SOCI 121, etc.
        pattern = f"{keyword}-"
        mask |= df["Course Section"].str.contains(pattern, case=False, na=False, regex=False)
    
    filtered_df = df[mask]
    
    if filtered_df.empty:
        print("⚠️ Warning: No matching courses found in data. Double-check your input.")
        print(f"   Searched for patterns like: {[c + '-' for c in course_keywords]}")
        filtered_df = df  # fallback to full dataset
    else:
        print(f"✅ Found {len(filtered_df)} matching rows for: {course_keywords}")
else:
    filtered_df = df

# Debug print
print("\nFiltered course sections include:")
print(filtered_df["Course Section"].unique()[:30])  # show first 30 matches for verification
print()

# === Summarize course data for Claude ===
summary = f"""
COURSE DATA SUMMARY:
- Total matching sections: {len(filtered_df)}
- Columns: {', '.join(filtered_df.columns.tolist())}

Sample of matching data:
{filtered_df.head(20).to_string(index=False)}
"""

# Clean up downloaded file
os.remove(local_file)

# === Prepare Bedrock client ===
client = boto3.client(
    service_name="bedrock-runtime",
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_access_key,
    region_name="us-east-1",
)

model_id = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"

# === Build the message for the model ===
prompt = f"""
You are an expert academic advisor. I need you to analyze course sections and extract professor information.

COURSE DATA:
{summary}

MY PREFERENCES:
- Required courses: {specific_courses or 'None specified'}

TASK:
Find all course sections for the required courses and extract professor information in JSON format.

IMPORTANT RULES:
1. When matching required courses, use **exact course-number prefixes only**.  
   - Example: if the user specifies "MATH 51", only include course sections whose
     "Course Section" column begins with "MATH 51-" (a hyphen immediately after the number).  
   - Exclude any courses like "MATH 511", "MATH 519", or "MATH 512".
2. Do **not fabricate** or infer any classes that do not appear in the dataset.
3. Output ONLY the JSON array below - no explanations, no markdown, no other text.

OUTPUT FORMAT (JSON only):
[
    {{"class number": "1",
    "course section": "MATH 51-1", 
    "teacher": "Professor Name",
    "time": "MWF 1:00-2:05 pm"}},
    {{"class number": "1",
    "course section": "MATH 51-2",
    "teacher": "Another Professor", 
    "time": "TTH 8:00-12:10pm"}},
    {{"class number": "2",
    "course section": "PHYS 32-1",
    "teacher": "Physics Professor",
    "time": "MWF 2:10-3:15pm"}}
]

The "class number" indicates what class it is. For example, if I need to take MATH 51, all course sections of MATH 51 are labeled class number 1, and if I need to take PHYS 32, all course sections of PHYS 32 are labeled class number 2.

RESPOND WITH JSON ONLY - NO OTHER TEXT.
"""
conversation = [
    {"role": "user", "content": [{"text": prompt}]}
]

# === Stream response from Claude ===
print("\nGenerating schedule... please wait.\n")

def split_name(full_name: str) -> tuple[str, str] | None:
    """
    Split 'First Middle Last' → ('First','Last') while tolerating middle names/initials.
    If only one token, return None.
    """
    parts = [p for p in re.split(r"\s+", full_name.strip()) if p]
    if len(parts) < 2:
        return None
    first = parts[0]
    last  = " ".join(parts[1:])  # supports multi-word last names
    return first, last

claude_output = ""
try:
    response = client.converse_stream(
        modelId=model_id,
        messages=conversation,
        inferenceConfig={"maxTokens": 1467, "temperature": 0.9},
    )

    for chunk in response["stream"]:
        if "contentBlockDelta" in chunk:
            delta = chunk["contentBlockDelta"]["delta"]
            if delta.get("text"):
                print(delta["text"], end="")
                claude_output += delta["text"]
except Exception as e:
    print(f"ERROR: Failed to query Bedrock. Reason: {e}")
    claude_output = ""  # Ensure it's empty if there was an error

# Check if we have valid output before parsing JSON
if not claude_output.strip():
    print("❌ ERROR: No response received from Claude. Please check your AWS credentials and try again.")
    exit(1)

# Try to extract JSON from the response (in case Claude includes extra text)
def extract_json_from_response(text):
    """Extract JSON array from Claude response, handling cases where extra text is included."""
    text = text.strip()
    
    # First, try to parse the entire response as JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # If that fails, look for JSON array patterns
    import re
    
    # Look for JSON array starting with [
    json_pattern = r'\[[\s\S]*?\]'
    matches = re.findall(json_pattern, text)
    
    for match in matches:
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue
    
    # If no valid JSON found, return None
    return None

try:
    all_sections = extract_json_from_response(claude_output)
    if all_sections is None:
        raise json.JSONDecodeError("No valid JSON found in response", claude_output, 0)
except json.JSONDecodeError as e:
    print(f"❌ ERROR: Failed to parse Claude's response as JSON: {e}")
    print(f"Raw output received: {repr(claude_output[:200])}...")  # Show first 200 chars
    exit(1)
teacher_jsons = []
course_sections_map = []  # Map to track which professor info goes with which course section

for section in all_sections:
    teacher_name = section['teacher']
    name_parts = split_name(teacher_name)
    
    if name_parts is None:
        print(f"⚠️ Could not parse teacher name: '{teacher_name}' - skipping")
        teacher_jsons.append(None)
        course_sections_map.append({
            'course_section': section.get('course section', 'Unknown'),
            'class_number': section.get('class number', 'Unknown'),
            'time': section.get('time', 'Unknown'),
            'teacher': teacher_name
        })
        continue
    
    first_name, last_name = name_parts
    print(f"🔍 Looking up professor: {first_name} {last_name}")
    
    teacher_info = ratemyprof_info.professorRater(first_name, last_name)
    teacher_jsons.append(teacher_info)
    course_sections_map.append({
        'course_section': section.get('course section', 'Unknown'),
        'class_number': section.get('class number', 'Unknown'),
        'time': section.get('time', 'Unknown'),
        'teacher': teacher_name
    })

# Create a structured comparison data set
comparison_data = []
for i, (section_info, prof_data) in enumerate(zip(course_sections_map, teacher_jsons)):
    if prof_data and prof_data.get('professor_info'):
        comparison_data.append({
            'course_section': section_info['course_section'],
            'class_number': section_info['class_number'],
            'time': section_info['time'],
            'teacher_name': section_info['teacher'],
            'professor_data': {
                'rating': prof_data['professor_info'].get('avgRating'),
                'difficulty': prof_data['professor_info'].get('avgDifficulty'),
                'numRatings': prof_data['professor_info'].get('numRatings'),
                'wouldTakeAgain': prof_data['professor_info'].get('wouldTakeAgainPercent'),
                'department': prof_data['professor_info'].get('department'),
                'recent_comments': [c.get('comment', '') for c in prof_data.get('comments', [])[:2]]
            }
        })

comparison_prompt = f"""
You are an academic advisor helping a student choose the best professors based on their preferences.

STUDENT'S TEACHER PREFERENCES: "{teacher_preference}"

AVAILABLE COURSE SECTIONS AND PROFESSORS:
{json.dumps(comparison_data, indent=2)}

TASK:
1. Review each course section and its available professor(s)
2. For each unique course (grouped by "class_number"), recommend the BEST professor that matches the student's preferences
3. Consider: ratings, difficulty, "would take again" percentage, and recent student comments
4. Output JSON ONLY with this format (no markdown, no explanations):
[
    {{
        "course_section": "MATH 51-2",
        "teacher": "Professor Name",
        "class_number": "1",
        "time": "MWF 2:10-3:15pm",
        "reasoning": "Brief explanation of why this professor fits the student's preferences"
    }},
    ...
]

IMPORTANT: Output ONLY the JSON array. No other text or formatting.
"""
comparison_conversation = [
    {
        "role": "user",
        "content": [{"text": comparison_prompt}]
    }
]
claude_comparison_output = ""
try:
    comparison_response = client.converse_stream(
        modelId=model_id,
        messages=comparison_conversation,
        inferenceConfig={"maxTokens": 1467, "temperature": 0.5},
    )

    for chunk in comparison_response["stream"]:
        if "contentBlockDelta" in chunk:
            delta = chunk["contentBlockDelta"]["delta"]
            if delta.get("text"):
                print(delta["text"], end="")  # print in real-time
                claude_comparison_output += delta["text"]

except Exception as e:
    print(f"ERROR: Failed to query Bedrock for comparison. Reason: {e}")
    claude_comparison_output = ""  # Ensure it's empty if there was an error

# Check if we have valid comparison output before parsing JSON
if not claude_comparison_output.strip():
    print("❌ ERROR: No response received from Claude for teacher comparison. Please check your AWS credentials and try again.")
    exit(1)

# === Parse Claude's output into Python JSON ===
try:
    recommended_teachers = extract_json_from_response(claude_comparison_output)
    if recommended_teachers is None:
        raise json.JSONDecodeError("No valid JSON found in comparison response", claude_comparison_output, 0)
    print("\n\n✅ Final instructor recommendations parsed successfully.")
except json.JSONDecodeError as e:
    print("❌ ERROR parsing Claude's output as JSON:", e)
    print(f"Raw comparison output received: {repr(claude_comparison_output[:200])}...")  # Show first 200 chars
    recommended_teachers = []
instructors = [s['teacher'] for s in all_sections]

# === Display Professor Information ===
print("\n" + "="*60)
print("PROFESSOR INFORMATION COLLECTED")
print("="*60)

if teacher_jsons:
    print(f"Found information for {len(teacher_jsons)} professors:")
    print()
    
    for i, prof_info in enumerate(teacher_jsons, 1):
        if prof_info and prof_info.get('professor_info'):  # Check if we got valid data
            prof_data = prof_info['professor_info']
            print(f"{i}. {prof_data.get('firstName', 'N/A')} {prof_data.get('lastName', 'N/A')}")
            print(f"   Department: {prof_data.get('department', 'N/A')}")
            print(f"   Average Rating: {prof_data.get('avgRating', 'N/A')}/5.0")
            print(f"   Average Difficulty: {prof_data.get('avgDifficulty', 'N/A')}/5.0")
            print(f"   Number of Ratings: {prof_data.get('numRatings', 'N/A')}")
            print(f"   Would Take Again: {prof_data.get('wouldTakeAgainPercent', 'N/A')}%")
            print(f"   School: {prof_data.get('school', 'N/A')}")
            
            # Show recent comments
            comments = prof_info.get('comments', [])
            if comments:
                print(f"   Recent Comments:")
                for comment in comments[:3]:  # Show first 3 comments
                    comment_text = comment.get('comment', '')[:100]  # First 100 chars
                    if comment_text:
                        print(f"     - \"{comment_text}...\"")
            print()
        else:
            print(f"{i}. Professor data not available")
            print()
else:
    print("No professor information was collected.")

# === Display Recommended Teachers ===
print("\n" + "="*60)
print("🎯 RECOMMENDED TEACHERS BASED ON YOUR PREFERENCES")
print("="*60)

if recommended_teachers:
    print(f"\n✅ Found {len(recommended_teachers)} personalized recommendations:")
    print()
    
    for i, rec in enumerate(recommended_teachers, 1):
        print(f"{i}. 📚 Course: {rec.get('course_section', 'N/A')}")
        print(f"   👨‍🏫 Recommended Teacher: {rec.get('teacher', 'N/A')}")
        if rec.get('time'):
            print(f"   🕐 Time: {rec.get('time')}")
        if rec.get('class_number'):
            print(f"   #️⃣  Class Number: {rec.get('class_number')}")
        print(f"   💡 Reasoning: {rec.get('reasoning', 'N/A')}")
        print()
else:
    print("⚠️ No teacher recommendations were generated.")

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Total course sections analyzed: {len(all_sections)}")
print(f"Professors researched: {len(teacher_jsons)}")
print(f"Teacher recommendations: {len(recommended_teachers)}")
print("="*60)

