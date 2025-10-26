import boto3
import pandas as pd
import os
from dotenv import load_dotenv

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

preferred_times = input("Preferred time range (e.g., 'morning', '9am-2pm', 'any'): ").strip()
specific_courses = input("Specific courses you must take? (e.g., 'PSYC 51, MATH 30'): ").strip()
avoid_conflicts = input("Avoid back-to-back classes? (y/n): ").strip().lower()

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
You are an expert academic advisor. I need you to create an optimal personalized schedule.

COURSE DATA:
{summary}

MY PREFERENCES:
- Preferred times: {preferred_times or 'No preference'}
- Required courses: {specific_courses or 'None specified'}
- Avoid back-to-back classes: {'Yes' if avoid_conflicts == 'y' else 'No preference'}

TASK:
1. Create a **weekly timetable** with:
   - Course names/codes
   - Days and times
   - Instructor
   - Room/location
2. Give **2–3 alternative schedules** with trade-offs.
3. Provide **recommendations** (balance, load, conflicts).
4. Treat classes like PSYC 51-2 and PSYC 51-3 as sections of the same course.  
5. When matching required courses, use **exact course-number prefixes only**.  
   - Example: if the user specifies “SOCI 1”, only include course sections whose
     “Course Section” column begins with “SOCI 1-” (a hyphen immediately after the number).  
   - Exclude any courses like “SOCI 11”, “SOCI 119”, or “SOCI 192”.
6. Factor in **all available course sections** from the dataset (1700+ rows).
7. Do **not fabricate** or infer any classes that do not appear in the dataset.
"""
conversation = [
    {"role": "user", "content": [{"text": prompt}]}
]

# === Stream response from Claude ===
print("\nGenerating schedule... please wait.\n")

try:
    response = client.converse_stream(
        modelId=model_id,
        messages=conversation,
        inferenceConfig={"maxTokens": 800, "temperature": 0.3},
    )

    for chunk in response["stream"]:
        if "contentBlockDelta" in chunk:
            delta = chunk["contentBlockDelta"]["delta"]
            if delta.get("text"):
                print(delta["text"], end="")

except Exception as e:
    print(f"ERROR: Failed to query Bedrock. Reason: {e}")
