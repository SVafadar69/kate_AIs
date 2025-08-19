# tab3.py
import os
import time
import streamlit as st
from dotenv import load_dotenv
from ai_models import stream_llama
from helper_functions import retrieve_prompt, retrieve_template

def run():
    # Load environment variables
    load_dotenv()
    groq_api_key = os.getenv("GROQ_API_KEY")
    openai_models = ['openai/gpt-oss-20b', 'gpt-5']

    # Streamlit heading
    st.header("Tab 3 - Light Follow-Up")

    # Retrieve patient chart template
    conversation = retrieve_template(template_path="transcript.txt")

    # Build light prompt
    light_prompt = retrieve_prompt(
        prompt_path="kate_prompts/follow_up.md"
    ).replace("{{CONVERSATION}}", conversation).replace("{{INSERT_NUMBER}}", "5")

    # Call model
    st.write("### Running Light Analysis...")
    start_time = time.time()
    with st.spinner("Processing GPT output..."):
        regular_response = stream_llama(
            light_prompt,
            api_key=groq_api_key,
            model=openai_models[0]
        )
        print(regular_response)
    end_time = time.time()

    # Display results
    st.success(f"Light model call completed in {end_time - start_time:.2f} seconds")
    st.write(regular_response)

if __name__ == "__main__":
    run()
