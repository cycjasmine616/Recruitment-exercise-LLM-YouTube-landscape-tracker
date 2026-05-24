import os
from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer
from sentence_transformers import SentenceTransformer
import torch

def download_models():
    print("Downloading Hugging Face models...")
    print("This may take some time on first run (models are cached after download)")
    
    model_dir = "./models"
    os.makedirs(model_dir, exist_ok=True)
    
    print("\n1/4 Downloading summarization model (facebook/bart-large-cnn)...")
    try:
        summarizer = pipeline(
            "summarization",
            model="facebook/bart-large-cnn",
            cache_dir=model_dir
        )
        print("✓ Summarization model downloaded")
    except Exception as e:
        print(f"⚠ Could not download BART: {e}")
        print("Downloading smaller summarization model...")
        try:
            summarizer = pipeline(
                "summarization",
                model="google/pegasus-xsum",
                cache_dir=model_dir
            )
            print("✓ Smaller summarization model downloaded")
        except Exception as e2:
            print(f"⚠ Could not download any summarization model: {e2}")
    
    print("\n2/4 Downloading classification model (facebook/bart-large-mnli)...")
    try:
        classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            cache_dir=model_dir
        )
        print("✓ Classification model downloaded")
    except Exception as e:
        print(f"⚠ Could not download BART-MNLI: {e}")
        print("Downloading smaller classification model...")
        try:
            classifier = pipeline(
                "zero-shot-classification",
                model="MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli",
                cache_dir=model_dir
            )
            print("✓ Smaller classification model downloaded")
        except Exception as e2:
            print(f"⚠ Could not download any classification model: {e2}")
    
    print("\n3/4 Downloading sentence transformer (all-MiniLM-L6-v2)...")
    try:
        model = SentenceTransformer(
            'all-MiniLM-L6-v2',
            cache_folder=model_dir
        )
        print("✓ Sentence transformer downloaded")
    except Exception as e:
        print(f"⚠ Could not download sentence transformer: {e}")
    
    print("\n4/4 Testing models...")
    try:
        test_text = "Large language models have revolutionized artificial intelligence."
        test_summary = summarizer(test_text, max_length=30, min_length=5)
        print(f"✓ Models working! Test summary: {test_summary[0]['summary_text'][:100]}...")
    except Exception as e:
        print(f"⚠ Model test failed: {e}")
        print("Models may still work when enough memory is available")
    
    print(f"\n✅ Model download complete! Models cached in: {os.path.abspath(model_dir)}")
    print("You can now run the main application.")

if __name__ == "__main__":
    download_models()
