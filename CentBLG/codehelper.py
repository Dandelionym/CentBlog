from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import random


def official_code_img_gen(session_put):
	width = 200
	height = 45
	
	def get_random_color():
		return random.randint(100, 200), random.randint(100, 200), random.randint(100, 200)
	
	img = Image.new("RGBA", (width, height), color=(255, 255, 255))
	draw = ImageDraw.Draw(img)
	BHB_font = ImageFont.truetype('arial.ttf', size=30)
	# BHB_font = ImageFont.load_default()

	official_code = ""
	
	for i in range(4):
		random_num = str(random.randint(0, 9))
		random_lower_alpha = chr(random.randint(97, 122))
		random_upper_alpha = chr(random.randint(65, 90))
		random_char = random.choice([random_num, random_upper_alpha, random_lower_alpha])
		draw.text((5 + i * 53, 5), random_char, get_random_color(), font=BHB_font)
		official_code += str(random_char)
	
	session_put(official_code)

	for i in range(25):
		x1 = random.randint(0, width)
		x2 = random.randint(0, width)
		y1 = random.randint(0, height)
		y2 = random.randint(0, height)
		draw.line((x1, y1, x2, y2), fill=get_random_color())
	for i in range(25):
		draw.point([random.randint(0, width), random.randint(0, height)], fill=get_random_color())
		x = random.randint(0, width)
		y = random.randint(0, height)
		draw.arc((x, y, x + 4, y + 4), 0, 90, fill=get_random_color())
	f = BytesIO()
	img.save(f, "png")
	data = f.getvalue()
	
	return data