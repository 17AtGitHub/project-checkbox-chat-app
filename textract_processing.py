import boto3
import json
import time
import trp
from trp.trp2 import TDocumentSchema
from trp.t_pipeline import order_blocks_by_geo_x_y

program_file_name = "textract_processing.py"

def process_document(bucket, key):
    textract = boto3.client('textract')
    
    try:
        print(f"{program_file_name} - Starting Textract job: inprocess...")
        # Start job
        response = textract.start_document_analysis(
            DocumentLocation={'S3Object': {'Bucket': bucket, 'Name': key}},
            FeatureTypes=['TABLES']
        )
        job_id = response['JobId']
    except Exception as e:
        print(f"{program_file_name} - ERROR: Starting Textract job: {e}")
        return
    
    # Wait for job completion
    try:
        print(f"{program_file_name} - Waiting for Textract job completion: inprocess...")
        while True:
            response = textract.get_document_analysis(JobId=job_id)
            status = response['JobStatus']
            if status in ['SUCCEEDED', 'FAILED']:
                break
            time.sleep(5)
        
        if status == 'FAILED':
            print(f"{program_file_name} - ERROR: Textract job failed")
            raise Exception("Textract job failed")
    except Exception as e:
        print(f"{program_file_name} - ERROR: Waiting for Textract job completion: {e}")
        return
    
    # Get results
    pages = []
    next_token = None
    try:
        print(f"{program_file_name} - Retrieving Textract job results: inprocess...")
        while True:
            if next_token:
                response = textract.get_document_analysis(JobId=job_id, NextToken=next_token)
            else:
                response = textract.get_document_analysis(JobId=job_id)
            pages.append(response)
            next_token = response.get('NextToken')
            if not next_token:
                break
    except Exception as e:
        print(f"{program_file_name} - ERROR: Retrieving Textract job results: {e}")
        return
    
    try:
        print(f"{program_file_name} - Combining Textract job results: inprocess...")
        # Combine results
        combined_json = {'Blocks': []}
        for page in pages:
            combined_json['Blocks'].extend(page['Blocks'])
    except Exception as e:
        print(f"{program_file_name} - ERROR: Combining Textract job results: {e}")
        return
    
    try:
        print(f"{program_file_name} - Ordering Textract blocks: inprocess...")
        # Order blocks
        t_doc = TDocumentSchema().load(combined_json)
        ordered_doc = order_blocks_by_geo_x_y(t_doc)

        trp_doc = trp.Document(TDocumentSchema().dump(ordered_doc))
    except Exception as e:
        print(f"{program_file_name} - ERROR: Ordering Textract blocks: {e}")
        return
    
    try:
        print(f"{program_file_name} - Parsing Textract document: inprocess...")
        # Parse document
        parsed_content = parse_document(trp_doc)
    except Exception as e:
        print(f"{program_file_name} - ERROR: Parsing Textract document: {e}")
        return
    
    try:
        print(f"{program_file_name} - Saving Textract results to S3: inprocess...")
        # Save results to S3
        s3 = boto3.client('s3')
        s3.put_object(Bucket=bucket, Key=f"{key}_parsed.txt", Body=parsed_content)
        s3.put_object(Bucket=bucket, Key=f"{key}_raw.json", Body=json.dumps(combined_json))
    except Exception as e:
        print(f"{program_file_name} - ERROR: Saving Textract results to S3: {e}")
        return

def parse_document(trp_doc):
    parsed_content = []
    
    for page in trp_doc.pages:
        for line in page.lines:
            text = line.text.strip()
            if text:
                selection_elements = [word for word in line.words if isinstance(word, trp.SelectionElement)]
                
                if selection_elements:
                    selected = [se for se in selection_elements if se.selectionStatus == 'SELECTED']
                    if selected:
                        # Only add the text of the selected option
                        selected_text = selected[0].selectionStatus
                        parsed_content.append(f"{text} {selected_text.upper()}")
                    else:
                        parsed_content.append(f"{text} UNANSWERED")
                else:
                    parsed_content.append(text)
        
        print(f"{program_file_name} - Parsing Lines Complete")
        if page.tables:
            parsed_content.append("\nTABLE:")
            for table in page.tables:
                for row in table.rows:
                    row_text = ' | '.join([cell.text.strip() for cell in row.cells])
                    parsed_content.append(row_text)
                parsed_content.append("")  # Empty line after each table
        print(f"{program_file_name} - Parsing Tables Complete")
    
    return '\n'.join(parsed_content)
