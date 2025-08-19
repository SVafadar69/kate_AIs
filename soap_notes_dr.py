# tab2.py
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
    openai_models = ['gpt-5']

    # Streamlit heading
    st.header("Tab 2 - Regular GPT-5 Diagnosis")

    # Retrieve patient chart template
    patient_chart = retrieve_template(
        template_path="transcript.txt"
    )

   # template
    soap_template = retrieve_template(template_path="SOAP Template Draft (For Revision).txt")

    # Build regular prompt
    regular_prompt = retrieve_prompt(
        prompt_path="kate_prompts/soap_notes.md"
    ).replace("{{CONVERSATION}}", patient_chart).replace("{{SOAP Template}}", soap_template)

    # Call GPT-5
    st.write("### Running GPT-5 Analysis...")
    start_time = time.time()
    with st.spinner("Processing GPT-5 output..."):
        regular_response = stream_grok(
            regular_prompt,
            api_key=grok_api_key,
        )
    end_time = time.time()

    # Display results
    st.success(f"GPT-5 call completed in {end_time - start_time:.2f} seconds")
    st.write(regular_response)

if __name__ == "__main__":
    run()


