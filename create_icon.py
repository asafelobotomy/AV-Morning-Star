#!/usr/bin/env python3
"""
Simple script to create a basic icon for the application
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    # Create a 256x256 image with a gradient background
    size = 256
    img = Image.new('RGB', (size, size), color='#2c3e50')
    draw = ImageDraw.Draw(img)
    
    # Draw a gradient-like effect
    for i in range(0, size, 4):
        color = int(44 + (i / size) * 40)
        draw.rectangle([0, i, size, i+4], fill=(color, color+20, color+40))
    
    # Draw a play button symbol
    triangle = [(80, 60), (80, 196), (196, 128)]
    draw.polygon(triangle, fill='#e74c3c')
    
    # Draw a music note
    draw.ellipse([140, 180, 170, 210], fill='#3498db')
    draw.rectangle([165, 150, 175, 195], fill='#3498db')
    
    # Add text
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    text = "AV ⭐"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = (size - text_width) // 2
    text_y = 20
    
    # Draw text with shadow
    draw.text((text_x+2, text_y+2), text, fill='#000000', font=font)
    draw.text((text_x, text_y), text, fill='#ecf0f1', font=font)
    
    # Save
    img.save('av-morning-star.png')
    print("Icon created: av-morning-star.png")

if __name__ == '__main__':
    try:
        create_icon()
    except ImportError:
        print("Pillow not installed. Creating a placeholder icon...")
        # Create a minimal SVG icon instead
        svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="256" height="256" xmlns="http://www.w3.org/2000/svg">
  <rect width="256" height="256" fill="#2c3e50"/>
  <polygon points="80,60 80,196 196,128" fill="#e74c3c"/>
  <circle cx="155" cy="195" r="15" fill="#3498db"/>
  <rect x="165" y="150" width="10" height="45" fill="#3498db"/>
  <text x="128" y="40" font-family="Arial" font-size="24" fill="#ecf0f1" text-anchor="middle">AV ⭐</text>
</svg>'''
        with open('av-morning-star.svg', 'w') as f:
            f.write(svg_content)
        print("SVG icon created: av-morning-star.svg")
        print("Please convert it to PNG or provide your own av-morning-star.png")
