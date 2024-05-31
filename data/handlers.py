from datetime import datetime

import requests
from face_recognition import compare_faces
from data.models import Data, Journal
import telegram



import os
import shutil

import cv2
import dlib
from skimage import io
from scipy.spatial import distance

TOKEN = '7047307763:AAHfBNSGPaZePzmRGfHgSu8-sFUtqvN_M1A'
bot = telegram.Bot(token=TOKEN)


def detect_faces(input_image_path, output_folder, userid=None, padding = 20):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    image = cv2.imread(input_image_path)
    gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder)

    for i, (x, y, w, h) in enumerate(faces):
        x -= padding
        y -= padding
        w += 2 * padding
        h += 2 * padding
        face = image[y:y + h, x:x + w]
        output_path = os.path.join(output_folder, f"face_{i+1}.jpg")
        cv2.imwrite(output_path, face)
        # print(f"Face {i+1} Saved as {output_path}")
    if userid:
        compare_faces(output_folder, userid)
    else:
        return compare_faces(output_folder)


def compare_faces(buf_folder_path, userid=None, data_folder_path='/Users/zelenol/Documents/VKRProject/photos'):
    print("Comparing faces...")
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor('/Users/zelenol/Documents/VKRProject/data/shape_predictor_68_face_landmarks.dat')
    facerec = dlib.face_recognition_model_v1('/Users/zelenol/Documents/VKRProject/data/dlib_face_recognition_resnet_model_v1.dat')
    users = []
    users_data = []
    for input_filename in os.listdir(buf_folder_path):
        input_image_path = os.path.join(buf_folder_path, input_filename)
        if not os.path.isfile(input_image_path) or not input_filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            continue
        input_img = io.imread(input_image_path)
        dets1 = detector(input_img, 1)
        for k, d in enumerate(dets1):
            shape1 = predictor(input_img, d)
            face_descriptor1 = facerec.compute_face_descriptor(input_img, shape1)

            for db_filename in os.listdir(data_folder_path):
                db_image_path = os.path.join(data_folder_path, db_filename)
                if not os.path.isfile(db_image_path) or not db_filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    continue
                db_img = io.imread(db_image_path)
                dets2 = detector(db_img, 1)
                for k, d in enumerate(dets2):
                    shape2 = predictor(db_img, d)
                    face_descriptor2 = facerec.compute_face_descriptor(db_img, shape2)

                    distance_between_faces = distance.euclidean(face_descriptor1, face_descriptor2)
                    if distance_between_faces <= 0.6:
                        try:
                            user = Data.objects.get(photo=f'photos/{db_filename}')
                            users.append(f'{user.first_name} {user.last_name} {user.group}')
                            users_data.append(
                                {
                                    'name': f'{user.first_name} {user.last_name}',
                                    'group': user.group
                                }
                            )
                            print(user.first_name + " " + user.last_name)
                            date = datetime.now()
                            if not Journal.objects.filter(user=user, date=date).exists():
                                Journal.objects.create(user=user)

                        except Data.DoesNotExist:
                            print("none")


                        print("Присутствует " + db_filename)
                        break
                else:
                    continue
                break
    text = ""
    for user in users:
        text += f'{user}\n'
    if userid:
        bot.send_message(chat_id=userid, text=text)
    return users_data


def journal_find(date, userid):
    date_object = datetime.strptime(date, '%Y-%m-%d')
    journal = Journal.objects.filter(date=date_object)
    print(journal)
    users = ""
    for user in journal:
        users += f'{user.user.first_name} {user.user.last_name} {user.user.group}\n'
    text = (f'Дата: {date}\n'
            f'Присутствует {len(journal)}\n'
            f'\n'
            f'{users}')
    if userid:
        bot.send_message(chat_id=userid, text=text)
    user_data = []
    for user in journal:
        user_data.append(
            {
                'name': f'{user.user.first_name} {user.user.last_name}',
                'group': f'{user.user.group}'
            }
        )
    return user_data
