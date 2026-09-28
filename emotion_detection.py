"""Emotion detection module using the Watson NLP EmotionPredict service."""
import json
import os
import requests

URL = ('https://sn-watson-emotion.labs.skills.network/v1/'
       'watson.runtime.nlp.v1/NlpService/EmotionPredict')
HEADERS = {"grpc-metadata-mm-model-id": "emotion_aggregated-workflow_lang_en_stock"}
NULL_RESULT = {
    'anger': None, 'disgust': None, 'fear': None,
    'joy': None, 'sadness': None, 'dominant_emotion': None
}


def _mock_response(text):
    """Offline stand-in for Watson, for local development only."""
    keywords = {
        'joy': ('love', 'happy', 'glad'),
        'anger': ('mad', 'angry', 'hate'),
        'disgust': ('disgust',),
        'sadness': ('sad',),
        'fear': ('afraid', 'scared', 'fear'),
    }
    scores = {emotion: 0.01 for emotion in keywords}
    for emotion, words in keywords.items():
        if any(word in text.lower() for word in words):
            scores[emotion] = 0.95
    return {'emotionPredictions': [{'emotion': scores}]}


def emotion_detector(text_to_analyze):
    """Return emotion scores and the dominant emotion; None values on a 400 error."""
    if not text_to_analyze or not text_to_analyze.strip():
        return dict(NULL_RESULT)

    if os.environ.get('EMOTION_MOCK') == '1':
        formatted = _mock_response(text_to_analyze)
    else:
        payload = {"raw_document": {"text": text_to_analyze}}
        response = requests.post(URL, json=payload, headers=HEADERS, timeout=10)
        if response.status_code == 400:
            return dict(NULL_RESULT)
        formatted = json.loads(response.text)

    emotions = formatted['emotionPredictions'][0]['emotion']
    return {
        'anger': emotions['anger'],
        'disgust': emotions['disgust'],
        'fear': emotions['fear'],
        'joy': emotions['joy'],
        'sadness': emotions['sadness'],
        'dominant_emotion': max(emotions, key=emotions.get)
    }