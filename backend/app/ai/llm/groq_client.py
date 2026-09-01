from groq import Groq

from app.ai.config import ai_settings


class GroqClient:

    def __init__(self):

        self.client = Groq(
            api_key=ai_settings.GROQ_API_KEY
        )

    def generate(
        self,
        prompt: str,
        temperature: float = 0.0
    ) -> str:

        response = self.client.chat.completions.create(
            model=ai_settings.GROQ_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=temperature
        )

        return response.choices[0].message.content.strip()


groq_client = GroqClient()