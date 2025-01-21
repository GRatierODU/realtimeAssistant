from RealtimeSTT import AudioToTextRecorder
from boto3 import client
import litellm
import os
import io
from pydub import AudioSegment
from pydub.playback import play


litellm._logging._disable_debugging()
chat_history = []


def process_text(text):
    global chat_history
    recorder.stop()
    context = chat_history[-10:]
    context.append({"content": text, "role": "user"})

    response = litellm.completion(
        model="bedrock/us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        messages=context,
    )
    chat_history.append({"content": text, "role": "user"})
    chat_history.append(
        {"content": response.choices[0].message.content, "role": "assistant"}
    )
    print(
        "\n\n---------------\n"
        + response.choices[0].message.content
        + "\n---------------\n"
    )
    aws_polly_tts(response.choices[0].message.content)


def aws_polly_tts(text):
    polly = client("polly", region_name="us-east-1")

    response = polly.synthesize_speech(Text=text, OutputFormat="mp3", VoiceId="Matthew")

    stream = response.get("AudioStream")
    audio = AudioSegment.from_file(io.BytesIO(stream.read()), format="mp3")
    play(audio)


if __name__ == "__main__":
    print("Wait until it says 'speak now'")
    recorder = AudioToTextRecorder(model="medium")

    while True:
        user_text = recorder.text()
        process_text(user_text)
