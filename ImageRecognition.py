import boto3, os, shutil, uuid
from PIL import Image

class ImageRecognition:
    def __init__(self, version):
        self.INDEX_DIRECTORY = "./images-index"
        self.LOCAL_PHOTO_DIRECTORY = "./input-images"
        self.RESIZED_IMAGE_DIRECTORY = './resized-input-images'
        self.TEMP_FOLDER = "/tmp/Facetrack/"
        COLLECTION_VERSION = version
        self.REKOGNITION_COLLECTION_ID = "Facetrack-main-v" + str(COLLECTION_VERSION)
        self.REKOGNITION_INDEX_COLLECTION_ID = "Facetrack-index-v" + str(COLLECTION_VERSION)
        AWS_REGION = "ap-south-1"
        self.rekognition_client = boto3.client('rekognition', region_name=AWS_REGION)
        
    def resize_all_images(self):
        files = os.listdir(self.LOCAL_PHOTO_DIRECTORY)
        for filename in files:
            input_path = os.path.join(self.LOCAL_PHOTO_DIRECTORY, filename)
            output_path = os.path.join(self.RESIZED_IMAGE_DIRECTORY, filename)
            with Image.open(input_path) as img:
                width, height = img.size
                aspect_ratio = height / width
                new_height = int(800 * aspect_ratio)
                resized_img = img.resize((800, new_height), Image.Resampling.LANCZOS)
                resized_img.save(output_path)
        return True
    
    def get_all_resized_images(self):
        files = os.listdir(self.RESIZED_IMAGE_DIRECTORY)
        return list(map(lambda x: self.RESIZED_IMAGE_DIRECTORY + '/' + x, files))

    def index_image(self, file_path, collection_type = 'main'):
        collection_id = self.REKOGNITION_COLLECTION_ID if collection_type == 'main' else self.REKOGNITION_INDEX_COLLECTION_ID
        image_bytes = open(file_path, 'rb').read()
        response = self.rekognition_client.index_faces(
                    CollectionId=collection_id,
                    Image={'Bytes': image_bytes},
                    ExternalImageId=file_path.split('/')[-1],
                    DetectionAttributes=['ALL']
                )
        bounding_rects = []
        if (response and response['FaceRecords'] and len(response['FaceRecords']) > 0):
                for face_match in response['FaceRecords']:
                    face_bounding_box = face_match['Face']['BoundingBox']
                    
                    bounding_rects.append((face_bounding_box['Left'], face_bounding_box['Top'], face_bounding_box['Left'] + face_bounding_box['Width'], face_bounding_box['Top'] + face_bounding_box['Height']))
        return bounding_rects

    def crop_image_by_path_and_bounding_rects(self, file_path, bounding_rects):
        output_paths = []
        for bounding_rect in bounding_rects:
            with Image.open(file_path) as img:
                img_width, img_height = img.size
                left = int(bounding_rect[0] * img_width)
                top = int(bounding_rect[1] * img_height)
                right = int(bounding_rect[2] * img_width)
                bottom = int(bounding_rect[3] * img_height)
                # Crop the image using the bounding rectangle
                cropped_img = img.crop((left, top, right, bottom))
                output_path = self.TEMP_FOLDER + str(uuid.uuid4()) + '.jpg'
                cropped_img.save(output_path)
                output_paths.append(output_path)
        return output_paths

    def search_image_in_collection(self, face_file_path, collection_type = 'main'):
        collection_id = self.REKOGNITION_COLLECTION_ID if collection_type == 'main' else self.REKOGNITION_INDEX_COLLECTION_ID
        image_bytes = open(face_file_path, 'rb').read()
        response = self.rekognition_client.search_faces_by_image(
            CollectionId=collection_id,
            Image={'Bytes': image_bytes}
        )
        number_of_faces = len(response['FaceMatches'])
        external_image_ids = []
        if (number_of_faces):
            for FaceMatch in response['FaceMatches']:
                external_image_ids.append(FaceMatch['Face']['ExternalImageId'])
        return list(dict.fromkeys(external_image_ids))

    def move_image_from_temp_to_index(self, temp_file_path):
        file_name = temp_file_path.split('/')[-1]
        shutil.copy2(temp_file_path, self.INDEX_DIRECTORY + '/' + file_name)
    
    def clean_up(self):
        new_folders = [self.INDEX_DIRECTORY, self.RESIZED_IMAGE_DIRECTORY, self.TEMP_FOLDER]
        for folder in new_folders:
            if os.path.isdir(folder):
                shutil.rmtree(folder)
            os.makedirs(folder, exist_ok=True)

    def create_collections(self):
        self.rekognition_client.create_collection(CollectionId=self.REKOGNITION_COLLECTION_ID)
        self.rekognition_client.create_collection(CollectionId=self.REKOGNITION_INDEX_COLLECTION_ID)
        
    def delete_collections(self):
        self.rekognition_client.delete_collection(CollectionId=self.REKOGNITION_COLLECTION_ID)
        self.rekognition_client.delete_collection(CollectionId=self.REKOGNITION_INDEX_COLLECTION_ID)
