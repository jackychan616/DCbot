import http.client

conn = http.client.HTTPSConnection("express-voic-text-to-speech.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "1e2925f06amsh1c54f80f0d68a34p145b2ajsn083f638e2ed6",
    'x-rapidapi-host': "express-voic-text-to-speech.p.rapidapi.com"
}

conn.request("GET", "/getAudioLink?service=StreamElements&voice=Chinese&text=This%20is%20a%20sample%20text%20that%20will%20be%20converted%20into%20audio.", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))