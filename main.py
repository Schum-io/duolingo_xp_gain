import time
import random
import base64
import json
import requests
from datetime import datetime
from pydantic import BaseSettings


class Config(BaseSettings):
    """All variables in this class are system environment variables."""

    jwt_token: str = "copy your jwt_token here"
    """
    While logged in, open the browser's console F12 -> Application -> Cookies -> https://www.duolingo.com -> jwt_token
    than create a new environment variable named JWT_TOKEN and paste the value or replace the value in this class with the new one
    """


CONFIG = Config()

LESSONS_COUNT: int = 10
"""How many lessons to complete."""

PAUSE_RANGE_BETWEEN_LESSONS_SEC: tuple[int, int] = (100, 180)
"""Pauses between lessons are generated randomly within the specified range in seconds."""


def _pause_between_lessons():
    # Generate a random duration within the specified range
    pause_time = random.randint(*PAUSE_RANGE_BETWEEN_LESSONS_SEC)
    print(f"Pausing for {pause_time} seconds...")
    time.sleep(pause_time)


def gain_xp():
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CONFIG.jwt_token}",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
    }

    # Decode JWT and extract 'sub'
    decoded_jwt = base64.b64decode(CONFIG.jwt_token.split(".")[1] + "==").decode("utf-8")
    sub = json.loads(decoded_jwt)["sub"]

    # Fetch user information
    response = requests.get(
        f"https://www.duolingo.com/2017-06-30/users/{sub}?fields=fromLanguage,learningLanguage,xpGains", headers=headers
    )
    user_info = response.json()
    from_language = user_info["fromLanguage"]
    learning_language = user_info["learningLanguage"]
    xp_gains = iter(user_info["xpGains"])
    xp_gains_exists = []

    # Iterate through lessons
    for i in range(int(LESSONS_COUNT)):
        # Start a new session
        skill_id = next(
            xpGain for xpGain in xp_gains if xpGain.get("skillId") and xpGain.get("skillId") not in xp_gains_exists
        )["skillId"]
        session_response = requests.post(
            "https://www.duolingo.com/2017-06-30/sessions",
            headers=headers,
            json={
                "challengeTypes": [
                    "assist",
                    "characterIntro",
                    "characterMatch",
                    "characterPuzzle",
                    "characterSelect",
                    "characterTrace",
                    "completeReverseTranslation",
                    "definition",
                    "dialogue",
                    "form",
                    "freeResponse",
                    "gapFill",
                    "judge",
                    "listen",
                    "listenComplete",
                    "listenMatch",
                    "match",
                    "name",
                    "listenComprehension",
                    "listenIsolation",
                    "listenTap",
                    "partialListen",
                    "partialReverseTranslate",
                    "readComprehension",
                    "select",
                    "selectPronunciation",
                    "selectTranscription",
                    "syllableTap",
                    "syllableListenTap",
                    "speak",
                    "tapCloze",
                    "tapClozeTable",
                    "tapComplete",
                    "tapCompleteTable",
                    "tapDescribe",
                    "translate",
                    "typeCloze",
                    "typeClozeTable",
                    "typeCompleteTable",
                ],
                "fromLanguage": from_language,
                "isFinalLevel": False,
                "isV2": True,
                "juicy": True,
                "learningLanguage": learning_language,
                "skillId": skill_id,
                "smartTipsVersion": 2,
                "type": "SPEAKING_PRACTICE",
            },
        ).json()

        # Update the session
        current_time = datetime.now()
        update_response = requests.put(
            f"https://www.duolingo.com/2017-06-30/sessions/{session_response['id']}",
            headers=headers,
            json={
                **session_response,
                "heartsLeft": 0,
                "startTime": (current_time.timestamp() - 60),
                "enableBonusPoints": False,
                "endTime": current_time.timestamp(),
                "failed": False,
                "maxInLessonStreak": 9,
                "shouldLearnThings": True,
            },
        ).json()

        # Print the xp gain
        print(f'xp: {update_response["xpGain"]} for skill_id: {skill_id}')
        xp_gains_exists.append(skill_id)
        _pause_between_lessons()


if __name__ == "__main__":
    gain_xp()
