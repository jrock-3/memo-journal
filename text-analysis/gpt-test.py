from openai import OpenAI
from openai.types.chat import ChatCompletion
from dotenv import load_dotenv

import os, sys

def quickstart_test(content: str) -> ChatCompletion:
    client = OpenAI(project=os.getenv("OPENAI_API_PROJECT_ID"))

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": str(os.getenv("OPENAI_API_ROLE_DESCRIPTION"))
            },
            {
                "role": "user",
                "content": content
            }
        ]
    )

    return completion

def main():
    if not (len(sys.argv) == 2 and os.path.isfile(sys.argv[1])):
        raise Exception()

    load_dotenv()

    with open(sys.argv[1], "r") as infile:
        res = quickstart_test("\n".join(infile.readlines()))
        print(res.choices[0].message.content)

if __name__ == "__main__":
    main()
