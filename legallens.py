import PyPDF2
import docx
import openai
import streamlit as st
import re

# Set OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["key_openai"]


# Define Streamlit app title and sidebar content
st.set_page_config(page_title="Legal Lens")
st.sidebar.markdown("# Configs")
output_lang = st.sidebar.radio("Output Language:", ["English", "Spanish", "Portuguese"])
st.sidebar.markdown("# About")
st.sidebar.markdown("Legal Lens is a mini-app that utilizes AI to analyze legal documents and offer insights.")
st.sidebar.markdown("Made by [Gustavo Matos](https://www.linkedin.com/in/gfmatos/)")

# Define function to generate a response using OpenAI GPT-3 API
def generate_response(prompt):
    completions = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1624,
        n=1,
        stop=None,
        temperature=0.5,
    )
    message = completions.choices[0].text
    return message

def read_file(uploaded_file):
    if uploaded_file.name.endswith('.pdf'):
        pdf_file = uploaded_file
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        content = ''
        for page in range(len(pdf_reader.pages)):
            content += pdf_reader.pages[page].extract_text()
        pdf_file.close()
    elif uploaded_file.name.endswith('.docx'):
        doc_file = docx.Document(uploaded_file)
        content = ''
        for paragraph in doc_file.paragraphs:
            content += paragraph.text
    else:
        raise Exception('File type not supported')

    # split the content into sentences
    sentences = re.findall(r'(?s)\s*([A-Z].*?(?:\.|\?|!))(?=\s*[A-Z]|\Z)', content)
    
    # join sentences until the length of the string exceeds the chunk size
    chunk_size = 4000
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += sentence
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def get_input():
    uploaded_file = st.file_uploader("Upload a file")
    if uploaded_file is not None:
        input_text = read_file(uploaded_file)
    else:
        input_text = None
    return input_text

# Define Streamlit app content
def main():
    st.title("Legal Lens")
    user_input = get_input()
    if st.button("Craft!"):
        with st.spinner('Crafting...'):
            st.write(user_input)

if __name__ == "__main__":
    main()
