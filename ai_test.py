from ollama import chat

response = chat(
    model="qwen2.5-coder:3b",
    messages=[
        {
            "role": "user",
            "content": """
Create a modern Python calculator using tkinter.
Use OOP, type hints and clean code.
"""
        }
    ]
)

print(response.message.content)