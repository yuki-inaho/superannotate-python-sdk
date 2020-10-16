from pathlib import Path
import json


class VoTTConverter(object):
    def __init__(self, args):
        self.dataset_name = args.dataset_name
        self.project_type = args.project_type
        self.task = args.task
        self.output_dir = args.output_dir
        self.export_root = args.export_root
        self.direction = args.direction

    def set_output_dir(self, output_dir_):
        self.output_dir = output_dir_

    def set_export_root(self, export_root_):
        self.export_root = export_root_

    def set_dataset_name(self, dname):
        self.dataset_name = dname

    def get_file_list(self):
        json_file_list = []
        path = Path(self.export_root)
        if self.dataset_name != '':
            json_file_list.append(path.joinpath(self.dataset_name + '.json'))
        else:
            file_generator = path.glob('*.json')
            for gen in file_generator:
                json_file_list.append(gen)

        return json_file_list

    def save_objects(self, files_dict):
        for key, value in files_dict.items():
            path = Path(self.output_dir)
            with open(path.joinpath(key), 'w') as fw:
                json.dump(value, fw, indent=2)

    def save_classes(self, classes):
        path = Path(self.output_dir)
        with open(path.joinpath('classes', 'classes.json'), 'w') as fw:
            json.dump(classes, fw)