import numpy as np
import cv2
import math
import darknet
from perspective_correction import PerspectiveCorrection


class Player:

  def __init__(self, x, y, w, h, transformer) -> None:
    self.x = x
    self.y = y
    self.w = w
    self.h = h
    self.transformer =  transformer
    self.passer = False
    self.suspect = False
    self.offside = False
    self.path = []


  def leg_pos(self):
    x = self.x
    y = self.y + self.h//2
    return x, y

  def transformed_x(self):
    pts = np.reshape(np.array([[self.x, self.y]], dtype=np.float32), (-1, 2))
    transformed = self.transformer.transform_perspective(pts)
    return transformed[0, 0, 0]

  def update(self, x, y, w, h):
    self.path.append([self.x, self.y])
    self.path = self.path[-20: ]
    self.x = x
    self.y = y
    self.w = w
    self.h = h

  def get_line_points(self):
    pass


class Football:

  def __init__(self, x, y, w, h) -> None:
      self.x = x
      self.y = y
      self.w = w
      self.h = h
      self.path = []

  def  update(self, x, y, w, h):
    self.path.append([self.x, self.y])
    self.path = self.path[-20: ]
    self.x = x
    self.y = y
    self.w = w
    self.h = h

  def moving_left(self):
    if len(self.path) > 0 and self.path[-1][0] < self.x:
      return True
    else:
      return False
    

