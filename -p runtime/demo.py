from transformers import pipeline

# load a small model so it runs on CPU
generator = pipeline("text-generation", model="gpt2")

prompt = "Skybase is waking up, and"
result = generator(prompt, max_length=50, num_return_sequences=1)

print("\n=== AI Output ===\n")
print(result[0]["generated_text"])

