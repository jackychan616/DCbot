from openai import OpenAI,AsyncOpenAI
from dotenv import dotenv_values
from models.music import Music

def CheckUSer(args):
    return True
function_mapping = {
    "SkipSong": lambda bot, message: Music(bot = bot,message=message).SkipSong(),
    "JoinVoiceChat": lambda bot,message: Music(bot=bot,message=message).JoinUserVC(),
    "PlaySong": lambda bot,message: Music(bot=bot,message=message).PlaySong(),
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
    },
    {
        "name": "JoinVoiceChat",
        "description": "Join Voice Chat",
        "parameters": {
            "type" : "object",
            "properties": {}
        }
    },
    {
        "name": "PlaySong",
        "description": "Play song that user wants or add the song to the playlist",
        "parameters": {
            "type" : "object",
            "properties": {
                "Song_name" : {
                    "type": "string",
                    "description": "The song that user required"
                }            
            },
            "required" : ["Songname"]
        }
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
        # Content to User not yet done
        print(res)
        if res.choices[0].message.function_call != None:
            function_call = res.choices[0].message.function_call
            function_name = function_call.name
            arguments = eval(function_call.arguments)
            print(function_call)
            # Dynamically call the corresponding Python function
            if function_name in function_mapping:
               await function_mapping[function_name](self.bot, self.msg)
            else:
                print(f"Function {function_name} is not implemented.")
