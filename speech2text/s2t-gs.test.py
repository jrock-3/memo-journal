from google.cloud import speech
from dotenv import load_dotenv

import sys, os

def transcribe_gcs(gcs_uri: str) -> str:
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

    print("Waiting for operation to complete...")
    response = operation.result(timeout=90)
    if response is None:
        raise Exception()

    transcript_builder = []
    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    for result in response.results:
        # The first alternative is the most likely one for this portion.
        transcript_builder.append(f"\nTranscript: {result.alternatives[0].transcript}")
        transcript_builder.append(f"\nConfidence: {result.alternatives[0].confidence}")

    transcript = "".join(transcript_builder)
    print(transcript)

    return transcript

def main():
    load_dotenv()
    if not (len(sys.argv) == 3 and os.path.isfile(sys.argv[1])):
        raise Exception()

    res = transcribe_gcs(sys.argv[1])

    with open(sys.argv[2], "w") as outfile:
        outfile.write(repr(res))

if __name__ == "__main__":
    main()

