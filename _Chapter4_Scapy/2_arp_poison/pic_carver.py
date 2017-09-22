# -*- coding: utf-8 -*-

import re
import zlib
import cv2

from scapy.all import *

picture_directory = "./pictures"
faces_directory = "./faces"
pcap_file = "bhp.pcap"

def get_http_headers(http_payload):
    try:
        # 如果为HTTP流量，提取HTTP头
        headers_raw = http_payload[:http_payload.index("\r\n\r\n") + 2]

        # 对HTTP头进行切分
        # (?P<name>.*?) ---> 对找到的结果进行进一步分割成字典形式
        # 如：dict(re.findall(r"(?P<name>.*?): (?P<value>.*?)\r\n", "Content-Type: image/pgf\r\n"))
        # 输出：{'Content-Type': 'image/pgf'}
        headers = dict(re.findall(r"(?P<name>.*?): (?P<value>.*?)\r\n", headers_raw))

    except:
        return None

    if "Content-Type" not in headers:
        return None

    return headers


def extract_image(headers, http_payload):
    image = None
    image_type = None

    try:
        if "image" in headers['Content-Type']:

            # 获取图像的类型和图像数据
            image_type = headers['Content-Type'].split("/")[1]

            image = http_payload[http_payload.index("\r\n\r\n") + 4:]

            # 如果进行了数据压缩则解压
            try:
                if "Content-Encoding" in headers.keys():
                    if headers['Content-Encoding'] == 'gzip':
                        image = zlib.decompress(image, 16 + zlib.MAX_WBITS)
                    elif headers['Content-Encoding'] == 'deflate':
                        image = zlib.decompress(image)
            except:
                pass
    except:
        return None, None

    return image, image_type


def face_detect(path, file_name):

    img = cv2.imread(path)
    cascade = cv2.CascadeClassifier("haarcascade_frontalface_alt.xml")
    rects = cascade.detectMultiScale(img, 1.3, 4, cv2.cv.CV_HAAR_SCALE_IMAGE, (20,20))

    if len(rects) == 0:
        return False

    rects[:, 2:] += rects[:, :2]

    # 对图像中的人脸进行高亮显示处理
    for x1,y1,x2,y2 in rects:
        cv2.rectangle(img, (x1,y1), (x2,y2), (127,255,0), 2)

    cv2.imwrite("%s/%s-%s" % (faces_directory, pcap_file, file_name), img)

    return True


def http_assembler(pcap_file):
    carved_images = 0
    faces_detected = 0

    a = rdpcap(pcap_file)

    sessions = a.sessions()

    for session in sessions:
        http_payload = ""

        for packet in sessions[session]:

            # 这一步与在Wireshark中右键 Follow TCP Stream 相似
            try:
                if packet[TCP].dport == 80 or packet[TCP].sport == 80:
                    # 对数据组包
                    http_payload += str(packet[TCP].payload)

            except:
                pass

        headers = get_http_headers(http_payload)

        if headers is None:
            continue

        image, image_type = extract_image(headers, http_payload)

        if image is not None and image_type is not None:
            # 存储图像
            file_name = "%s-pic_carver_%d.%s" % (pcap_file, carved_images, image_type)

            fd = open("%s/%s" % (picture_directory, file_name), "wb")
            fd.write(image)
            fd.close()

            carved_images += 1

            # 开始人脸检测
            try:
                result = face_detect("%s/%s" % (picture_directory, file_name), file_name)

                if result is True:
                    faces_detected += 1

            except:
                pass
    return carved_images, faces_detected


if __name__ == '__main__':
    carved_images, faces_detected = http_assembler(pcap_file)

    print "Extracted: %d images" % carved_images
    print "Detected: %d faces" % faces_detected
