import boto3

# Initialize Boto3 client for Amazon Bedrock
client = boto3.client('bedrock')

# List available foundation models
response = client.list_foundation_models()

# Access models under 'modelSummaries' key
models = response['modelSummaries']

# Print details of each model
for model in models:
    print(f"Model ID: {model['modelId']}, Name: {model['modelName']}, Provider: {model['providerName']}")

