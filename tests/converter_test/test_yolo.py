from pathlib import Path
import superannotate as sa


def yolo_object_detection(tmpdir):
    out_dir = tmpdir / "vector_annotation"
    sa.import_annotation_format(
        'tests/converter_test/YOLO/input/toSuperAnnotate', str(out_dir), 'YOLO',
        '', 'Vector', 'object_detection', 'Web'
    )

    project_name = "yolo_object_detection"

    projects = sa.search_projects(project_name, True)
    if projects:
        sa.delete_project(projects[0])
    project = sa.create_project(project_name, "converter vector", "Vector")

    sa.create_annotation_classes_from_classes_json(
        project, out_dir + "/classes/classes.json"
    )
    sa.upload_images_from_folder_to_project(project, out_dir)
    sa.upload_annotations_from_folder_to_project(project, out_dir)

    return 0


def test_yolo(tmpdir):
    assert yolo_object_detection(tmpdir) == 0