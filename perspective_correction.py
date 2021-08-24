import argparse
import cv2
import numpy as np
import time


class PerspectiveCorrection :

  def __init__(self, points) -> None:
    self.M, self.tl, self.tr, self.br, self.bl = self.get_transformation_info(points)

  def transform_perspective(self, points):
    pts = np.array([points], dtype=np.float32)
    trans_pts = cv2.perspectiveTransform(pts, self.M)
    return trans_pts

  def transform_image(self, image):
    full_wrap = cv2.warpPerspective(image, self.M, (image.shape[1], image.shape[0] + image.shape[0]//2))
    return full_wrap

  def order_points(self, pts):
    rect = np.zeros((4, 2), dtype = "float32")
    s = pts.sum(axis = 1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis = 1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

  def get_transformation_info(self, pts):
    rect = self.order_points(pts)
    (tl, tr, br, bl) = rect
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))
    dst = np.array([
      [0, 0],
      [maxWidth - 1, 0],
      [maxWidth - 1, maxHeight - 1],
      [0, maxHeight - 1]], dtype = "float32")
    M = cv2.getPerspectiveTransform(rect, dst)
    return M, tl, tr, br, bl


if __name__ == '__main__':
  # construct the argument parse and parse the arguments
  ap = argparse.ArgumentParser()
  ap.add_argument("-i", "--input",
    help = "input video path")
  ap.add_argument("-c", "--coords",
    help = "comma seperated list of source points")
  args = vars(ap.parse_args())
  pts = np.array(eval(args["coords"]), dtype = "float32")

  perspective_correction = PerspectiveCorrection(pts)

  cap = cv2.VideoCapture(args['input'])
  fourcc = cv2.VideoWriter_fourcc(*'XVID')

  width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # float `width`
  height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # float `height`
  out_height = height+ height + height//2

  out = cv2.VideoWriter('output.avi', fourcc, 20.0, (width, out_height))

  while(cap.isOpened()):
      ret, frame = cap.read()
      if ret:
        trans_points = perspective_correction.transform_perspective(pts)
        full_wrap = perspective_correction.transform_image(frame)
        
        for i in range(len(pts)):
          cv2.circle(frame, (int(pts[ i, 0]), int(pts[i, 1])), 10, color=(255, 0, 0), thickness=5)
          cv2.circle(full_wrap, (int(trans_points[0, i, 0]), int(trans_points[0, i, 1])), 10, color=(255, 0, 0), thickness=5)
        cv2.imshow("original", frame)
        cv2.imshow("full_wrap", full_wrap)
        concat_image = np.vstack([frame, full_wrap])
        out.write(concat_image)

        cv2.waitKey(1)
      else:
        break

  cap.release()
  out.release()
  cv2.destroyAllWindows()

# img = "obj/obj/pestwo - Google Drive 001.jpg"

# points = "[(378, 0), (900, 0), (0, 720), (1278, 720)]"
# offside4 video points = "[(492, 0), (868, 0), (0, 768), (1360, 768)]" 