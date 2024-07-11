# Document Processing and QA Application

This application processes documents using AWS Textract, restructures the content, and allows users to ask questions about the document using Claude, an AI model from Anthropic.

## Features

- Document upload and processing using AWS Textract
- Document content restructuring
- Question-answering capability using Claude AI
- User-friendly interface built with Streamlit

## Prerequisites

- Python 3.7+
- AWS account with access to S3 and Textract services
- Anthropic API access for Claude

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/document-qa-app.git
   cd document-qa-app
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your AWS credentials:
   - Create a file named `~/.aws/credentials` (on Linux/Mac) or `C:\Users\YourUsername\.aws\credentials` (on Windows)
   - Add your AWS access key and secret key:
     ```
     [default]
     aws_access_key_id = YOUR_ACCESS_KEY
     aws_secret_access_key = YOUR_SECRET_KEY
     ```

## Usage

1. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

2. Open your web browser and go to `http://localhost:8501`

3. Upload a document (PDF, PNG, JPG, or JPEG)

4. Wait for the document to be processed and restructured

5. Enter your question about the document and click "Submit"

6. View the AI-generated answer

## File Structure

- `app.py`: Main Streamlit application
- `textract_processing.py`: Handles document processing with AWS Textract
- `document_restructuring.py`: Restructures the processed document content
- `claude_qa.py`: Manages interaction with the Claude AI model for question-answering
- `requirements.txt`: Lists all Python dependencies