class GameCoordinator():
  def __init__(self, class_colors, calibration_points, left_player_label='Player_D', right_player_label='Player_L') -> None:
    self.offside_detected = False
    self.offside_player = None
    self.class_colors = class_colors
    self.left_player_label = left_player_label
    self.right_player_label = right_player_label
    self.perspective_correction = PerspectiveCorrection(calibration_points)
    self.ball = None
    self.left_players = []
    self.right_players = []


  def get_iou(self, ybox1, ybox2):
    """
    Calculate the Intersection over Union (IoU) of two bounding boxes.

    Parameters
    ----------
    bb1 : dict
        Keys: {'x1', 'x2', 'y1', 'y2'}
        The (x1, y1) position is at the top left corner,
        the (x2, y2) position is at the bottom right corner
    bb2 : dict
        Keys: {'x1', 'x2', 'y1', 'y2'}
        The (x, y) position is at the top left corner,
        the (x2, y2) position is at the bottom right corner

    Returns
    -------
    float
        in [0, 1]
    """
    bb1 = {"x1": ybox1[0]-ybox1[2]//2,
      "x2": ybox1[0]+ybox1[2]//2,
      "y1": ybox1[1]-ybox1[3]//2,
      "y2": ybox1[1]+ybox1[3]//2}

    bb2 = {"x1": ybox2[0]-ybox2[2]//2,
      "x2": ybox2[0]+ybox2[2]//2,
      "y1": ybox2[1]-ybox2[3]//2,
      "y2": ybox2[1]+ybox2[3]//2}

    assert bb1['x1'] < bb1['x2']
    assert bb1['y1'] < bb1['y2']
    assert bb2['x1'] < bb2['x2']
    assert bb2['y1'] < bb2['y2']

    # determine the coordinates of the intersection rectangle
    x_left = max(bb1['x1'], bb2['x1'])
    y_top = max(bb1['y1'], bb2['y1'])
    x_right = min(bb1['x2'], bb2['x2'])
    y_bottom = min(bb1['y2'], bb2['y2'])

    if x_right < x_left or y_bottom < y_top:
        return 0.0

    # The intersection of two axis-aligned bounding boxes is always an
    # axis-aligned bounding box
    intersection_area = (x_right - x_left) * (y_bottom - y_top)

    # compute the area of both AABBs
    bb1_area = (bb1['x2'] - bb1['x1']) * (bb1['y2'] - bb1['y1'])
    bb2_area = (bb2['x2'] - bb2['x1']) * (bb2['y2'] - bb2['y1'])

    # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    iou = intersection_area / float(bb1_area + bb2_area - intersection_area)
    assert iou >= 0.0
    assert iou <= 1.0
    return iou

  def update_football(self, detection):
    if self.ball == None:
      self.ball = Football(detection[0], detection[1], detection[2], detection[3])
    else:
      self.ball.update(detection[0], detection[1], detection[2], detection[3])

  def distance(self, x1, y1, x2, y2):
    dis = (x1-x2)*(x1-x2) + (y1-y2)*(y1-y2)
    return int(math.sqrt(dis))

  def update_players(self, players, detection):

    x, y = detection[0], detection[1]
    max_iou = 0
    ind = None
    for i in range(len(players)):
      iou = self.get_iou(detection, [players[i].x, players[i].y, players[i].w, players[i].h])
      if iou > max_iou:
        max_iou = iou
        ind = i

    if ind and max_iou > 0.5:
      player = players[ind]
      del players[ind]
      player.update(detection[0], detection[1], detection[2], detection[3])
      return player
    else:
      return Player(detection[0], detection[1], detection[2], detection[3], self.perspective_correction)

  
  def update_game(self):
    
    if not self.ball:
      return

    new_passer = None
    ball_x, ball_y = self.ball.x, self.ball.y
    for player in self.left_players + self.right_players:
      x, y = player.leg_pos()
      dis = self.distance(ball_x, ball_y, x, y)
      if (dis < player.w//2 + player.w//4 and abs(y-ball_y) < player.w//2):
        if (not player.passer and player.suspect):
          self.offside_detected = True
          player.offside = True
          break
        else:
          new_passer = player
          player.passer = True
          player.suspect = False

    if new_passer:
      for player in self.left_players + self.right_players:
        player.suspect = False
        if player != new_passer:
          player.passer = False

      for player in self.left_players:
        if player.transformed_x() > self.right_players[-1].transformed_x():
          player.suspect = True
        else:
          break

      for player in self.right_players:
        if player.transformed_x() < self.left_players[-1].transformed_x():
          player.suspect = True
        else:
          break


  def process_next(self, frame, detections):
    self.detections = detections
    self.current_frame = frame
    self.ball = None
    self.perspective_corrected = []

    new_left_players = []
    new_right_players = []
    for label, _, bbox in detections:
      if label == 'Football':
        self.update_football(bbox)
      elif label == self.left_player_label:
        new_left_players.append(self.update_players(self.left_players, bbox))
      elif label == self.right_player_label:
        new_right_players.append(self.update_players(self.right_players, bbox))
        
      center_x, center_y = bbox[0], bbox[1]

      pts = np.reshape(np.array([[center_x, center_y]], dtype=np.float32), (-1, 2))
      self.perspective_corrected.append(self.perspective_correction.transform_perspective(pts))
    
    self.left_players = new_left_players
    self.right_players = new_right_players

    self.left_players.sort(key=lambda player: player.transformed_x(), reverse=True)
    self.right_players.sort(key=lambda player: player.transformed_x(), reverse=False)

    # print([(player.x, player.y, player.transformed_x()) for player in self.left_players])
    # print([(player.x, player.y, player.transformed_x()) for player in self.right_players])

    self.update_game()


  def draw_path(self, image, path, thikness=5):
  
    if not path or len(path) < 1:
      return

    x, y = path[0][0], path[0][1]

    for i in range(1, len(path)):
      x2, y2 = path[i][0], path[i][1]
      cv2.line(image, (x, y), (x2, y2), (0, 255, 0), thickness=thikness)
 


  def visualize(self):

    vis_image = self.current_frame.copy()
    vis_image = darknet.draw_boxes(self.detections, vis_image, self.class_colors)

    for player in self.left_players + self.right_players:
      if player.suspect:
        cv2.circle(vis_image, (player.x, player.y), 10, color=(0, 0, 0), thickness=5)
        calib_points = cv2.perspectiveTransform(np.array([[(200, 0), (200, 768)]], dtype=np.float32), self.perspective_correction.M)
        inv_trans = np.linalg.pinv(self.perspective_correction.M)
        trans_points = cv2.perspectiveTransform(np.array(
          [[(player.transformed_x(), calib_points[0, 0, 1]), (player.transformed_x(), calib_points[0, 1, 1])]],
          dtype=np.float32),
          inv_trans)
        vis_image = cv2.line(vis_image, (trans_points[0, 0, 0], trans_points[0, 0, 1]), (trans_points[0, 1, 0], trans_points[0, 1, 1]), color=(0, 0, 255), thickness=3)  

      if player.passer:
        cv2.circle(vis_image, (player.x, player.y), 10, color=(255, 255, 255), thickness=5)  
      if player.offside:
        cv2.circle(vis_image, (player.x, player.y), 10, color=(0, 0, 255), thickness=10)


    perspective_image = self.perspective_correction.transform_image(self.current_frame)

    for center in self.perspective_corrected:
      cv2.circle(perspective_image, (int(center[0, 0, 0]), int(center[0, 0, 1])), 10, color=(255, 0, 0), thickness=5)

    return vis_image, perspective_image