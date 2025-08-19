# tab5.py
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
    openai_api_key = os.getenv("OPENAI_API_KEY")
    grok_api_key = os.getenv('XAI_API_KEY')
    deepresearch_model = 'gpt-5'

    # Streamlit heading
    st.header("Tab 5 - Smartest Diagnosis")

    # Retrieve patient chart template
    patient_chart = retrieve_template(template_path="transcript.txt")

    # Build prompt
    regular_prompt = retrieve_prompt(
        prompt_path="kate_prompts/diagnoses.md"
    ).replace("{{CONVERSATION}}", patient_chart)

    # Call GPT-5
    st.write("### Running GPT-5 Smart Diagnosis...")
    start_time = time.time()
    with st.spinner("Processing GPT-5 output..."):
        dr_diagnosis = stream_grok(
            regular_prompt,
            api_key=grok_api_key,
        )
        print(dr_diagnosis)
    end_time = time.time()

    # Display results
    st.success(f"GPT-5 call completed in {end_time - start_time:.2f} seconds")
    st.write(dr_diagnosis)

if __name__ == "__main__":
    run()
