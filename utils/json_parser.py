import json


class JsonParser:

    def write_json_to_file(self, output_file_path: str, output_data: dict) -> None:
        with open(output_file_path, 'w+') as json_file:
            json.dump(output_data, json_file, indent=4)

    def read_json_from_file(self, input_file_path: str) -> dict:
        with open(input_file_path, 'r') as json_file:
            return json.load(json_file)
