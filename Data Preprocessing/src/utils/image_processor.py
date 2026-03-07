import cv2
import numpy as np

def resize_and_normalize(image, target_size=(1024, 1024)):
    """
    Resize image to target_size and normalize pixel values.
    """
    # Resize
    resized = cv2.resize(image, target_size, interpolation=cv2.INTER_AREA)
    
    # Normalize to [0, 1] range
    normalized = resized.astype(np.float32) / 255.0
    
    return normalized

def detect_blur_and_bright_spot(image, blur_threshold=250.0):
    """
    Detects if an image is blurry or has bright spots.
    Returns (is_blurry, has_bright_spot, laplacian_variance, binary_variance)
    """
    # Convert image to grayscale for analysis
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    # Apply binary thresholding for bright spot detection
    _, binary_image = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

    # Apply Laplacian filter for edge detection
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)

    # Calculate variances
    binary_variance = binary_image.var()
    laplacian_variance = laplacian.var()

    # Determine conditions
    is_blurry = laplacian_variance < blur_threshold
    
    # Check bright spot condition based on variance of binary image (as per Sahil Utekar's blog)
    # Note: 5000 < binary_variance < 8500 range was mentioned
    has_bright_spot = 5000 < binary_variance < 8500

    return is_blurry, has_bright_spot, laplacian_variance, binary_variance

def sharpen_image(image):
    """
    Applies a sharpening filter to the image using a standard kernel.
    """
    # Standard sharpening kernel
    kernel = np.array([[-1, -1, -1],
                       [-1,  9, -1],
                       [-1, -1, -1]])
    # Apply filtering
    sharpened = cv2.filter2D(image, -1, kernel)
    return sharpened
