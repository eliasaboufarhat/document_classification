from ollama import chat
from ollama import ChatResponse


class LLM:
    """ "
    To run use: ollama run deepseek-r1:1.5b
    """

    def __init__(self, model="deepseek-r1:1.5b"):
        self.model = model

    def run(self, prompt, base_model):

        response: ChatResponse = chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            format=base_model.model_json_schema(),
        )

        label = base_model.model_validate_json(response.message.content)

        return label


if __name__ == "__main__":
    from pydantic import BaseModel

    llm = LLM()

    class Label(BaseModel):
        label: str

    prompt = f"""
        I have the following documents metadata and text in one cluster:
        Recipe: How to make a cake

        Based on the content, choose the most appropriate label from this list or suggest a new one if it does not exists:
        []

        Return the result as JSON format. Make sure to follow this structure
        {{
            "label": "In here will be your label",
        }}
        """

    llm.run(prompt, Label)
