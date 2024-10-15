import re, os, sys

from google.cloud import storage
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech

from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
RECOGNIZER_ID = os.getenv("GOOGLE_CLOUD_RECOGNIZER_ID")
BUCKET_NAME = os.getenv("GOOGLE_CLOUD_BUCKET_NAME")

def transcribe_batch_gcs_input_gcs_output_v2(
    audio_uri: str,
    gcs_output_path: str,
) -> cloud_speech.BatchRecognizeResults:
    """Transcribes audio from a Google Cloud Storage URI using the Google Cloud Speech-to-Text API.
    The transcription results are stored in another Google Cloud Storage bucket.
    Args:
        audio_uri (str): The Google Cloud Storage URI of the input audio file.
            E.g., gs://[BUCKET]/[FILE]
        gcs_output_path (str): The Google Cloud Storage bucket URI where the output transcript will be stored.
            E.g., gs://[BUCKET]
    Returns:
        cloud_speech.BatchRecognizeResults: The response containing the URI of the transcription results.
    """
    # Instantiates a client
    client = SpeechClient()

    config = cloud_speech.RecognitionConfig(
        auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
        language_codes=["en-US"],
        model="long",
    )

    file_metadata = cloud_speech.BatchRecognizeFileMetadata(uri=audio_uri)

    request = cloud_speech.BatchRecognizeRequest(
        recognizer=f"projects/{PROJECT_ID}/locations/global/recognizers/{RECOGNIZER_ID}",
        config=config,
        files=[file_metadata],
        recognition_output_config=cloud_speech.RecognitionOutputConfig(
            gcs_output_config=cloud_speech.GcsOutputConfig(
                uri=gcs_output_path,
            ),
        ),
    )

    # Transcribes the audio into text
    operation = client.batch_recognize(request=request)

    # print("Waiting for operation to complete...")
    response = operation.result(timeout=600)

    file_results = response.results[audio_uri]

    # print(f"Operation finished. Fetching results from {file_results.uri}...")
    output_bucket, output_object = re.match(
        r"gs://([^/]+)/(.*)", file_results.uri
    ).group(1, 2)

    # Instantiates a Cloud Storage client
    storage_client = storage.Client()

    # Fetch results from Cloud Storage
    bucket = storage_client.bucket(output_bucket)
    blob = bucket.blob(output_object)
    results_bytes = blob.download_as_bytes()
    batch_recognize_results = cloud_speech.BatchRecognizeResults.from_json(
        results_bytes, ignore_unknown_fields=True
    )

    # for result in batch_recognize_results.results:
    #     print(f"Transcript: {result.alternatives[0].transcript}")
    #
    return batch_recognize_results

def main():
    if len(sys.argv) != 2:
        raise Exception()

    res = transcribe_batch_gcs_input_gcs_output_v2(f"gs://{BUCKET_NAME}/{sys.argv[1]}", f"gs://{BUCKET_NAME}")

    # for result in res.results:
    #     print(result.alternatives[0].transcript)

    print("\n".join(str(result.alternatives[0].transcript) for result in res.results if len(result.alternatives)))

if __name__ == "__main__":
    main()

