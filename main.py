# main.py

from dotenv import load_dotenv
import os

# Unset GOOGLE_APPLICATION_CREDENTIALS if it exists to prevent conflict with API Key auth
if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
    del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]

from crew import run_with_fallback

load_dotenv()

def run(user_input: str):
    result = run_with_fallback(inputs={"user_input": user_input})

    print("-"*50)
    print(result)
    print("-" * 50)

if __name__ == "__main__":
    user_input = (
        "A man broke into my house at night while my family was sleeping. "
        "He stole jewelry and cash from our bedroom. When I confronted him, "
        "he threatened me with a knife and ran away. We reported it to the police, "
        "but I'm not sure which legal charges should be filed under IPC."
    )

    run(user_input)
