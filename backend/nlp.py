from textblob import TextBlob

def analyze_sentiment(text: str) -> tuple:
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity

    if polarity > 0.2:
        return "Pozitif", polarity
    elif polarity < -0.2:
        return "Negatif", polarity
    else:
        return "Nötr", polarity
