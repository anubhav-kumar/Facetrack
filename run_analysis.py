import ImageRecognition

rek = ImageRecognition.ImageRecognition(1)
rek.clean_up()
rek.create_collections()
rek.resize_all_images()
resized_image_paths = rek.get_all_resized_images()

for resized_image_path in resized_image_paths:
    bounding_rects = rek.index_image(resized_image_path, 'main')
    temp_output_images = rek.crop_image_by_path_and_bounding_rects(resized_image_path, bounding_rects)

    for temp_output_image in temp_output_images:
        matching_ext_ids = rek.search_image_in_collection(temp_output_image, 'index')
        if (len(matching_ext_ids) == 0):
            rek.index_image(temp_output_image, 'index')
            rek.move_image_from_temp_to_index(temp_output_image)

# rek.delete_collections()
# rek.clean_up()
            
    
