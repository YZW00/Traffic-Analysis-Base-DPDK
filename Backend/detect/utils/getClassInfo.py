import os
# txt_dir = '../weights/classic_ClassesInfo.txt'

# 读取类别信息
def getClassInfo(txt_dir):
    try:
        class_dict = dict()
        with open(txt_dir,'r', encoding='utf-8') as f:
            for line in f.readlines():
                line = line.strip().split(':')
                class_dict[int(line[0])] = line[1]
        return class_dict
    except Exception as e:
        return {'status': 'fail', 'error':str(e)}

if __name__ == '__main__':
    txt_dir = '../weights/classic_ClassesInfo.txt'
    class_dict = getClassInfo(txt_dir)
    print(class_dict)