import datetime
import requests
from requests.auth import HTTPDigestAuth
import io
from PIL import Image
import numpy as np
import cv2

def network_cam(url, user=None, pswd=None):
    if user==None or pswd==None:
        rs = requests.get(url)
    else:
        rs = requests.get(url, auth=HTTPDigestAuth(user, pswd))
    img_bin = io.BytesIO(rs.content)
    img_pil = Image.open(img_bin)
    img_np  = np.asarray(img_pil)
    return cv2.cvtColor(img_np, cv2.COLOR_RGBA2BGR)

def calibration(img, dist1=0, dist2=0, dist3=0, dist4=0, dist5=0):
    h, w = img.shape[:2]
    f = max([h, w])
    mtx = np.array([[f,    0.,  w / 2],
                    [0.,   f,   h / 2],
                    [0.,   0.,  1    ]])
    dist = np.array([dist1, dist2, dist3, dist4, dist5])
    n_mtx = cv2.getOptimalNewCameraMatrix(mtx, dist, (img.shape[1], img.shape[0]), 1)[0]
    map = cv2.initUndistortRectifyMap(mtx, dist, np.eye(3), n_mtx, (img.shape[1], img.shape[0]), cv2.CV_32FC1)
    img = cv2.remap(img, map[0], map[1], cv2.INTER_CUBIC)
    return img

def nothing(x):
    pass

if __name__ == "__main__":
    import argparse, time
    parser = argparse.ArgumentParser(description='ネットワークカメラから映像を取得します') 
    parser.add_argument('url', help='ネットワークカメラのURL')
    parser.add_argument('-i', '--id', help='ネットワークカメラのログインID')
    parser.add_argument('-p', '--pw', help='ネットワークカメラのログインパスワード')
    parser.add_argument('-s', '--sec', help='データの取得間隔')
    args = parser.parse_args()
    url = args.url
    user = args.id
    pswd = args.pw
    sec = float(args.sec)
    img = network_cam(url, user, pswd)
    height, width = calibration(img).shape[:2]
    cv2.namedWindow('image', cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow('trackbar', cv2.WINDOW_NORMAL)
    cv2.createTrackbar('dist1','trackbar',50,100,nothing)
    cv2.createTrackbar('dist2','trackbar',50,100,nothing)
    cv2.createTrackbar('dist3','trackbar',50,100,nothing)
    cv2.createTrackbar('dist4','trackbar',50,100,nothing)
    cv2.createTrackbar('dist5','trackbar',50,100,nothing)
    cv2.createTrackbar('height','trackbar',height,height,nothing)
    cv2.createTrackbar('width','trackbar',width,width,nothing)
    flg = False
    last_save = 0

    try:
        while True:
            dist1 = (cv2.getTrackbarPos('dist1','trackbar')-50)/10
            dist2 = (cv2.getTrackbarPos('dist2','trackbar')-50)/10
            dist3 = (cv2.getTrackbarPos('dist3','trackbar')-50)/10
            dist4 = (cv2.getTrackbarPos('dist4','trackbar')-50)/10
            dist5 = (cv2.getTrackbarPos('dist5','trackbar')-50)/10
            __h = cv2.getTrackbarPos('height','trackbar')
            __w = cv2.getTrackbarPos('width','trackbar')
            img = network_cam(url, user, pswd)
            img = calibration(img, dist1, dist2, dist3, dist4, dist5)
            img = img[int(height/2-__h/2):int(height/2+__h/2),int(width/2-__w/2):int(width/2+__w/2)]
            now = datetime.datetime.now()
            now_str = now.strftime('%Y/%m/%d %H:%M:%S')
            if flg: now_str = now_str + '  now saving'
            filename = now.strftime('%Y%m%d_%H%M%S')
            key = cv2.waitKey(1) & 0xff
            if key == ord('q'):
                cv2.destroyAllWindows()
                break
            elif key == ord('s') and not flg:
                flg = True
                last_save = 0
            elif key == ord('s') and flg:
                flg = False
            if flg and time.time() - last_save > sec:
                cv2.imwrite('./'+filename+'.png', img)
                last_save = time.time()
            cv2.putText(img,now_str, (0, 15), cv2.FONT_HERSHEY_PLAIN, 1, (255,255,255), 1, cv2.LINE_AA)
            cv2.imshow('trackbar',np.zeros((1, 1, 1)))
            cv2.imshow('image',img)
    except Exception as e:
        print(e)
