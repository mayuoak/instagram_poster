from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import os


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


def create_image(quote):
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
    frames[0].save('vintage_quote_post.gif', save_all=True, append_images=frames[1:], duration=100, loop=0)

create_image("If you believe you can, you can. If you believe you can't, then, well you can't. - Celestine Chua")