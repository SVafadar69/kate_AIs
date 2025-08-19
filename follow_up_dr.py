# tab4.py
import os
import time
import streamlit as st
from dotenv import load_dotenv
from ai_models import call_gpt5, stream_grok    
from xai_sdk import Client
from xai_sdk.chat import user, system   
from helper_functions import retrieve_prompt, retrieve_template

def run():
    # Load environment variables
    load_dotenv()
    grok_api_key = os.getenv('XAI_API_KEY')

    # Streamlit heading
    st.header("Tab 4 - Follow-Up (15)")

    # Retrieve patient chart template
    conversation = retrieve_template(template_path="transcript.txt")

    # Build light prompt
    light_prompt = retrieve_prompt(
        prompt_path="kate_prompts/follow_up.md"
    ).replace("{{CONVERSATION}}", conversation).replace("{{INSERT_NUMBER}}", "15")

    # Call GPT-5
    st.write("### Running GPT-5 Analysis...")
    start_time = time.time()
    with st.spinner("Processing GPT-5 output..."):
        regular_response = stream_grok(
            light_prompt,
            api_key=grok_api_key,
        )
        print(regular_response)
    end_time = time.time()

    # Display results
    st.success(f"GPT-5 call completed in {end_time - start_time:.2f} seconds")
    st.write(regular_response)

if __name__ == "__main__":
    run()
