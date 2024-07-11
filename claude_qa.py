import boto3
import json
from botocore.exceptions import ClientError

program_file_name = "claude_qa.py"

def ask_claude(bucket, key, question):
    print(f"{program_file_name} - Initializing Bedrock Runtime client: inprocess...")
    # Create a Bedrock Runtime client in the AWS Region of your choice.
    client = boto3.client("bedrock-runtime", region_name="us-east-1")

    # Set the model ID, e.g., Claude 3 Haiku.
    model_id = "anthropic.claude-3-haiku-20240307-v1:0"
    
    s3 = boto3.client('s3')

    try:
        print(f"{program_file_name} - Retrieving LM_info.txt from S3: inprocess...")
        # Get LM_info.txt
        lm_info = s3.get_object(Bucket=bucket, Key=f"{key}_LM_info.txt")['Body'].read().decode('utf-8')
    except ClientError as e:
        print(f"{program_file_name} - ERROR: Retrieving LM_info.txt: {e}")
        return
    except Exception as e:
        print(f"{program_file_name} - ERROR: Unexpected error while retrieving LM_info.txt: {e}")
        return

    # Prepare the message for Claude
    message_content = f"Here's the context:\n\n{lm_info}\n\nQuestion: {question}\n\nPlease answer the question based on the given context."
    
    # Prepare the request body
    max_tokens_to_generate = 250

    # Format the request payload using the model's native structure.
    native_request = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens_to_generate,
        "temperature": 0.5,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": message_content}],
            }
        ],
    }

    # Convert the native request to JSON.
    request = json.dumps(native_request)

    try:
        print(f"{program_file_name} - Invoking model {model_id}: inprocess...")
        # Invoke the model with the request.
        response = client.invoke_model(modelId=model_id, body=request)
    except ClientError as e:
        print(f"{program_file_name} - ERROR: Invoking model {model_id}: {e}")
        return
    except Exception as e:
        print(f"{program_file_name} - ERROR: Unexpected error while invoking model {model_id}: {e}")
        return

    try:
        print(f"{program_file_name} - Decoding model response: inprocess...")
        # Decode the response body.
        model_response = json.loads(response["body"].read())
        answer = model_response['content'][0]['text']
    except Exception as e:
        print(f"{program_file_name} - ERROR: Decoding model response: {e}")
        return

    print(f"{program_file_name} - Retrieving answer process completed successfully.")
    return answer
