import os
os.environ["CUDA_DEVICE_ORDER"] = 'PCI_BUS_ID'
os.environ["CUDA_VISIBLE_DEVICES"]="1"
os.environ["TF_FORCE_GPU_ALLOW_GROWTH"] = '0.8'

import os
import cv2
import xml.etree.ElementTree as ET
import numpy as np
import random

def get_noise_data (input_path , name_data, per_noise_label,per_noise_bboxes,w,h):
        all_imgs = []

        classes_count = {}

        class_mapping = {}

        visualise = False

        data_paths = [os.path.join(input_path,s) for s in [ 'VOC2012']]
        print('Parsing annotation files')

        for data_path in data_paths:

            annot_path = os.path.join(data_path, 'Annotations')
            imgs_path = os.path.join(data_path, 'JPEGImages')

            imgsets_path_train = os.path.join(data_path, 'ImageSets','Main','train.txt')
            imgsets_path_val = os.path.join(data_path, 'ImageSets','Main','val.txt')
            imgsets_path_test = os.path.join(data_path, 'ImageSets','Main','test.txt')

            train_files = []
            val_files = []
            test_files=[]
            try:

                with open(imgsets_path_train) as f:
                    for line in f:
                        train_files.append(line.strip() + '.jpg')

	    except Exception as e:
                print(e)


            try:
                with open(imgsets_path_val) as f:
                    for line in f:
                        val_files.append(line.strip() + '.jpg')
            except Exception as e:

                if data_path[-7:] == 'VOC2012':
                                # this is expected, most pascal voc distibutions dont have the test.txt file
                    pass
                else:
                    print(e)

            annots = [os.path.join(annot_path, s) for s in os.listdir(annot_path)]
            idx = 0
            for annot in annots:

                try:
                    idx += 1
                    et = ET.parse(annot)
                    element = et.getroot()
                    element_objs = element.findall('object')
                    element_filename = element.find('filename').text
                    element_width = int(element.find('size').find('width').text)
                    element_height = int(element.find('size').find('height').text)

                    if len(element_objs) > 0:
                        annotation_data = {'filepath': os.path.join(imgs_path, element_filename), 'width': element_width, 'height': element_height, 'bboxes': []}

                        if element_filename in train_files:
                            annotation_data['imageset'] = 'train'
                        elif element_filename in val_files:
                            annotation_data['imageset'] = 'val'
                        else:
                            annotation_data['imageset'] = 'train'

                    choice_bbox = [0, 1, 2]
                    rN_class_name = []

                    Nclass_mapping = ['person', 'cat', 'boat', 'chair', 'dog', 'tvmonitor', 'train', 'car', 'bottle',
                                      'diningtable', 'sofa', 'pottedplant', 'aeroplane', 'sheep', 'bus', 'bird',
                                      'bicycle',  'cow',  'motorbike',  'horse', 'bg']



                    if name_data == 'train':
                        for element_obj in element_objs:
                            class_name = element_obj.find('name').text
                            if class_name not in classes_count:
                                classes_count[class_name] = 1
                            else:
                                classes_count[class_name] += 1

                            if class_name not in class_mapping:
                                class_mapping[class_name] = len(class_mapping)


                            rNoise_bbox = random()
                            rNoise_label = random()

                            obj_bbox = element_obj.find('bndbox')

                            if rNoise_bbox <= per_noise_bboxes:
                                # On ajoute du bruit
                                # Bruit de bounding boxes
                                # On perturbe les coordonnées en largeur ou langueur
                                rand_choice_bbox = random.choice(choice_bbox)
                                if rand_choice_bbox == 0:
                                    # on perturbe en longueur
                                    Nw=random.uniform(0, w )
                                    x1 = int(round(float(obj_bbox.find('xmin').text))) -Nw
                                    y1 = int(round(float(obj_bbox.find('ymin').text)))
                                    x2 = int(round(float(obj_bbox.find('xmax').text))) + Nw
                                    y2 = int(round(float(obj_bbox.find('ymax').text)))
                                    difficulty = int(element_obj.find('difficult').text) == 1

                                elif rand_choice_bbox == 1:
                                    # on perturbe en longueur
                                    Nh=random.uniform(0,h)
                                    x1 = int(round(float(obj_bbox.find('xmin').text)))
                                    y1 = int(round(float(obj_bbox.find('ymin').text))) -Nh
                                    x2 = int(round(float(obj_bbox.find('xmax').text)))
                                    y2 = int(round(float(obj_bbox.find('ymax').text))) + Nh
                                    difficulty = int(element_obj.find('difficult').text) == 1
                                else:
                                    # on perturbe en longueur et largeur
                                    Nh=random.uniform(0,h)
                                    Nw=random.uniform(0,w)
                                    x1 = int(round(float(obj_bbox.find('xmin').text))) -Nw
                                    y1 = int(round(float(obj_bbox.find('ymin').text))) - Nh
                                    x2 = int(round(float(obj_bbox.find('xmax').text))) + Nw
                                    y2 = int(round(float(obj_bbox.find('ymax').text))) + Nh
                                    difficulty = int(element_obj.find('difficult').text) == 1

                            else:   # # on ne perturbe pas les bndboxes
                                x1 = int(round(float(obj_bbox.find('xmin').text)))
                                y1 = int(round(float(obj_bbox.find('ymin').text)))
                                x2 = int(round(float(obj_bbox.find('xmax').text)))
                                y2 = int(round(float(obj_bbox.find('ymax').text)))


                            if rNoise_label <= per_noise_label:
                                rN_class_name = random.choice(Nclass_mapping)
                                annotation_data['bboxes'].append({'class': rN_class_name, 'x1': x1, 'x2': x2, 'y1': y1, 'y2': y2,'difficult': difficulty})
                            else:
                                annotation_data['bboxes'].append({'class':class_name, 'x1': x1, 'x2': x2, 'y1': y1, 'y2': y2,'difficult': difficulty})

                        all_imgs.append(annotation_data)

                                    


                    elif name_data == 'val':
                        annotation_data['imageset'] = 'val'
                        for element_obj in element_objs:
                            class_name = element_obj.find('name').text
                            if class_name not in classes_count:
                                classes_count[class_name] = 1
                            else:
                                classes_count[class_name] += 1
                            if class_name not in class_mapping:
                                class_mapping[class_name] = len(class_mapping)

                            obj_bbox = element_obj.find('bndbox')
                            x1 = int(round(float(obj_bbox.find('xmin').text)))
                            y1 = int(round(float(obj_bbox.find('ymin').text)))
                            x2 = int(round(float(obj_bbox.find('xmax').text)))
                            y2 = int(round(float(obj_bbox.find('ymax').text)))
                            difficulty = int(element_obj.find('difficult').text) == 1
                            annotation_data['bboxes'].append({'class': class_name, 'x1': x1, 'x2': x2, 'y1': y1, 'y2': y2, 'difficult': difficulty})
                        all_imgs.append(annotation_data)

                    elif name_data == 'test':
                        annotation_data['imageset'] = 'test'
                        for element_obj in element_objs:
                            class_name = element_obj.find('name').text
                            if class_name not in classes_count:
                                classes_count[class_name] = 1
                            else:
                                classes_count[class_name] += 1

                            if class_name not in class_mapping:

                            obj_bbox = element_obj.find('bndbox')
                            x1 = int(round(float(obj_bbox.find('xmin').text)))
                            y1 = int(round(float(obj_bbox.find('ymin').text)))
                            x2 = int(round(float(obj_bbox.find('xmax').text)))
                            y2 = int(round(float(obj_bbox.find('ymax').text)))
                            difficulty = int(element_obj.find('difficult').text) == 1
                            annotation_data['bboxes'].append({'class': class_name, 'x1': x1, 'x2': x2, 'y1': y1, 'y2': y2, 'difficult': difficulty})
                        all_imgs.append(annotation_data)

                    if visualise:
                        img = cv2.imread(annotation_data['filepath'])
                        for bbox in annotation_data['bboxes']:
                            cv2.rectangle(img, (bbox['x1'], bbox['y1']), (bbox['x2'], bbox['y2']), (0, 0, 255))

                        cv2.imshow('img', img)
                        cv2.waitKey(0)

                except Exception as e:
                    print(e)
                    continue
        return all_imgs, classes_count, class_mapping
                            



















