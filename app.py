import os
import speech_recognition as sr
from flask import Flask, render_template, request
from transformers import RagTokenizer, RagRetriever, RagTokenForGeneration
from gtts import gTTS
import pandas as pd


# Load preprocessed CSV data
urdu_df = pd.read_csv('preprocessed_dataset.csv')

# Load RAG model
tokenizer = RagTokenizer.from_pretrained("facebook/rag-token-nq")
retriever = RagRetriever.from_pretrained("facebook/rag-token-nq", index_name="exact", use_dummy_dataset=True)
model = RagTokenForGeneration.from_pretrained("facebook/rag-token-nq", retriever=retriever)

# Flask app
app = Flask(__name__)

# Function to retrieve information using RAG
# Function to retrieve information using RAG
def retrieve_information(query):
    inputs = tokenizer(query, return_tensors="pt")
    question_outputs = model.question_encoder(**inputs)
    
    # Access the pooler_output from the last layer
    question_hidden_states = question_outputs.last_hidden_state[:, 0, :]
    
    retriever_outputs = retriever(
        input_ids=inputs["input_ids"],
        attention_mask=inputs["attention_mask"],
        question_hidden_states=question_hidden_states,
        return_tensors="pt"
    )

    doc_scores = retriever_outputs['doc_scores']
    top_doc_indices = doc_scores.argsort(dim=1, descending=True)[:, :3]  # Top 3 documents
    retrieved_documents = urdu_df.loc[top_doc_indices[0]]['story_content'].tolist()
    
    return retrieved_documents


# Function to generate response using RAG
def generate_response(user_input):
    retrieved_info = retrieve_information(user_input)
    return retrieved_info[0]  # For simplicity, returning the first retrieved document as the response


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    user_input = request.form['user_input']
    
    # Use STT to convert speech to text if user_input is 'SpeechInput'
    if user_input == 'SpeechInput':
        # Modify this section to use your STT model for speech recognition
        # Example using the simplified STT with SpeechRecognition library:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Speak something:")
            audio = recognizer.listen(source)

        try:
            user_input = recognizer.recognize_google(audio, language="ur-PK")
        except sr.UnknownValueError:
            user_input = "Sorry, I couldn't understand the speech."

    response = generate_response(user_input)
    
    if response:
        tts = gTTS(text=response, lang='ur')
        tts.save("output.mp3")
        os.system("start output.mp3")

    return render_template('index.html', user_input=user_input, response=response)

def recognize_speech(audio_file):
    recognizer = sr.Recognizer()
    audio_text = ""
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
        try:
            audio_text = recognizer.recognize_google(audio, language="ur-PK")
        except sr.UnknownValueError:
            audio_text = "Sorry, I couldn't understand the speech."
    return audio_text

if __name__ == '__main__':
    app.run(debug=True, port=5001)
