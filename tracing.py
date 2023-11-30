import cv2
import yaml
import parameter
import numpy as np

with open("config.yaml", 'r') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

def calculate_angle(line1, line2):
    """
    计算两条直线的夹角。

    Parameters:
    - line1 (numpy.ndarray): 第一条直线的参数 [vx, vy, x, y]。
    - line2 (numpy.ndarray): 第二条直线的参数 [vx, vy, x, y]。

    Returns:
    - angle (float): 两条直线之间的夹角（度数）。
    """
    if line1 is None or line2 is None:
        return None

    # 计算斜率
    slope1 = line1[1] / line1[0] if line1[0] != 0 else np.inf
    slope2 = line2[1] / line2[0] if line2[0] != 0 else np.inf

    # 计算夹角（以度数为单位）
    angle = np.arctan(np.abs((slope2 - slope1) / (1 + slope1 * slope2))) * (180 / np.pi)

    return angle

def calculate_distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return distance

def is_horizontal_line(line, angle_threshold=15):
    """
    判断给定直线是否接近水平。

    Parameters:
    - line (numpy.ndarray): 直线端点坐标数组 [x1, y1, x2, y2]。
    - angle_threshold (int): 判断水平的角度阈值，默认为15度。

    Returns:
    - bool: 直线是否接近水平。
    """
    if line is None or len(line) < 4:
        return False

    x1, y1, x2, y2 = line
    angle = np.arctan2(y2 - y1, x2 - x1) * (180 / np.pi)
    return abs(angle) < angle_threshold or abs(angle - 180) < angle_threshold

def fit_horizontal_lines(lines):
    """
    使用RANSAC算法对水平直线进行拟合。

    Parameters:
    - lines (list): 包含多个水平直线端点坐标的列表。

    Returns:
    - fitted_line (numpy.ndarray): 拟合后的水平直线数组 [vx, vy, x, y]。
    """
    if len(lines) < 2:
        return None

    points = np.array(lines).reshape(-1, 2)
    vx, vy, x, y = cv2.fitLine(points, cv2.DIST_L2, 0, 0.01, 0.01)

    return vx, vy, x, y

def find_color_boundary(frame):
    """
    在图像中查找指定颜色的水平直线，并进行拟合。

    Parameters:
    - frame (numpy.ndarray): 输入图像。

    Returns:
    - frame (numpy.ndarray): 处理后的图像，水平直线已经被拟合并标记。
    """
    point1 = (0, 0)
    point2 = (320, 640)
    angle = [0]
    
    Edge_Thresholds = config.get('Edge_Thresholds', {})

    lower_bound = Edge_Thresholds.get('lower_contour', [])
    upper_bound = Edge_Thresholds.get('upper_contour', [])

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, tuple(lower_bound), tuple(upper_bound))

    kernel = np.ones((9, 9), np.uint8)

    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    # cv2.imshow('gray', mask)
    edges = cv2.Canny(mask, 50, 150)

    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=100, maxLineGap=10)

    if lines is not None:
        horizontal_lines = [line[0] for line in lines if is_horizontal_line(line[0])]

        if horizontal_lines:
            fitted_line = fit_horizontal_lines(horizontal_lines)

            if fitted_line is not None:
                vx, vy, x, y = fitted_line
                points = np.array([[0, 320], [1280, 320]], dtype=np.int32)

                # 使用 cv2.fitLine() 进行直线拟合
                base_line= cv2.fitLine(points, cv2.DIST_L2, 0, 0.01, 0.01)

                # 计算直线的两个端点
                left_y = int((-x * vy / vx) + y)
                right_y = int(((frame.shape[1] - x) * vy / vx) + y)

                # 画出拟合后的直线
                cv2.line(frame, (0, left_y), (frame.shape[1] - 1, right_y), (0, 255, 0), 2)
                cv2.line(mask, (0, left_y), (frame.shape[1] - 1, right_y), (0, 255, 0), 2)
                cv2.line(frame, (0, 360), (1280, 360), (0, 0, 255), 2)
                # 提取拟合后的直线的端点坐标
                coordinates = [(0, left_y), (frame.shape[1] - 1, right_y)]
                #计算直线中点，两条直线的角度
                point1 = ((0 + frame.shape[1] - 1)/2, (left_y + right_y)/2)
                angle = calculate_angle(fitted_line, base_line)
                cv2.circle(frame, tuple(map(int, point1)), 5, (255, 0, 0), -1) 
                print("Fitted Line Coordinates:", coordinates)
    dis = [abs(int(point1[0] - point2[0])), abs(int(point1[1] - point2[1]))]

    parameter.Object_Data.angle = int(angle[0])
    parameter.Object_Data.dis = dis
    print("距离 = ", dis)
    print("角度 = ", angle)
    print("中点坐标 = ", point1)
    cv2.imshow('frame', frame)
    cv2.imshow('gray', mask)
