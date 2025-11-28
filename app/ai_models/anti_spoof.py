import cv2
import numpy as np
from scipy.spatial import distance as dist


# ---------------------------------------------------------
# LEVEL 1: LBP Texture Analysis (detect printed photos)
# ---------------------------------------------------------
def lbp_histogram(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    lbp = np.zeros_like(gray)

    for i in range(1, gray.shape[0] - 1):
        for j in range(1, gray.shape[1] - 1):
            center = gray[i, j]
            binary = ""

            binary += "1" if gray[i - 1, j - 1] > center else "0"
            binary += "1" if gray[i - 1, j] > center else "0"
            binary += "1" if gray[i - 1, j + 1] > center else "0"
            binary += "1" if gray[i, j + 1] > center else "0"
            binary += "1" if gray[i + 1, j + 1] > center else "0"
            binary += "1" if gray[i + 1, j] > center else "0"
            binary += "1" if gray[i + 1, j - 1] > center else "0"
            binary += "1" if gray[i, j - 1] > center else "0"

            lbp[i, j] = int(binary, 2)

    hist, _ = np.histogram(lbp.ravel(), 256, [0, 256])
    hist = hist.astype("float")
    hist /= hist.sum()
    return hist


def lbp_spoof_detector(frame):
    hist = lbp_histogram(frame)
    flatness = hist[0] + hist[-1]  # printed photos show high flatness

    if flatness > 0.35:
        return False  # SPOOF
    return True  # LIVE


# ---------------------------------------------------------
# LEVEL 2: Eye Blink + Mouth Movement (real-time check)
# ---------------------------------------------------------
def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)


def blink_detector(ear):
    return ear < 0.21  # threshold


# ---------------------------------------------------------
# LEVEL 3: Shadow/Depth Check (3D estimation)
# ---------------------------------------------------------
def depth_shadow_check(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    sobel = cv2.Sobel(gray, cv2.CV_64F, 1, 1, ksize=5)

    variance = np.var(sobel)
    if variance < 150:   # flat surface = printed photo
        return False
    return True


# ---------------------------------------------------------
# FINAL SPOOF DETECTION
# ---------------------------------------------------------
def is_live_face(frame):
    """
    Returns:
        True → Real human
        False → Spoof attack
    """

    # LEVEL 1: LBP
    if not lbp_spoof_detector(frame):
        return False

    # LEVEL 2: Depth/Shadow
    if not depth_shadow_check(frame):
        return False

    # LEVEL 3: (Blink detection optional - landmarks needed)

    return True
