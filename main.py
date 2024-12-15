import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

def scrape_pitch_presentation(url, total_slides=15):
    """
    Scrape a Pitch.com presentation and generate a PDF
    
    Args:
    url (str): URL of the Pitch.com presentation
    total_slides (int): Total number of slides expected
    
    Returns:
    str: Path to the generated PDF
    """
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Setup WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Navigate to the URL
        driver.get(url)
        
        # Wait for the presentation to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test-id='player-button-next']"))
        )
        
        # Prepare for PDF generation
        slides_dir = "pitch_slides"
        os.makedirs(slides_dir, exist_ok=True)
        
        # Capture slides
        slides_paths = []
            # Set fixed 16:9 aspect ratio dimensions (1920x1080 is a common 16:9 resolution)
        base_width = 1920
        base_height = 1080
        
        # Set window size to match desired aspect ratio
        driver.set_window_size(base_width, base_height)
        
        for slide_num in range(total_slides):
            # Wait for slide to be fully rendered
            time.sleep(1.5)
            
            # Capture slide as PNG
            slide_path = os.path.join(slides_dir, f"slide_{slide_num+1}.png")
            driver.save_screenshot(slide_path)
            slides_paths.append(slide_path)
            
            # Don't try to click next on the last slide
            if slide_num < total_slides - 1:
                try:
                    next_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-test-id='player-button-next']"))
                    )
                    next_button.click()
                except Exception as e:
                    print(f"Could not click next button on slide {slide_num+1}: {e}")
                    break
        
        # Generate PDF with fixed dimensions
        width_points = base_width * 72 / 96  # Convert pixels to points (96 DPI)
        height_points = base_height * 72 / 96
        
        pdf_path = "pitch_presentation.pdf"
        c = canvas.Canvas(pdf_path, pagesize=(width_points, height_points))
        
        for slide_image in slides_paths:
            # Draw image exactly filling the page
            c.drawImage(slide_image, 0, 0, width=width_points, height=height_points)
            c.showPage()
        
        c.save()
        
        return pdf_path
    
    finally:
        # Always close the browser
        driver.quit()

def main():
    # Replace with your actual Pitch.com presentation URL
    url = input("Enter the Pitch.com presentation URL: ")
    
    # Optional: Specify total number of slides if different from 15
    slides = int(input("Enter total number of slides (default is 15): ") or 15)
    
    pdf_path = scrape_pitch_presentation(url, slides)
    print(f"PDF generated successfully at: {pdf_path}")

if __name__ == "__main__":
    main()

# Required dependencies:
# pip install selenium webdriver-manager Pillow reportlab
