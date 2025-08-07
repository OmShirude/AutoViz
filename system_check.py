from dashboard_app.nlp_model.llm_handler import LLMHandler
from dashboard_app.nlp_model.chart_creator import ChartCreator
from dashboard_app.nlp_model.system_prompt_generator import SystemPromptGenerator
import json

user_query = input("you: ")
db_url = 'postgresql://postgres:admin@127.0.0.1:5432/example'
generator = SystemPromptGenerator()
system_prompt = generator.generate_prompt(db_url=db_url)

llm = LLMHandler()

raw_output = llm.generate_sql_and_chart(user_query=user_query, system_prompt=system_prompt)
print(raw_output)
if raw_output.strip().startswith("```"):
    raw_output = raw_output.strip().strip("`")
    first_newline = raw_output.find("\n")
    raw_output = raw_output[first_newline+1:]  # Skip first line with ```json

parsed_output = json.loads(raw_output)
print(json.dumps(parsed_output),"\n\n")

def serialize_params_field(payload: dict) -> dict:
    """Convert the 'params' field in the dict into a JSON string."""
    if 'params' in payload and isinstance(payload['params'], dict):
        payload['params'] = json.dumps(payload['params'])
    return payload


final_payload = serialize_params_field(parsed_output)
print(json.dumps(final_payload))
chart = ChartCreator()
chart_creation_result = chart.create_chart(final_payload)
print("📊 Chart Creation Response:", chart_creation_result)
