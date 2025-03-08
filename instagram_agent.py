import requests
from PIL import Image, ImageDraw, ImageFont
from instagrapi import Client
import json

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

# Generate Instagram caption with basic hashtags
def generate_caption(quote):
    caption = f"{quote} #inspiration #motivation #dailyquote #positivity #wisdom"
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

    font_size = 60
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", font_size)
    except:
        font = ImageFont.load_default()

    max_width = img.width * 0.9
    lines = wrap_text(draw, quote, font, max_width)

    line_height = draw.textbbox((0, 0), "A", font=font)[3] - draw.textbbox((0, 0), "A", font=font)[1]
    line_spacing = 10
    total_height = (line_height + line_spacing) * len(lines)

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

    y = (img.height - total_height) // 2

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
        cl.challenge_select_verify_method(1)
        code = input("Enter the confirmation code sent to your email: ")
        cl.challenge_send_code(code)

# Post image to Instagram story and feed
def post_to_instagram(username, password, image_path):
    cl = Client()

    # Load session from GitHub secret
    session = json.loads(os.environ["IG_SESSION"])
    cl.load_settings(session)
    # try:
    #     cl.login(username, password)
    # except Exception as e:
    #     if "challenge_required" in str(e):
    #         handle_security_challenge(cl)
    #     else:
    #         print(f"Login failed: {e}")
    #         return

    try:
        cl.login(username, password)
        caption = generate_caption(get_quote())
        cl.photo_upload(image_path, caption=caption)
        cl.photo_upload_to_story(image_path)
        print("Image posted to Instagram story and feed!")
    except Exception as e:
        print(f"Failed to post image: {e}")

if __name__ == "__main__":
    quote = get_quote()
    print(f"Quote: {quote}")

    if "Could not fetch" not in quote:
        create_image(quote)
        print("\nImage saved as 'quote_post.jpg'")
        post_to_instagram("dailyquote785", "temp@1234", "quote_post.jpg")
    else:
        print("Failed to create a post.")
