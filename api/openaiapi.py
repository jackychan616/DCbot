from openai import OpenAI,AsyncOpenAI
from dotenv import load_dotenv,dotenv_values
import re



class OpenAiApi():
    def __init__(self,Lang,style,req,artist):
        self.Lang = Lang
        self.style = style
        self.req = req
        self.artist = artist
    async def getSongList(self):
        client = AsyncOpenAI(api_key=dotenv_values(".env")["OPENAI_API_KEY"],base_url=dotenv_values(".env")["OPENAI_BASE_URL"])
        
        completion = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a bot that suject some song in Lang"},
            {"role": "user", "content": f"can you suject a json list of song of {self.Lang}, style of songs are {self.style},{self.req},{self.artist}, only json , key is title , artist and album"}
            ]
        )
        res = completion.choices[0].message.content
        res = res.replace("```json","")
        res = res.replace("```","")
        return eval(res)
    async def getUserCmd(self):
        
        pass
