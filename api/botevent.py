from openai import OpenAI,AsyncOpenAI
from dotenv import dotenv_values
from models.music import Music
def head(async_iterator): return async_iterator.__anext__()

def CheckUSer(args):
    return True
function_mapping = {
    "SkipSong": lambda bot, message: Music(bot = bot,message=message).SkipSong(),
    "CheckUSer": lambda bot , message: CheckUSer(message),
}
functions=[
    {
        "name" : "SkipSong",
        "description" : "Executes SkipSong",
        "parameters": {
            "type" : "object",
            "properties": {}
        },
    },
    {
        "name" : "CheckUSer",
        "description" : "Check if user is in a voice channel",
        "parameters": {
            "type" : "object",
            "properties": {}
        },
    }
]
class BotEvent():
    def __init__(self, msg,bot):
        self.msg = msg    
        self.bot = bot
    async def OpenaiApi(self):
        client = AsyncOpenAI(api_key=dotenv_values(".env")["OPENAI_API_KEY"],base_url=dotenv_values(".env")["OPENAI_BASE_URL"])
        res = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"user","content":f"skip song"}
            ],
            functions = functions,
            function_call="auto"
        )
        print(res)
        if  res.choices[0].message.function_call != None:
            function_call = res.choices[0].message.function_call
            function_name = function_call.name
            arguments = eval(function_call.arguments)
            print(function_call)
            # Dynamically call the corresponding Python function
            if function_name in function_mapping:
               await function_mapping[function_name](self.bot, self.msg)
            else:
                print(f"Function {function_name} is not implemented.")
