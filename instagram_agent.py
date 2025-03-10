import os
import requests
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import instagrapi
from instagrapi import Client
import json
from hashtags import generate_metadata
import imageio

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
    gm = generate_metadata()
    hashtags = gm.generate_hashtags(quote)
    caption = f"{quote} {hashtags}"
    return caption

# Wrap text to fit within bounds
def wrap_text(text, font, max_width, draw):
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        test_line = ' '.join(current_line + [word])
        text_width = draw.textlength(test_line, font=font)
        if text_width <= max_width:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))
    return lines


def create_image(quote, image_name):
    print('Creating post, story and reel...')
    img = Image.open('old_paper_texture.jpg').convert('RGB')
    #draw = ImageDraw.Draw(img)
    img = img.resize((1080, 1080))
    font_size = 60
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    text_color = (50, 30, 10)  # Dark brown for vintage look

    # Create a drawable image
    combined = img.copy()
    draw = ImageDraw.Draw(combined)

    # Wrap the quote and calculate position
    max_text_width = combined.width - 100
    wrapped_text = wrap_text(quote, font, max_text_width, draw)

    # Calculate total text height
    text_height = sum(draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] for line in wrapped_text)
    text_y = (combined.height - text_height) // 2

    # Draw the wrapped text
    for line in wrapped_text:
        text_width = draw.textlength(line, font=font)
        text_x = (combined.width - text_width) // 2
        draw.text((text_x, text_y), line, font=font, fill=text_color)
        text_y += draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1]

    # Create frames with subtle flicker effect
    frames = []
    for i in range(10):
        enhancer = ImageEnhance.Brightness(combined)
        flicker = enhancer.enhance(0.95 + (i % 2) * 0.05)  # Alternates brightness
        frames.append(flicker)

    # Save as animated GIF
    print('creating gif...')
    frames[0].save(image_name+'.gif', save_all=True, append_images=frames[1:], duration=100, loop=0)
    print('Creating post and story...')
    frames[0].convert('RGB').save(image_name+'.jpg')
    print('Creating reel...')
    # Save the frames as an MP4 video for reels using imageio
    with imageio.get_writer(image_name+'.mp4', fps=2) as writer:
        for frame in frames:
            writer.append_data(imageio.v3.imread(frame))

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

    try:
        cl.login(username, password)
    except instagrapi.exceptions.TwoFactorRequired:
        verification_code = os.getenv("IG_2FA_CODE")
        if not verification_code:
            raise Exception("2FA code is missing! Please set IG_2FA_CODE in your GitHub secrets.")
        cl.login(username, password, verification_code=verification_code)

    try:
        #cl.login(username, password)
        caption = generate_caption(get_quote())
        cl.photo_upload(image_path+'.jpg', caption=caption)
        cl.photo_upload_to_story(image_path+'.jpg')
        media = cl.clip_upload(image_path+'.mp4', caption=caption)
        print("Image posted to Instagram story, reel and feed!")
    except Exception as e:
        print(f"Failed to post image: {e}")

if __name__ == "__main__":
    quote = get_quote()
    print(f"Quote: {quote}")

    if "Could not fetch" not in quote:
        image_name = 'quote_post'
        create_image(quote, image_name)
        print(f"\nImage saved as {image_name}")
        password = os.getenv("password")
        post_to_instagram("dailyquote785", password, image_name)
    else:
        print("Failed to create a post.")
