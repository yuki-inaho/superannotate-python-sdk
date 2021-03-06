import os
import json
import superannotate as sa


def test_conversion(tmpdir):
    input_dir = "tests/converter_test/COCO/input/fromSuperAnnotate/cats_dogs_vector_instance_segm"
    temp_dir = tmpdir / 'output_Desktop'
    final_dir = tmpdir / 'output_Web'

    sa.convert_platform(str(input_dir), str(temp_dir), "Web")
    sa.convert_platform(str(temp_dir), str(final_dir), "Desktop")

    init_jsons = [file for file in os.listdir(input_dir) if '.json' in file]
    final_jsons = [file for file in os.listdir(final_dir) if '.json' in file]
    assert set(init_jsons) == set(final_jsons)

    init_file_names = set(
        [file.replace('___objects.json', '') for file in init_jsons]
    )
    temp_file_names = set(
        json.load(open(os.path.join(temp_dir, 'annotations.json'))).keys()
    )
    final_file_names = set(
        [file.replace('___objects.json', '') for file in final_jsons]
    )

    assert init_file_names == temp_file_names
    assert init_file_names == final_file_names
