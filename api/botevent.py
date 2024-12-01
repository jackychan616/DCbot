from openai import OpenAI,AsyncOpenAI
from dotenv import dotenv_values
from models.music import Music
from temp.user_message import user_message
def CheckUSer(args):
    return True
function_mapping = {
    "SkipSong": lambda bot, message,arguments: Music(bot = bot,message=message,arguments = arguments).SkipSong(),
    "JoinVoiceChat": lambda bot,message: Music(bot=bot,message=message).JoinUserVC(),
    "PlaySong": lambda bot,message,arguments: Music(bot=bot,message=message,arguments= arguments).PlaySong(),
    "PlayListOfSongs": lambda bot,message,arguments: Music(bot=bot,message=message,arguments= arguments).PlayListOfSongs(),
    "CheckUSer": lambda bot , message: CheckUSer(message),
}
def test():
    return "123"
tools=[
{
    "type": "function",
    "function": {
        "name" : "SkipSong",
        "description" : "Executes SkipSong,and reply user",
        "parameters": {
            "type" : "object",
            "properties": {
                "context" : {
                    "type" : "string",
                    "description" : "reply that you skipped the song"
                }
            }
        },
    },
},
{
    "type": "function",
    "function": {
        "name": "JoinVoiceChat",
        "description": "You self Join Voice Chat , tell them after joined",
        "parameters": {
            "type" : "object",
            "properties": {}
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "PlaySong",
        "description": "Play song that user wants or add the song to the playlist , and reply user",
        "parameters": {
            "type" : "object",
            "properties": {
                "Song_name" : {
                    "type": "string",
                    "description": "The song that user required"
                },
                "context" : {
                "type" : "string",
                "description" : "reply that you played that song"
                },            
            },
            "required" : ["Songname"]
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "PlayListOfSongs",
        "description": "add the list of songs that user wants or add the songs to the playlist , and reply user",
        "parameters": {
            "type" : "object",
            "properties": {
                "context" : {
                    "type" : "string",
                    "description" : "tell user what song you added"
                },
                "Song_list" : {
                    "type": "string",
                    "description": "json list of songs that user required"
                }
            },
            "required" : ["songs_properties"]
        }
    }
}
]

class BotEvent():
    def __init__(self, msg,bot,user_id,user_name):
        self.msg = msg    
        self.bot = bot
        self.user_id = user_id 
        self.user_name = user_name
        if user_id not in user_message:
            user_message[user_id] = [
                {"role": "system", "content": "You are a assistant. Provide helpful responses and call functions when necessary. The creator is Jacky Chan , discord id is Uncontrollable_Force"},
                {"role":"user","content":f"{self.msg.content}"}
            ]
        else:
            user_message[user_id].append({"role":"user","content":f"{self.msg.content}"})
    async def OpenaiApi(self):
        try:
            client = AsyncOpenAI(api_key=dotenv_values(".env")["OPENAI_API_KEY"],base_url=dotenv_values(".env")["OPENAI_BASE_URL"])
            res = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=user_message[self.user_id],
                tools=tools,
            ) 
            if res.choices[0].message.content != None:
                user_message[self.user_id].append({"role":"system","content":f"{res.choices[0].message.content}"})
            else:
                user_message[self.user_id].append({"role":"system","content":f"{res.choices[0].message.tool_calls}"})
                
            print(res)
            if res.choices[0].message.tool_calls != None:
                function_call = res.choices[0].message.tool_calls
                function_name = function_call[0].function.name
                arguments = eval(function_call[0].function.arguments)
                await self.msg.reply(f"ok ! {self.msg.author.name}")
                # Dynamically call the corresponding Python function
                if function_name in function_mapping and arguments == {}:
                    await function_mapping[function_name](self.bot, self.msg)
                else:
                    await function_mapping[function_name](self.bot, self.msg ,arguments)
                    if "context" in arguments:
                        await self.msg.reply(arguments["context"])
            else:
                    content = res.choices[0].message.content
                    if len(content) <= 2000:
                        await self.msg.reply(content)
                    else:
                        # Split the content into chunks of 2000 characters
                        chunks = [content[i:i+2000] for i in range(0, len(content), 2000)]
                        for chunk in chunks:
                            await self.msg.reply(chunk)
        except Exception as e:
            await self.msg.reply(f"Error: {e}")
            print(e)
            return
                


