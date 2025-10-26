import boto3
import pandas as pd
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv

load_dotenv()

# Put your AWS credentials in a .env file
access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")

# Create S3 client for downloading the Excel file
s3_client = boto3.client(
    's3',
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_access_key,
    region_name="us-east-1"
)

# Download and read the Excel file from S3
try:
    bucket_name = 'schedulebuildertool'
    s3_key = 'classes/SCU_Find_Course_Sections.xlsx'
    local_file = 'SCU_Find_Course_Sections.xlsx'
    
    # Test S3 connection first
    print(f"Testing S3 connection to bucket: {bucket_name}")
    s3_client.head_bucket(Bucket=bucket_name)
    print("✓ S3 bucket access confirmed")
    
    # Check if file exists
    print(f"Checking if file exists: {s3_key}")
    s3_client.head_object(Bucket=bucket_name, Key=s3_key)
    print("✓ File exists in S3")
    
    # Download the file from S3
    print(f"Downloading {s3_key} from S3 bucket {bucket_name}...")
    s3_client.download_file(bucket_name, s3_key, local_file)
    print("✓ File downloaded successfully")
    
    # Read the Excel file
    df = pd.read_excel(local_file)
    
    print(f"Successfully loaded course data from S3")
    print(f"Data shape: {df.shape}")
    print("Column names:", df.columns.tolist())
    
    # Get a comprehensive summary of ALL courses
    print("Analyzing all courses in the dataset...")
    
    # Create a structured summary of all courses
    # This gives Claude access to all 1700 courses in a compact format
    
    # If there's a course identification column, use it
    course_col = None
    
    # Print all available columns to help debug
    print(f"Available columns in dataset: {df.columns.tolist()}")
    
    # Try to find a course identification column
    possible_course_cols = ['Course', 'CourseName', 'CourseID', 'Subject', 'CourseCode', 'Course Section', 
                           'CourseSection', 'Section', 'Course_Name', 'Course_Code', 'Class', 'ClassName',
                           'Class Name', 'Course Code', 'Subject Code']
    
    for col in possible_course_cols:
        if col in df.columns:
            course_col = col
            break
    
    # Create summary of all unique courses
    if course_col:
        unique_courses = df[course_col].unique()
        print(f"Found {len(unique_courses)} unique courses")
        
        # Get ALL unique courses, not just first 100
        all_courses_list = sorted(unique_courses)
        
        # Get a larger sample from different parts of the dataset
        sample_indices = []
        step = max(1, len(df) // 20)  # Get 20 samples across the dataset
        for i in range(0, len(df), step):
            sample_indices.append(i)
        sample_df = df.iloc[sample_indices]
        
        data_summary = f"""
    COMPREHENSIVE COURSE DATA:
    - Total courses/sections: {len(df)}
    - Unique courses available: {len(unique_courses)}
    - Columns available: {', '.join(df.columns.tolist())}
    
    ALL AVAILABLE COURSES ({len(all_courses_list)} total):
    {', '.join(all_courses_list)}
    
    SAMPLE COURSE DATA (showing {len(sample_df)} entries from across the dataset):
    {sample_df.to_string(index=False)}
    
    NOTE: This dataset contains {len(df)} total course sections across {len(unique_courses)} different courses.
    All courses listed above are available for scheduling.
    """
    else:
        # Fallback if no course column found
        sample_df = df.head(50)
        data_summary = f"""
    COMPREHENSIVE COURSE DATA:
    - Total courses/sections: {len(df)}
    - Columns available: {', '.join(df.columns.tolist())}
    
    REPRESENTATIVE COURSE DATA (50 entries):
    {sample_df.to_string(index=False)}
    
    NOTE: This dataset contains {len(df)} total course sections.
    """
    
    print(f"Created comprehensive summary with {len(unique_courses) if course_col else 'all'} courses")
    
    # Clean up the downloaded file
    os.remove(local_file)
    print("Cleaned up temporary file")
    
except Exception as e:
    error_type = type(e).__name__
    error_msg = str(e)
    
    print(f"❌ S3 Error Details:")
    print(f"   Error Type: {error_type}")
    print(f"   Error Message: {error_msg}")
    
    # Provide specific troubleshooting based on error type
    if "NoSuchBucket" in error_msg:
        print(f"\n🔧 TROUBLESHOOTING:")
        print(f"   • The bucket '{bucket_name}' does not exist")
        print(f"   • Check if the bucket name is correct")
        print(f"   • Verify you have access to this bucket")
    elif "AccessDenied" in error_msg:
        print(f"\n🔧 TROUBLESHOOTING:")
        print(f"   • Access denied to bucket '{bucket_name}' or file '{s3_key}'")
        print(f"   • Check your AWS credentials in the .env file")
        print(f"   • Verify your IAM user has S3 read permissions")
        print(f"   • Check bucket policy and ACL settings")
    elif "NoSuchKey" in error_msg:
        print(f"\n🔧 TROUBLESHOOTING:")
        print(f"   • The file '{s3_key}' does not exist in bucket '{bucket_name}'")
        print(f"   • Check if the file path is correct")
        print(f"   • Verify the file was uploaded successfully")
    elif "InvalidAccessKeyId" in error_msg:
        print(f"\n🔧 TROUBLESHOOTING:")
        print(f"   • Invalid AWS Access Key ID")
        print(f"   • Check your AWS_ACCESS_KEY_ID in the .env file")
    elif "SignatureDoesNotMatch" in error_msg:
        print(f"\n🔧 TROUBLESHOOTING:")
        print(f"   • Invalid AWS Secret Access Key")
        print(f"   • Check your AWS_SECRET_ACCESS_KEY in the .env file")
    else:
        print(f"\n🔧 TROUBLESHOOTING:")
        print(f"   • Check your AWS credentials in the .env file")
        print(f"   • Verify the bucket name and file path")
        print(f"   • Ensure your AWS account has S3 access")
    
    print(f"\n📋 REQUIRED AWS PERMISSIONS:")
    print(f"   • s3:GetObject for the specific file")
    print(f"   • s3:ListBucket for the bucket")
    print(f"   • s3:GetBucketLocation for region verification")
    
    course_data = "Error loading course data from S3"
    data_summary = "Error loading course data from S3"

client = boto3.client(
    service_name="bedrock-runtime",
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_access_key,
    region_name="us-east-1",
)

# The model or inference ID for the model you want to use
# !If you get an error with "Retry your request with the ID or ARN", use the inference ID version below

model_id = "us.anthropic.claude-sonnet-4-5-20250929-v1:0" # Reasoning model

# Example inference ID for Claude 3.5 Sonnet
# model_id = "us.anthropic.claude-3-5-sonnet-20240620-v1:0" # No reasoning model

# Get user preferences for schedule generation
print("\n" + "="*50)
print("SCHEDULE GENERATION PREFERENCES")
print("="*50)

# Get user input for schedule preferences
preferred_days = input("What days do you prefer for classes? (e.g., 'MWF', 'TTh', 'Monday-Friday'): ").strip()
preferred_times = input("What time range do you prefer? (e.g., 'morning', 'afternoon', '9am-2pm'): ").strip()
max_courses = input("How many courses do you want to take? (leave blank for all available): ").strip()
specific_courses = input("Any specific courses you must take? (leave blank if none): ").strip()
avoid_conflicts = input("Do you want to avoid back-to-back classes? (y/n): ").strip().lower()

# Create a simple, direct message with Excel file information
print("\nCreating schedule recommendation based on Excel file data...")

# Create the final conversation with Excel file structure information
final_message = f"""You are an expert academic advisor. I need you to create an optimal personalized schedule based on the course schedule data from an Excel file.

EXCEL FILE STRUCTURE:
{data_summary}

MY PREFERENCES:
- Preferred days: {preferred_days if preferred_days else 'No preference'}
- Preferred times: {preferred_times if preferred_times else 'No preference'}
- Number of courses: {max_courses if max_courses else 'All available'}
- Required courses: {specific_courses if specific_courses else 'None specified'}
- Avoid back-to-back classes: {'Yes' if avoid_conflicts == 'y' else 'No preference'}

TASK: Based on the Excel file structure above, please provide:

1. **RECOMMENDED SCHEDULE**:
   - Create a specific weekly schedule showing:
     * Course names/codes
     * Days of the week
     * Exact times
     * Room/location if available
   - Format it as a clear timetable

2. **ALTERNATIVES**: 
   - Provide 2-3 alternative schedule options
   - Explain the trade-offs of each option

3. **RECOMMENDATIONS**:
   - Suggest any courses I should consider adding/removing
   - Point out any potential issues with the proposed schedule
   - Advise on course load balance

Please be specific and practical in your recommendations. Use the column names and data structure from the Excel file to create realistic schedule suggestions."""

conversation = [
    {
        "role": "user",
        "content": [{"text": final_message}],
    }
]

try:
    streaming_response = client.converse_stream(
        modelId=model_id,
        messages=conversation,
        inferenceConfig={"maxTokens": 512, "temperature": 0.8},
    )

    # Extract and print the streamed response text in real-time
    for chunk in streaming_response["stream"]:
        if "contentBlockDelta" in chunk:
            delta = chunk["contentBlockDelta"]["delta"]

            if delta.get("text"):
                print(delta["text"], end="")
            elif delta.get("reasoningContent") and delta["reasoningContent"].get("text"):
                print(f"Reasoning: {delta["reasoningContent"]["text"]}")

except Exception as e:
    print(f"ERROR: Can't invoke '{model_id}'. Reason: {e} (Exception type: {type(e).__name__})")