import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv

load_dotenv()

# Put your AWS credentials in a .env file
access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")

client = boto3.client(
    service_name="bedrock-runtime",
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_access_key,
    region_name="us-east-1",
)

# The model or inference ID for the model you want to use
# !If you get an error with "Retry your request with the ID or ARN", use the inference ID version below

model_id = "openai.gpt-oss-20b-1:0" # Reasoning model

# Example inference ID for Claude 3.5 Sonnet
# model_id = "us.anthropic.claude-3-5-sonnet-20240620-v1:0" # No reasoning model

# The message you want to send to the model
user_message = "Summarize AWS"

conversation = [
    {
        "role": "user",
        "content": [{"text": user_message}],
    }
]

try:
    response = client.converse(
        modelId=model_id,
        messages=conversation,
        inferenceConfig={"maxTokens": 512, "temperature": 0.5, "topP": 0.9},
    )

    response_actual = response["output"]["message"]["content"]

    # Some models provide reasoning context and layout this JSON differently
    # Ex: reasoningContent comes after the main text response, so swap [0] and [1]
    # You can always debug by printing the full response
    # print(response_actual)

    if response_actual[0].get("reasoningContent"):
        reasoning_text = response_actual[0]["reasoningContent"]["reasoningText"]["text"]
        print("Reasoning:")
        print(reasoning_text)
        response_text = response_actual[1]["text"]
    else:
        response_text = response_actual[0]["text"]

    print("\nResponse:")
    print(response_text)
except Exception as e:
    print(f"ERROR: Can't invoke '{model_id}'. Reason: {e} (Exception type: {type(e).__name__})")