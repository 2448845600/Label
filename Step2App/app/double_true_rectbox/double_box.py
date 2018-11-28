import tkinter.filedialog as tkf
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
import os

"""
功能：
1 将正样本按照中心扩张,得到大小两个框，记录两个框的长宽，
2 修改负样本框，中心点不变，长宽和正样本扩张后的框相同。

错误提醒：
越界：检测是否存在框越界，若越界，输出该图片路径
"""

# 常量
input_weight = 1080
input_height = 1920
input_depth = 3
true_label = "true" # 需要扩张的label
false_label = "false"


def get_bigger_true_box(bndbox_dict, file_name):
    """

    :param bndbox_dict:
    :param file_name:
    :return: 返回扩张后的bbox和该bbox的边长
    """
    name = Element("name")
    name.text = true_label
    pose = Element("pose")
    pose.text = "Unspecified"
    truncated = Element("truncated")
    truncated.text = "0"
    difficult = Element("difficult")
    difficult.text = "0"

    xmin = Element("xmin")
    xmax = Element("xmax")
    ymin = Element("ymin")
    ymax = Element("ymax")
    xmin.text, ymin.text, xmax.text, ymax.text, length = get_expanded_bbox(bndbox_dict, file_name)

    bndbox = Element("bndbox")
    bndbox.append(xmin)
    bndbox.append(ymin)
    bndbox.append(xmax)
    bndbox.append(ymax)

    bigger_box = Element('object')
    bigger_box.append(name)
    bigger_box.append(pose)
    bigger_box.append(truncated)
    bigger_box.append(difficult)
    bigger_box.append(bndbox)

    return bigger_box, length


def get_expanded_bbox(bbox, file_name):
    """ 扩展框操作
    :param bbox:需要扩展的bbox
    :param file_name:该bbox所属的图片路径
    :return: str(xmin), str(ymin), str(xmax), str(ymax)
    """

    length = max(int(bbox["xmax"]) - int(bbox["xmin"]), int(bbox["ymax"]) - int(bbox["ymin"])) * 2

    xmin = int((int(bbox["xmin"]) + int(bbox["xmax"])) / 2 - int(length) / 2)
    xmax = int((int(bbox["xmin"]) + int(bbox["xmax"])) / 2 + int(length) / 2)
    ymin = int((int(bbox["ymin"]) + int(bbox["ymax"])) / 2 - int(length) / 2)
    ymax = int((int(bbox["ymin"]) + int(bbox["ymax"])) / 2 + int(length) / 2)

    return str(xmin), str(ymin), str(xmax), str(ymax), length


def get_expand_file_name():
    ext = '.xml'
    dir = tkf.askdirectory()  # 返回目录路径
    expand_file_name = list(filter(lambda filename: os.path.splitext(filename)[1] == ext, os.listdir(dir)))
    return list(map(lambda filename: os.path.join(dir, filename), expand_file_name))


def is_same_center(bbox_1, bbox_2):
    center_1_x = (int(bbox_1["xmin"]) + int(bbox_1["xmax"])) / 2
    center_1_y = (int(bbox_1["ymin"]) + int(bbox_1["ymax"])) / 2

    center_2_x = (int(bbox_2["xmin"]) + int(bbox_2["xmax"])) / 2
    center_2_y = (int(bbox_2["ymin"]) + int(bbox_2["ymax"])) / 2

    if abs(center_1_x - center_2_x) <= 2 and abs(center_1_y - center_2_y) <= 2:
        return True
    else:
        return False


# 删除已经扩展过的框（若两个框中心点相同，算作已经扩展过）
def check_bndboxes(bbox_list):
    # 逻辑好像有一点点问题
    for i in range(len(bbox_list)):
        for j in range(i, len(bbox_list)):
            if not is_same_center(bbox_list[i], bbox_list[j]):
                del bbox_list[j]
    return bbox_list


def write_expansion_to_xml(file_name):
    print("处理图片:", file_name)

    true_boxes_list = []
    false_boxes_list = []
    tree = ET.parse(file_name)
    root = tree.getroot()

    for child in root:
        if child.tag == "object":
            box = {"xmin": child[4][0].text, "ymin": child[4][1].text,
                   "xmax": child[4][2].text, "ymax": child[4][3].text}
            if child[0].text == true_label:
                true_boxes_list.append(box)
            elif child[0].text == false_label:
                false_boxes_list.append(box)

    # true_boxes_list = check_bnd_boxes(true_boxes_list)
    if len(true_boxes_list) == 1:
        print("处理正样本")
        bigger_bbox_length = 0
        for true_box in true_boxes_list:
            if len(true_box) == 4:
                new_object, bigger_bbox_length = get_bigger_true_box(true_box, file_name)
                root.append(new_object)  # 将该object加入根结点
        print("处理负样本")
        for child in root:
            if child.tag == "object":
                if not child[0].text == true_label:
                    center_x = (int(child[4][0].text) + int(child[4][2].text)) / 2
                    center_y = (int(child[4][1].text) + int(child[4][3].text)) / 2
                    child[4][0].text = str(int(center_x - bigger_bbox_length / 2))
                    child[4][2].text = str(int(center_x + bigger_bbox_length / 2))
                    child[4][1].text = str(int(center_y - bigger_bbox_length / 2))
                    child[4][3].text = str(int(center_y + bigger_bbox_length / 2))

    # 检查边界问题
    for child in root:
        if child.tag == "object":
            try:
                xmin, ymin, xmax, ymax = int(child[4][0].text), int(child[4][1].text), int(child[4][2].text), int(child[4][3].text)
                if xmin < 0 or xmax > input_weight or ymin < 0 or ymax > input_height:
                    print("该图片存在框超出范围:", file_name)
            except:
                print("这张图好像出了点问题:", file_name)

    # 重新写入xml文件，保存修改
    tree.write(file_name, encoding='utf-8', xml_declaration=True)


if __name__ == '__main__':
    print("选择待处理的文件")
    # 使用tk，让用户选择待处理的文件夹
    files_name = get_expand_file_name()

    # 干
    print("开始处理")
    for file_name in files_name:
        write_expansion_to_xml(file_name)

    print("结束")

