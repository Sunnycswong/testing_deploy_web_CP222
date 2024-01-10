import re

def extract_html_string(data_string):
    pattern = r"<table>.*<\/table>"
    matches = re.findall(pattern, data_string, re.DOTALL)
    return matches

def remove_str_in_json(obj, target_string):
    modified_obj = obj.replace(target_string,"TOBEREPLACED")
    return modified_obj