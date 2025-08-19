# tab6.py
import os
import time
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from helper_functions import retrieve_prompt, retrieve_template

def run():
    # Load environment variables
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")

    # Streamlit heading
    st.header("Tab 6 - Deep Research Diagnosis")

    # Retrieve templates
    patient_chart = retrieve_template(template_path="transcript.txt")
    dr_prompt = retrieve_prompt(prompt_path="kate_prompts/diagnoses_dr.md").replace("{{CONVERSATION}}", patient_chart)

    # Initialize client
    client = OpenAI(api_key=openai_api_key)

    # Call deep research model
    st.write("### Running o3-Deep-Research...")
    start_time = time.time()
    with st.spinner("Processing deep research..."):
        response = client.responses.create(
            model="o3-deep-research",
            input=dr_prompt,
            background=True,
            tools=[
                {"type": "web_search_preview"},
                {
                    "type": "file_search",
                    "vector_store_ids": [
                        "vs_68870b8868b88191894165101435eef6",
                        "vs_12345abcde6789fghijk101112131415"
                    ]
                },
                {
                    "type": "code_interpreter",
                    "container": {"type": "auto"}
                },
            ],
        )
    end_time = time.time()

    # Display results
    st.success(f"Deep research completed in {end_time - start_time:.2f} seconds")
    st.write(response)

if __name__ == "__main__":
    run()
