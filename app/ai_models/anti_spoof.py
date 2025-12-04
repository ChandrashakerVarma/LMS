import cv2
import numpy as np


# ============================================================
# SHARPNESS CHECK (BLUR DETECTOR)
# Prevents users from uploading extremely blurry photos.
# ============================================================
def is_blurry(image, threshold=60.0):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    return variance < threshold  # True → blurry


# ============================================================
# LIGHTWEIGHT LBP CHECK (very soft) — works on photos
# ============================================================
def lbp_live_check(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Compute histogram
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    hist = hist.ravel() / hist.sum()

    # Flat printed images tend to have huge counts in first & last bins
    flatness = hist[0] + hist[-1]

    # Very soft threshold so real selfies do not fail
    return flatness < 0.70  # True → Live


# ============================================================
# DEPTH / SHADOW CHECK (soft version)
# Detects 2D flat surfaces like printed photos
# ============================================================
def depth_shadow_live_check(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    sobel = cv2.Sobel(gray, cv2.CV_64F, 1, 1, ksize=5)

    variance = np.var(sobel)

    # Very soft threshold to avoid false positives
    return variance > 60   # True → Live


# ============================================================
# FINAL DECISION LOGIC
# mode = "registration" → allow all (no spoof check)
# mode = "attendance"   → apply soft spoof checks
# ============================================================
def is_live_face(image, mode="attendance"):
    """
    RETURNS:
        True  → image is live
        False → spoof detected
    """

    # ---------------------------------------------------------
    # REGISTRATION MODE → DO NOT BLOCK SPOOF, only blur check
    # ---------------------------------------------------------
    if mode == "registration":
        if is_blurry(image):
            return False  # force retake only if blurry
        return True

    # ---------------------------------------------------------
    # ATTENDANCE MODE → Apply 2 soft spoof checks
    # ---------------------------------------------------------

    # 1. Blur check
    if is_blurry(image):
        return False  # likely printed or screen show

    # 2. LBP soft check
    if not lbp_live_check(image):
        return False

    # 3. Depth/shadow soft check
    if not depth_shadow_live_check(image):
        return False

    return True
