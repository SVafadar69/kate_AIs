# tab6.py
import os
import time
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from helper_functions import retrieve_prompt, retrieve_template
from ai_models import stream_grok
def run():
    # Load environment variables
    load_dotenv()
    grok_api_key = os.getenv("XAI_API_KEY")

    # Streamlit heading
    st.header("Tab 6 - Deep Research Diagnosis")

    # Retrieve templates
    # Retrieve patient chart template
    conversation = retrieve_template(template_path="transcript.txt")

    # Build light prompt
    follow_up_dr_prompt = retrieve_prompt(
        prompt_path="kate_prompts/follow_up.md"
    ).replace("{{CONVERSATION}}", conversation).replace("{{INSERT_NUMBER}}", "15")

    diagnoses_dr_prompt = retrieve_prompt(prompt_path="kate_prompts/diagnoses_dr.md").replace("{{CONVERSATION}}", conversation)

    # template
    soap_template = retrieve_template(template_path="SOAP Template Draft (For Revision).txt")

    # Build regular prompt
    soap_notes_dr_prompt = retrieve_prompt(
        prompt_path="kate_prompts/soap_notes.md"
    ).replace("{{CONVERSATION}}", conversation).replace("{{SOAP Template}}", soap_template)

    # Deep Research Prompt
    treatment_dr_prompt = retrieve_prompt(prompt_path="kate_prompts/treatment_dr.md").replace("{{CONVERSATION}}", conversation)

    recommendations_dr_prompt = retrieve_prompt(prompt_path="kate_prompts/recommendations_dr.md").replace("{{CONVERSATION}}", conversation)

    all_in_one_prompt = retrieve_prompt(prompt_path="kate_prompts/all_in_one_dr.md").replace("{{DIAGNOSIS_DR_INSTRUCTIONS}}", diagnoses_dr_prompt)\
        .replace("{{FOLLOW-UP_DR_INSTRUCTIONS}}", follow_up_dr_prompt).replace("{{SOAP_DR_INSTRUCTIONS}}", soap_notes_dr_prompt).replace("{{TREATMENT_PLAN_DR_INSTRUCTIONS}}", \
            treatment_dr_prompt).replace("{{RECOMMENDATIONS_PLAN_DR_INSTRUCTIONS}}", recommendations_dr_prompt).replace("{{CONVERSATION}}", conversation)

    print(f'All In One Prompt: {all_in_one_prompt}')

    # Call deep research model
    st.write("### Running Deep-Research...")
    start_time = time.time()
    with st.spinner("Processing deep research..."):
        response = stream_grok(prompt = all_in_one_prompt,api_key=grok_api_key, model="grok-4-0709")
        # response = client.responses.create(
        #     model="o3-deep-research",
        #     input=all_in_one_prompt,
        #     background=True,
        #     tools=[
        #         {"type": "web_search_preview"},
        #         {
        #             "type": "file_search",
        #             "vector_store_ids": [
        #                 "vs_68870b8868b88191894165101435eef6",
        #                 "vs_12345abcde6789fghijk101112131415"
        #             ]
        #         },
        #         {
        #             "type": "code_interpreter",
        #             "container": {"type": "auto"}
        #         },
        #     ],
        # )
        # response.output_text
    end_time = time.time()

    # Display results
    st.success(f"Deep research completed in {end_time - start_time:.2f} seconds")
    st.write(response)

if __name__ == "__main__":
    run()
