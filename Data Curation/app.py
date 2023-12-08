import pandas as pd
import re
from langdetect import detect
import string

def clean_urdu_text(text):
    # Remove punctuations specific to Urdu
    urdu_punctuations = "،؛_()[\]{!۔''./""‘’؟"
    text = text.translate(str.maketrans("", "", urdu_punctuations))

    # Remove numeric digits
    text = re.sub(r'\d', '', text)

    # Remove extra whitespaces
    text = re.sub(r'\s+', ' ', text).strip()

    return text

def preprocess_urdu_text(text):
    # Skip language detection for very short texts
    if len(text) < 5:
        return text

    try:
        lang = detect(text)
        if lang == 'ur':
            text = clean_urdu_text(text)
    except Exception as e:
        print(f"Error during language detection: {e}")

    return text

def preprocess_dataset(dataset_path, text_column_name):
    df = pd.read_csv(dataset_path)
    if text_column_name not in df.columns:
        raise KeyError(f"The specified text column '{text_column_name}' does not exist in the dataset.")
    df = df.dropna(subset=[text_column_name])
    df = df.drop_duplicates()
    df[text_column_name] = df[text_column_name].apply(preprocess_urdu_text)
    df['tokenized_text'] = df[text_column_name].apply(lambda x: x.split())
    df.to_csv('preprocessed_dataset.csv', index=False)

if __name__ == "__main__":
    dataset_path = 'urdu_stories.csv'
    text_column_name = 'story_content'
    preprocess_dataset(dataset_path, text_column_name)
