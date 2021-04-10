#!/usr/bin/python3.6
#coding: UTF-8
from utilities import *
from settings import *
from PIL import Image
from datetime import datetime

import cv2 as cv
import numpy as np
import json
import os
import pyocr
import pyocr.builders
import re
import shutil
import sys
import math
from scipy import ndimage

# 解析結果ファイル一時保存場所
temporary_dir = get_pass('') + 'temporary/'
while True:
    now  = datetime.now()
    time = now.strftime("%Y%m%d_%H%M%S")
    temporary_path = temporary_dir + time

    # 同時実行を考慮してディレクトリが作成できるまでループ
    if not os.path.isdir(temporary_path):
        os.makedirs(temporary_path)
        break

# 文字認識
def execute_ocr(image):
    result = {
        'result':'NG',
        'data':''
    }

    # OCRツール準備
    tools = pyocr.get_available_tools()
    if len(tools) == 0:
        logger.error('No OCR tool found')
        return result

    tool = tools[0]

    # セッティング
    builder = pyocr.builders.TextBuilder()
    builder.tesseract_flags = ['--psm', '6']
    builder.tesseract_configs += ["-c", "load_system_dawg=false"]
    builder.tesseract_configs += ["-c", "load_freq_dawg=false"]
    builder.tesseract_configs += ["-c", "tessedit_char_whitelist=0123456789"]

    # 文字認識
    txt = tool.image_to_string(
        Image.open(image),
        lang='eng',
        builder=builder
    )

    # 結果を間引いてカード番号だけを抽出
    matches = [val for val in txt.replace(' ', '').split() if len(val) == 16]
    if len(matches) == 1:
        result = {
            'result':'OK',
            'data':matches[0]
        }

    return result

# 画像内で最大領域を占める物体の向きを取得
def get_orientation(src):
    copy_img = src.copy()
    # リサイズ後のサイズを取得
    height, width, channels = copy_img.shape
    size = height * width

    # HSVへ変換
    image = cv.cvtColor(copy_img, cv.COLOR_BGR2HSV)

    # 白い領域を抽出してグレースケール化
    threshold_min = np.array([0, 0, 180], np.uint8)
    threshold_max = np.array([180, 255, 255], np.uint8)
    image = cv.inRange(image, threshold_min, threshold_max)
    image = cv.cvtColor(image, cv.COLOR_GRAY2RGB)
#    cv.imwrite(temporary_path + '/dst_0.png', image)

    # ノイズ消去
    kernel = np.ones((9,9), np.uint8)
    image  = cv.morphologyEx(image, cv.MORPH_OPEN, kernel)
    image  = cv.morphologyEx(image, cv.MORPH_CLOSE, kernel)
#    cv.imwrite(temporary_path + '/dst_1.png', image)

    # 境界を抽出
    gray_min = np.array([0], np.uint8)
    gray_max = np.array([128], np.uint8)
    threshold_gray = cv.inRange(image, gray_min, gray_max)
    contours, dst = cv.findContours(threshold_gray, cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE)

    # 最大領域を検索
    max_area_contour = -1
    max_area = 0
    for contour in contours:
        area = cv.contourArea(contour)
        # 画像全体を占める領域は除外
        if size * 0.9 < area :
            continue

        if(max_area < area):
            max_area = area
            max_area_contour = contour

#    cv.drawContours(copy_img, max_area_contour, -1, (0, 255, 0), 5)
#    cv.imwrite(temporary_path + '/dst_2.png', copy_img)

    if max_area_contour is -1 or (type(max_area_contour) is int == False):
        return 1

    # 輪郭の近似
    epsilon = 0.04 * cv.arcLength(max_area_contour, True)
    approx = cv.approxPolyDP(max_area_contour, epsilon, True)
#    cv.drawContours(copy_img, [approx], -1, (0, 0, 255), 3)
#    cv.imwrite(temporary_path + '/dst_3.png', copy_img)

    # 外接矩形の情報を取得
    x, y, w, h = cv.boundingRect(max_area_contour)

    return 1 if w > h else 0

# 画像の傾きを取得
def get_degree(src):
    copy_img = src.copy()
    gray_img = cv.cvtColor(copy_img, cv.COLOR_RGB2GRAY)

    # エッジと直線検出
    edges = cv.Canny(gray_img,50,150,apertureSize = 3)
    minLineLength = 200
    maxLineGap = 30
    lines = cv.HoughLinesP(edges,1,np.pi/180,100,minLineLength,maxLineGap)

    if lines is None:
        return 0

    # 直線の角度を取得
    sum_arg = 0;
    count = 0;
    arg = 0;
    for line in lines:
        for x1,y1,x2,y2 in line:
            arg = math.degrees(math.atan2((y2-y1), (x2-x1)))
            HORIZONTAL = 0
            DIFF = 20
            if arg != 0 and arg > HORIZONTAL - DIFF and arg < HORIZONTAL + DIFF :
                sum_arg += arg;
                count += 1
    if count == 0:
        return HORIZONTAL
    else:
        return (sum_arg / count) - HORIZONTAL;

# メイン
def main(input):
    # ファイルを読み込んで解析用にリサイズ
    image = cv.imread(input, cv.IMREAD_COLOR)
    cv.imwrite(temporary_path + '/origin.png', image)
    image = cv.resize(image, dsize = None, fx = 0.8, fy = 0.8)

    # 傾き調整
    arg = get_degree(image)
    image = ndimage.rotate(image, arg)

#    # カードの向きを取得
#    orientation = get_orientation(image)
#
#    # 縦になっているなら90度回転
#    if orientation == 0:
#        image = cv.rotate(image, cv.ROTATE_90_COUNTERCLOCKWISE)

    # 先鋭化
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]], np.float32)
    image = cv.filter2D(image, -1, kernel)

    # グレースケール化
    gray_img = cv.cvtColor(image, cv.COLOR_RGB2GRAY)

    # しきい値指定によるフィルタリング
    retval, dst = cv.threshold(gray_img, 0, 255, cv.THRESH_OTSU)

    cv.imwrite(temporary_path + '/result.png', dst)

    # 予備として180度回転させた画像も準備
    dst2 = cv.rotate(dst, cv.ROTATE_180)
    cv.imwrite(temporary_path + '/result2.png', dst2)

    # OCR
    result = execute_ocr(temporary_path + '/result.png')

    # 失敗なら予備画像で再試行
    if result['result'] == 'NG':
        result = execute_ocr(temporary_path + '/result2.png')

    # 解析用ファイルを削除
    if result['result'] == 'OK':
        shutil.rmtree(temporary_path)

    return result

# 実行
args = sys.argv
print(json.dumps(main(args[1])))
