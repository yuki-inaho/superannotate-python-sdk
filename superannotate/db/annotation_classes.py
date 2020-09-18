import io
import json
import logging
from pathlib import Path

import boto3

from ..api import API
from ..exceptions import (
    SABaseException, SAExistingAnnotationClassNameException,
    SANonExistingAnnotationClassNameException
)
from .project import get_project_metadata

logger = logging.getLogger("superannotate-python-sdk")

_api = API.get_instance()


def create_annotation_class(project, name, color, attribute_groups=None):
    """Create annotation class in project

    :param project: project name or metadata of the project
    :type project: str or dict
    :param name: name for the class
    :type name: str
    :param color: RGB hex color value, e.g., "#FFFFAA"
    :type color: str
    :param attribute_groups: example:
     [ { "name": "tall", "is_multiselect": 0, "attributes": [ { "name": "yes" }, { "name": "no" } ] },
     { "name": "age", "is_multiselect": 0, "attributes": [ { "name": "young" }, { "name": "old" } ] } ]
    :type attribute_groups: list of dicts

    :return: new class metadata
    :rtype: dict
    """
    if not isinstance(project, dict):
        project = get_project_metadata(project)
    try:
        get_annotation_class_metadata(project, name)
    except SANonExistingAnnotationClassNameException:
        pass
    else:
        logger.warning(
            "Annotation class %s already in project. Skipping.", name
        )
        return None
    team_id, project_id = project["team_id"], project["id"]
    logger.info(
        "Creating annotation class in project %s with name %s", project["name"],
        name
    )
    params = {
        'team_id': team_id,
        'project_id': project_id,
    }
    data = {
        "classes":
            [
                {
                    "name":
                        name,
                    "color":
                        color,
                    "attribute_groups":
                        attribute_groups if attribute_groups is not None else []
                }
            ]
    }
    response = _api.send_request(
        req_type='POST', path='/classes', params=params, json_req=data
    )
    if not response.ok:
        raise SABaseException(
            response.status_code, "Couldn't create class " + response.text
        )
    res = response.json()
    new_class = res[0]
    return new_class


def delete_annotation_class(project, annotation_class):
    """Deletes annotation class from project

    :param project: project name or metadata of the project
    :type project: str or dict
    :param project: annotation class name or  metadata
    :type project: str or dict
    """
    if not isinstance(project, dict):
        project = get_project_metadata(project)
    if not isinstance(annotation_class, dict):
        annotation_class = get_annotation_class_metadata(
            project, annotation_class
        )
    team_id, project_id, name, class_id = _api.team_id, annotation_class[
        "project_id"], annotation_class["name"], annotation_class["id"]
    logger.info(
        "Deleting annotation class from project %s with name %s",
        project["name"], name
    )
    params = {
        'team_id': team_id,
        'project_id': project_id,
    }
    response = _api.send_request(
        req_type='DELETE', path=f'/class/{class_id}', params=params
    )
    if not response.ok:
        raise SABaseException(
            response.status_code,
            "Couldn't delete annotation class " + response.text
        )


def create_annotation_classes_from_classes_json(
    project, classes_json, from_s3_bucket=None
):
    """Creates annotation classes in project from a SuperAnnotate format
    annotation classes.json.

    :param project: project name or metadata of the project
    :type project: str or dict
    :param classes_json: JSON itself or path to the JSON file
    :type classes_json: dict or Pathlike (str or Path)
    :param from_s3_bucket: AWS S3 bucket to use. If None then classes_json is in local filesystem
    :type from_s3_bucket: str

    :return: list of created annotation class metadatas
    :rtype: list of dicts
    """
    if not isinstance(project, dict):
        project = get_project_metadata(project)
    team_id, project_id = project["team_id"], project["id"]
    if not isinstance(classes_json, dict):
        logger.info(
            "Creating annotation classes in project %s from %s.",
            project["name"], classes_json
        )
        if from_s3_bucket is None:
            classes = json.load(open(classes_json))
        else:
            from_session = boto3.Session()
            from_s3 = from_session.resource('s3')
            file = io.BytesIO()
            from_s3_object = from_s3.Object(from_s3_bucket, classes_json)
            from_s3_object.download_fileobj(file)
            file.seek(0)
            classes = json.load(file)
    else:
        classes = classes_json

    existing_classes = search_annotation_classes(project)
    new_classes = []
    for cs in classes:
        if cs["name"] in existing_classes:
            logger.warning(
                "Annotation class %s already in project. Skipping.", cs
            )
        else:
            new_classes.append(cs)

    params = {
        'team_id': team_id,
        'project_id': project_id,
    }
    data = {"classes": new_classes}
    response = _api.send_request(
        req_type='POST', path='/classes', params=params, json_req=data
    )
    if not response.ok:
        raise SABaseException(
            response.status_code, "Couldn't create classes " + response.text
        )
    res = response.json()
    return res


def search_annotation_classes(project, name_prefix=None, return_metadata=False):
    """Searches annotation classes by name_prefix (case-insensitive)

    :param project: project name or metadata of the project
    :type project: str or dict
    :param name_prefix: name prefix for search. If None all annotation classes
     will be returned
    :type name_prefix: str

    :return: annotation classes of the project
    :rtype: list of dicts
    """
    if not isinstance(project, dict):
        project = get_project_metadata(project)
    result_list = []
    team_id, project_id = project["team_id"], project["id"]
    params = {'team_id': team_id, 'project_id': project_id, 'offset': 0}
    if name_prefix is not None:
        params['name'] = name_prefix
    while True:
        response = _api.send_request(
            req_type='GET', path='/classes', params=params
        )
        if not response.ok:
            raise SABaseException(
                response.status_code, "Couldn't search classes " + response.text
            )
        res = response.json()
        result_list += res["data"]
        new_len = len(result_list)
        # for r in result_list:
        #     print(r)
        if res["count"] <= new_len:
            break
        params["offset"] = new_len

    if return_metadata:
        return result_list
    else:
        return [x["name"] for x in result_list]


def get_annotation_class_metadata(project, annotation_class_name):
    """Returns annotation class metadata

    :param project: project name or metadata of the project
    :type project: str or dict
    :param annotation_class_name: annotation class name
    :type annotation_class_name: str

    :return: metadata of annotation class
    :rtype: dict
    """
    annotation_classes = search_annotation_classes(
        project, annotation_class_name, return_metadata=True
    )
    results = []
    for annotation_class in annotation_classes:
        if annotation_class["name"] == annotation_class_name:
            results.append(annotation_class)

    if len(results) > 1:
        raise SAExistingAnnotationClassNameException(
            0, "Annotation class name " + annotation_class_name +
            " is not unique. To use SDK please make annotation class names unique."
        )
    elif len(results) == 1:
        return results[0]
    else:
        raise SANonExistingAnnotationClassNameException(
            0, "Annotation class with name " + annotation_class_name +
            " doesn't exist."
        )


def download_annotation_classes_json(project, folder):
    """Downloads project classes.json to folder

    :param project: project name or metadata of the project
    :type project: str or dict
    :param folder: folder to download to
    :type folder: Pathlike (str or Path)

    :return: path of the download file
    :rtype: str
    """
    if not isinstance(project, dict):
        project = get_project_metadata(project)
    logger.info(
        "Downloading classes.json from project %s to folder %s.",
        project["name"], folder
    )
    clss = search_annotation_classes(project, return_metadata=True)
    filepath = Path(folder) / "classes.json"
    json.dump(clss, open(filepath, "w"), indent=4)
    return str(filepath)
