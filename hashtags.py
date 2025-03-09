from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import re


class generate_metadata:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen1.5-0.5B")
        self.model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen1.5-0.5B")
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

    def generate_hashtags(self, sentence):
        prompt = (f"Generate at least 10 diverse, relevant, and trending hashtags based on the tone, emotion, and context "
                f"of the following sentence: '{sentence}'\nHashtags:")
        inputs = self.tokenizer(prompt, return_tensors="pt", padding=True, truncation=True).to(self.device)
        with torch.no_grad():
            output = self.model.generate(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_new_tokens=50,  # Reduced for speed
                num_return_sequences=1,
                temperature=0.7,  # Lower for faster convergence
                top_k=20,  # Reduced sampling space
                top_p=0.8,  # More focused sampling
                pad_token_id=self.tokenizer.eos_token_id,
                do_sample=True
            )
        generated_text = self.tokenizer.decode(output[0], skip_special_tokens=True)
        hashtags = list(set(re.findall(r'#[\w]+', generated_text)))
        return ' '.join(hashtags[:10])


# # Example usage
# sentence = "Artificial intelligence is transforming the world."
# gm = generate_metadata()
# hashtags = gm.generate_hashtags(sentence)
# print(hashtags)