import os
import time
import streamlit as st
from dotenv import load_dotenv
from helper_functions import retrieve_prompt, retrieve_template
from ai_models import stream_grok
def run():
    load_dotenv()

    grok_api_key = os.getenv("XAI_API_KEY")

    # Patient chart 
    patient_chart = retrieve_template(template_path="transcript.txt")

    # Deep Research Prompt
    dr_prompt = retrieve_prompt(prompt_path="kate_prompts/treatment_dr.md").replace("{{PATIENT_CHART}}", patient_chart)

    start_time = time.time()
    print(f'API HIT')
    response = stream_grok(prompt = dr_prompt, model="grok-4-0709", api_key=grok_api_key)
    end_time = time.time()
    print(f'Time Taken: {end_time - start_time}')
    st.success(f"GPT-5 call completed in {end_time - start_time:.2f} seconds")
    st.write(response)

if __name__ == "__main__":
    run()

