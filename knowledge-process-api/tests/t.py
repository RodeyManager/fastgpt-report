import requests
import os
import time

pdf_path = "E:/dify/UnstructuredIO/unstructured/example-docs/pdf/layout-parser-paper.pdf"
with open(pdf_path, 'rb') as f:
    content = f.read()

print("Testing MinerU async response")

response = requests.post(
    "http://127.0.0.1:8000/file_parse",
    files={"files": (os.path.basename(pdf_path), content)},
    data={
        "return_md": "true",
        "response_format_zip": "false",
        "return_original_file": "false",
        "lang": "ch",
        "parse_method": "auto",
        "backend": "pipeline"
    },
    timeout=300
)

print(f"Status: {response.status_code}")
result = response.json()
print(f"Keys: {list(result.keys())}")

# Check task status
if "task_id" in result:
    task_id = result["task_id"]
    print(f"Task ID: {task_id}")
    print(f"Status: {result.get('status')}")
    
    # If failed, show error
    if result.get("status") == "failed":
        print(f"Error: {result.get('error')}")
    else:
        # Poll for result
        status_url = result.get("status_url")
        result_url = result.get("result_url")
        
        print(f"\nPolling for result...")
        max_attempts = 30
        for i in range(max_attempts):
            # Check status
            status_resp = requests.get(status_url, timeout=30)
            status_data = status_resp.json()
            print(f"  Attempt {i+1}: {status_data.get('status')}")
            
            if status_data.get("status") == "success":
                # Get final result
                final_resp = requests.get(result_url, timeout=30)
                final_result = final_resp.json()
                print(f"\nFinal Keys: {list(final_result.keys())}")
                if "markdown" in final_result:
                    print(f"Markdown: {len(final_result['markdown'])} chars")
                    print(final_result["markdown"][:500])
                break
            elif status_data.get("status") == "failed":
                print(f"Failed: {status_data.get('error')}")
                break
            
            time.sleep(2)
        else:
            print("Timeout waiting for result")