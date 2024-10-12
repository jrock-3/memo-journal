from google.cloud import speech
from dotenv import load_dotenv

import sys, os

def transcribe_gcs(gcs_uri: str) -> speech.RecognizeResponse:
    """Asynchronously transcribes the audio file from Cloud Storage
    Args:
        gcs_uri: The Google Cloud Storage path to an audio file.
            E.g., "gs://storage-bucket/file.flac".
    Returns:
        The generated transcript from the audio file provided.
    """
    client = speech.SpeechClient()

    audio = speech.RecognitionAudio(uri=f"gs://{os.getenv('GOOGLE_CLOUD_BUCKET_NAME')}/{gcs_uri}")
    config = speech.RecognitionConfig(
        language_code="en-US",
    )

    operation = client.long_running_recognize(config=config, audio=audio)

    response = operation.result(timeout=90)
    if response is None:
        raise Exception()

    return response

def main():
    load_dotenv()
    if len(sys.argv) != 2:
        raise Exception()

    res = transcribe_gcs(sys.argv[1])

    print("\n".join(result.alternatives[0].transcript for result in res.results))

if __name__ == "__main__":
    main()

