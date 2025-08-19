# tab6.py
import os
import time
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from helper_functions import retrieve_prompt, retrieve_template
from ai_models import call_gpt5, stream_grok    
from xai_sdk import Client
from xai_sdk.chat import user, system

def run():
    # Load environment variables
    load_dotenv()
    grok_api_key = os.getenv('XAI_API_KEY')

    # Streamlit heading
    st.header("Tab 6 - Deep Research Diagnosis")

    # Retrieve templates
    # Retrieve patient chart template
    conversation = retrieve_template(template_path="transcript.txt")

    # Build light prompt
    follow_up__prompt = retrieve_prompt(
        prompt_path="kate_prompts/follow_up.md"
    ).replace("{{CONVERSATION}}", conversation).replace("{{INSERT_NUMBER}}", "5")

    diagnoses__prompt = retrieve_prompt(prompt_path="kate_prompts/diagnoses.md").replace("{{CONVERSATION}}", conversation)

    # template
    soap_template = retrieve_template(template_path="SOAP Template Draft (For Revision).txt")

    # Build regular prompt
    soap_notes__prompt = retrieve_prompt(
        prompt_path="kate_prompts/soap_notes.md"
    ).replace("{{CONVERSATION}}", conversation).replace("{{SOAP Template}}", soap_template)

    # Deep Research Prompt
    treatment__prompt = retrieve_prompt(prompt_path="kate_prompts/treatment.md").replace("{{CONVERSATION}}", conversation)

    recommendations__prompt = retrieve_prompt(prompt_path="kate_prompts/recommendations.md").replace("{{CONVERSATION}}", conversation)

    all_in_one_prompt = retrieve_prompt(prompt_path="kate_prompts/all_in_one.md").replace("{{DIAGNOSIS__INSTRUCTIONS}}", diagnoses__prompt)\
        .replace("{{FOLLOW-UP__INSTRUCTIONS}}", follow_up__prompt).replace("{{SOAP__INSTRUCTIONS}}", soap_notes__prompt).replace("{{TREATMENT_PLAN__INSTRUCTIONS}}", \
            treatment__prompt).replace("{{RECOMMENDATIONS_PLAN__INSTRUCTIONS}}", recommendations__prompt).replace("{{CONVERSATION}}", conversation)

    print(f'All In One Prompt: {all_in_one_prompt}')

    # Call deep research model
    st.write("### Running o3-Deep-Research...")
    start_time = time.time()
    with st.spinner("Processing deep research..."):
        response = stream_grok(
            all_in_one_prompt,
            api_key=grok_api_key,
        )
    end_time = time.time()

    # Display results
    st.success(f"Deep research completed in {end_time - start_time:.2f} seconds")
    st.write(response)

if __name__ == "__main__":
    run()
