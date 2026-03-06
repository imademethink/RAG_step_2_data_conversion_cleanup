import os
import json
import requests
from ragas.metrics import answer_relevancy, faithfulness, context_precision, context_recall
from pypdf import PdfReader

# env setup
file_ollama_key = "..\\data\\ollama_api_key_file.txt"
API_KEY = open(file_ollama_key).read()
BASE_URL = "https://ollama.com"
LLM_MODEL = "gpt-oss:120b-cloud"
EMBEDDING_MODEL = "nomic-embed-text"
REMOTE_OLLAMA_URL = "https://ollama.com/api/generate"

# env key setup
os.environ["OLLAMA_HOST"] = BASE_URL
os.environ["OLLAMA_API_KEY"] = API_KEY
os.environ["OPENAI_API_KEY"] = "not-used"

# prompt setup
total_item_verify = 10
headers = {"Content-Type": "application/json", "Authorization": f"Bearer {open(file_ollama_key).read()}"}
internal_prompt = ("Act as Python ragas expert. Analyze below content. "
                   "Do not round off numbers. Be simple and straight forward. "
                   "Do not open any link. Consider simple question as query and "
                   "accordingly generate question, ground truth. "
                   "Provide output in json format. Provide output in plain English. No unicode characters. "
                   "Respective key in json should be question, ground_truth. "
                   "Each key and value should be strictly string. "
                   "Provide top " + str(total_item_verify) + " set.")

# read input pdf file
pdf_path = "..\\data\\stock_market\\Report1.pdf"
pdf_rdr = PdfReader(pdf_path)
pdf_full_text = ""
for one_page in pdf_rdr.pages:
    pdf_full_text += one_page.extract_text()
internal_prompt = internal_prompt + "  " + pdf_full_text

# read output md file
md_path = "..\\data\\stock_market\\Report1_pdf.md"
with open(md_path, 'r', encoding='utf-8') as f:
    md_full_text = f.read()
md_full_text = md_full_text.lower()

# LLM integration
payload = {"model": LLM_MODEL, "prompt": internal_prompt, "stream": False}
response = requests.post(REMOTE_OLLAMA_URL, headers=headers, data=json.dumps(payload))
response.raise_for_status()
response_data = response.json()["response"].replace("```json", "").replace("```", "")
response_data_json_array = json.loads(response_data)
response.close()

# validate the (top 10) content from pdf suggested by LLM are found in md file, in automated way
not_found_cnt = 0
for n in range(0, total_item_verify):
    ground_truth = response_data_json_array[n]["ground_truth"]
    print("Ground Truth : " + ground_truth)
    if ground_truth.lower() in md_full_text:
        print("=>Found")
    else:
        not_found_cnt+= 1
        print("=>Not Found")

assert not_found_cnt == 0, "Some of the ground truth not found."
