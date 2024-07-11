import streamlit as st
import boto3
from textract_processing import process_document
from document_restructuring import restructure_document
from claude_qa import ask_claude

# Set up S3 client
s3 = boto3.client('s3')
BUCKET_NAME = 'checkbox-project-textract-chat-app-daksh'

# File name variable
program_file_name = "app.py"

def main():
    st.title("Document Processing and Q&A App")

    # Initialize session state
    if 'document_processed' not in st.session_state:
        st.session_state.document_processed = False
    if 's3_key' not in st.session_state:
        st.session_state.s3_key = None

    # File uploader
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "png", "jpg", "jpeg"])
    
    if uploaded_file is not None and not st.session_state.document_processed:
        # Upload to S3
        s3_key = f"uploads/{uploaded_file.name}"
        try:
            print(f"{program_file_name} - Uploading file: inprocess...")
            s3.upload_fileobj(uploaded_file, BUCKET_NAME, s3_key)
            st.session_state.s3_key = s3_key
        except Exception as e:
            print(f"{program_file_name} - Uploading file: error - {e}")
        
        # Process document
        try:
            print(f"{program_file_name} - Processing document: inprocess...")
            with st.spinner('Processing document...'):
                process_document(BUCKET_NAME, s3_key)
        except Exception as e:
            print(f"{program_file_name} - Processing document: error - {e}")
        
        # Restructure document
        try:
            print(f"{program_file_name} - Restructuring document: inprocess...")
            with st.spinner('Restructuring document...'):
                restructure_document(BUCKET_NAME, s3_key)
        except Exception as e:
            print(f"{program_file_name} - Restructuring document: error - {e}")

        print(f"{program_file_name} - Document processed and restructured!")
        st.success("Document processed and restructured!")
        st.session_state.document_processed = True

    # Q&A interface
    if st.session_state.document_processed:
        st.subheader("Ask a question about the document")
        question = st.text_input("Enter your question")
        
        if st.button("Submit"):
            if question:
                try:
                    print(f"{program_file_name} - Getting answer for question: inprocess...")
                    with st.spinner('Getting answer...'):
                        answer = ask_claude(BUCKET_NAME, st.session_state.s3_key, question)
                    st.write(f"Answer: {answer}")
                except Exception as e:
                    print(f"{program_file_name} - Getting answer for question: error - {e}")
                    st.error("An error occurred while getting the answer.")
            else:
                st.warning("Please enter a question.")

if __name__ == "__main__":
    main()