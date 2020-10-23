from shapely.geometry import Polygon, box, Point
import plotly.express as px
import logging

logger = logging.getLogger("superannotate-python-sdk")


def instance_consensus(inst_1, inst_2):
    """Helper function that computes consensus score between two instances:

    :param inst_1: First instance for consensus score.
    :type inst_1: shapely object
    :param inst_2: Second instance for consensus score.
    :type inst_2: shapely object

    """
    if inst_1.type == inst_2.type == 'Polygon':
        intersect = inst_1.intersection(inst_2)
        union = inst_1.union(inst_2)
        score = intersect.area / union.area
    elif inst_1.type == inst_2.type == 'Point':
        score = -1 * inst_1.distance(inst_2)
    else:
        raise NotImplementedError

    return score


def image_consensus(df, image_name, annot_type):
    """Helper function that computes consensus score for instances of a single image:

    :param df: Annotation data of all images
    :type df: pandas.DataFrame
    :param image_name: The image name for which the consensus score will be computed
    :type image_name: str
    :param annot_type: Type of annotation instances to consider. Available candidates are: ["bbox", "polygon", "point"]
    :type dataset_format: str

    """
    image_df = df[df["imageName"] == image_name]
    all_projects = list(set(df["project"]))
    column_names = [
        "creatorEmail", "imageName", "instanceId", "area", "className",
        "attributeGroupName", "attributeName"
    ]
    column_names.extend(all_projects)
    instance_id = 0
    image_data = {}
    for column_name in column_names:
        image_data[column_name] = []

    projects_shaply_objs = {}
    # generate shapely objects of instances
    for _, row in image_df.iterrows():
        if row["project"] not in projects_shaply_objs:
            projects_shaply_objs[row["project"]] = []
        inst_data = row["meta"]
        if annot_type == 'bbox':
            inst_coords = inst_data["points"]
            x1, x2 = inst_coords["x1"], inst_coords["x2"]
            y1, y2 = inst_coords["y1"], inst_coords["y2"]
            inst = box(min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
        elif annot_type == 'polygon':
            inst_coords = inst_data["points"]
            shapely_format = []
            for i in range(0, len(inst_coords) - 1, 2):
                shapely_format.append((inst_coords[i], inst_coords[i + 1]))
            inst = Polygon(shapely_format)
        elif annot_type == 'point':
            inst = Point(inst_data["x"], inst_data["y"])
        if inst.is_valid:
            projects_shaply_objs[row["project"]].append(
                (
                    inst, row["className"], row["creatorEmail"],
                    row["attributeGroupName"], row["attributeName"]
                )
            )
        else:
            logger.info(
                "Invalid %s instance occured, skipping to the next one.",
                annot_type
            )

    # match instances
    for curr_proj, curr_proj_instances in projects_shaply_objs.items():
        for curr_inst_data in curr_proj_instances:
            curr_inst, curr_class, _, _, _ = curr_inst_data
            max_instances = []
            for other_proj, other_proj_instances in projects_shaply_objs.items(
            ):
                if curr_proj == other_proj:
                    max_instances.append((curr_proj, *curr_inst_data))
                    projects_shaply_objs[curr_proj].remove(curr_inst_data)
                else:
                    max_score = float('-inf')
                    max_inst_data = None
                    for other_inst_data in other_proj_instances:
                        other_inst, other_class, _, _, _ = other_inst_data
                        score = instance_consensus(curr_inst, other_inst)
                        if score > max_score and other_class == curr_class:
                            max_score = score
                            max_inst_data = other_inst_data
                    if max_inst_data is not None:
                        max_instances.append((other_proj, *max_inst_data))
                        projects_shaply_objs[other_proj].remove(max_inst_data)
            if len(max_instances) == 1:
                image_data["creatorEmail"].append(max_instances[0][3])
                image_data["attributeGroupName"].append(max_instances[0][4])
                image_data["attributeName"].append(max_instances[0][5])
                image_data["area"].append(max_instances[0][1].area)
                image_data["imageName"].append(image_name)
                image_data["instanceId"].append(instance_id)
                image_data["className"].append(max_instances[0][2])
                for project in all_projects:
                    if project == max_instances[0][0]:
                        image_data[project].append(0)
                    else:
                        image_data[project].append(None)
            else:
                for curr_match_data in max_instances:
                    proj_cons = 0
                    for other_match_data in max_instances:
                        if curr_match_data[0] != other_match_data[0]:
                            score = instance_consensus(
                                curr_match_data[1], other_match_data[1]
                            )
                            proj_cons += (1. if score < 0 else score)
                    image_data["creatorEmail"].append(curr_match_data[3])
                    image_data["attributeGroupName"].append(curr_match_data[4])
                    image_data["attributeName"].append(curr_match_data[5])
                    image_data["area"].append(curr_match_data[1].area)
                    image_data["imageName"].append(image_name)
                    image_data["instanceId"].append(instance_id)
                    image_data["className"].append(curr_match_data[2])
                    for project in all_projects:
                        if project == curr_match_data[0]:
                            image_data[project].append(
                                proj_cons / (len(all_projects) - 1)
                            )
                        else:
                            image_data[project].append(None)
            instance_id += 1

    return image_data


def consensus_plot(consensus_df, projects):
    plot_data = consensus_df.copy()

    #annotator-wise boxplot
    plot_data["instance_score"] = plot_data[projects].mean(axis=1)
    annot_box_fig = px.box(
        plot_data, x="creatorEmail", y="instance_score", points="all"
    )
    annot_box_fig.show()

    #project-wise boxplot
    plot_data["instance_project"] = (
        plot_data[projects].notna().astype('int') == 1
    ).idxmax(1)
    project_box_fig = px.box(
        plot_data, x="instance_project", y="instance_score", points="all"
    )
    project_box_fig.show()

    #instance areas histogram colored by class
    area_hist = px.histogram(plot_data, x="area", color="className")
    area_hist.show()