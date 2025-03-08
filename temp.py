import requests
from transformers import LlamaForCausalLM, LlamaTokenizer
from transformers import AutoModelForCausalLM, AutoTokenizer

from huggingface_hub import login
from PIL import Image, ImageDraw, ImageFont
from instagrapi import Client
import pdb


# Get a quote from ZenQuotes API
def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    if response.status_code == 200:
        quote_data = response.json()
        quote = quote_data[0]["q"]
        author = quote_data[0]["a"]
        return f"{quote} - {author}"
    else:
        return "Could not fetch quote."

# Generate Instagram caption with viral hashtags
def generate_caption(quote):
    pdb.set_trace()
    model_name = "meta-llama/Llama-3.2-1B"
    tokenizer = AutoTokenizer.from_pretrained(model_name, legacy=False)
    model = AutoModelForCausalLM.from_pretrained(model_name)

    prompt = f"Create a viral Instagram caption for the quote: \"{quote}\" with popular hashtags"
    inputs = tokenizer(prompt, return_tensors="pt")

    outputs = model.generate(**inputs, max_length=100, num_return_sequences=1)
    caption = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return caption

# Wrap text for better fit
def wrap_text(draw, text, font, max_width):
    lines = []
    words = text.split()
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        bbox = draw.textbbox((0, 0), test_line, font=font)
        width = bbox[2] - bbox[0]
        if width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines

# Create a high-quality image with dynamically scaled text for the quote
def create_image(quote):
    img = Image.new('RGB', (1080, 1920), color='black')
    draw = ImageDraw.Draw(img)

    # Start with a reasonably large font size
    font_size = 60
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", font_size)
    except:
        font = ImageFont.load_default()

    # Wrap text and adjust font size
    max_width = img.width * 0.9
    lines = wrap_text(draw, quote, font, max_width)

    # Calculate total text height with increased line spacing
    line_height = draw.textbbox((0, 0), "A", font=font)[3] - draw.textbbox((0, 0), "A", font=font)[1]
    line_spacing = 10  # Added extra spacing between lines
    total_height = (line_height + line_spacing) * len(lines)

    # Scale text size within reasonable bounds
    while total_height < img.height * 0.4 and font_size < 150:
        font_size += 5
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", font_size)
        except:
            font = ImageFont.load_default()
        lines = wrap_text(draw, quote, font, max_width)
        line_height = draw.textbbox((0, 0), "A", font=font)[3] - draw.textbbox((0, 0), "A", font=font)[1]
        total_height = (line_height + line_spacing) * len(lines)

    while total_height > img.height * 0.8 and font_size > 30:
        font_size -= 5
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", font_size)
        except:
            font = ImageFont.load_default()
        lines = wrap_text(draw, quote, font, max_width)
        line_height = draw.textbbox((0, 0), "A", font=font)[3] - draw.textbbox((0, 0), "A", font=font)[1]
        total_height = (line_height + line_spacing) * len(lines)

    # Center text vertically
    y = (img.height - total_height) // 2

    # Draw each line with extra spacing
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (img.width - text_width) // 2
        draw.text((x, y), line, font=font, fill='white')
        y += line_height + line_spacing

    img.save("quote_post.jpg", quality=95)

# Handle Instagram security challenge
def handle_security_challenge(cl):
    challenge = cl.challenge_resolve(cl.last_json.get('challenge', {}).get('url'))
    if challenge == "select_verify_method":
        cl.challenge_select_verify_method(1)  # Usually 1 = email, 0 = phone
        code = input("Enter the confirmation code sent to your email: ")
        cl.challenge_send_code(code)

# Post image to Instagram story and feed
def post_to_instagram(username, password, image_path):
    cl = Client()
    try:
        cl.login(username, password)
    except Exception as e:
        if "challenge_required" in str(e):
            handle_security_challenge(cl)
        else:
            print(f"Login failed: {e}")
            return

    try:
        cl.photo_upload(image_path, caption="Check out this quote!")
        cl.photo_upload_to_story(image_path)
        print("Image posted to Instagram story and feed!")
    except Exception as e:
        print(f"Failed to post image: {e}")

# Create the Instagram post
if __name__ == "__main__":
    login(token='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')
    quote = get_quote()
    print(f"Quote: {quote}")

    if "Could not fetch" not in quote:
        caption = '#inspiration, #dailyquote, #inspire' #generate_caption(quote)
        print("\nInstagram Caption:\n")
        print(caption)
        create_image(quote)
        print("\nImage saved as 'quote_post.jpg'")
        post_to_instagram("dailyquote785", , "quote_post.jpg")
    else:
        print("Failed to create a post.")
