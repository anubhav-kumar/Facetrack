import os
import ImageRecognition

index_folder_path = "./images-index"

index_photos = [f for f in os.listdir(index_folder_path) if os.path.isfile(os.path.join(index_folder_path, f))]
rek = ImageRecognition.ImageRecognition(1)

for index_photo in index_photos:
    index_photo_path = './images-index/' + index_photo
    matching_ext_ids = rek.search_image_in_collection(index_photo_path, 'main')
    print("*" * 20)
    print("All Photos of " + index_photo.split('.')[-2])
    for matching_ext_id in matching_ext_ids:
        print(matching_ext_id)
print("*" * 20)
