import langid


async def getLangCode(text):
    language, confidence = langid.classify(text)
    return language
    