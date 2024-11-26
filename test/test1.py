from openai import OpenAI,AsyncOpenAI
from dotenv import load_dotenv,dotenv_values
load_dotenv()
client = OpenAI()
def PrintHelloWorld():
    print("Hello World")
functions = [
    {
        "name" : "PrintHelloWorld",
        "description" : "Prints Hello World",
        "parameters": {
            "type" : "object",
            "properties": {}
        },
    }
]   
comp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role":"user","content":"can you prints hello world"}
    ],
    functions=functions,
    function_call="auto"
)
print(comp.choices[0].message)