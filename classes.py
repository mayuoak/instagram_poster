import requests

class generate:
 def __init__(self, topic="fitness"):
  self.topic = topic
    
 def generate_quote(self):
  quote_api = "https://zenquotes.io/api/random"
  response = requests.get(quote_api)
  quote_data = response.json()[0]
  quote = quote_data['q']
  author = quote_data['a']
  return quote, author



obj = generate()
q, a = obj.generate_quote()
print(q, a)

unsplash_url = "https://source.unsplash.com/featured/?inspiration"
image_path = 'quote_image.jpg'
img_response = requests.get(unsplash_url)
if 'image' in img_response.headers['Content-Type']:
 with open(image_path, 'wb') as handler:
  handler.write(img_response.content)
else:
 raise ValueError("Failed to download a valid image")