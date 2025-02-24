"""
    api.py - API class interact with Ollama

"""
from wrapper import Script
from ollama import Client

class ResumeAPI:
    def __init__(
        self,
        url: str = "http://localhost:11434"
    ):
        self.client = Client(host=url)

    def create(
        self,
        summary: str
    ):
        response = self.client.chat(
            model="deepscaler:1.5b-preview-q4_K_M",
            messages=[
                {
                    "role": "system",
                    "content": "You are a fabulous director that able to give educational scripts for people want to learn English."
                },
                {
                    "role": "user",
                    "content": "Please provide a script based on the following statements:\n" + summary,
                }
            ],
            format=Script.model_json_schema()
        )
        response = Script.model_validate_json(response.message.content).model_dump()
        print(f"Ollama response: {response}")
        content = response["content"]
        content[0] = "CONTENT: " + content[0]
        text = [
            f'TITLE: {response["title"]}',
            f'DESCRIPTION: {response["description"]}'
        ] + content
        return [{
            "role": "assistant",
            "content": txt
        } for txt in text]