import csv

def csv_to_list(file_path):
    new_list = []
    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            new_list.append(row)
    return new_list


def csv_to_dict_list(csv_file_path):
    dict_list = []
    with open(csv_file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            dict_list.append(row)
    return dict_list

def dict_list_to_csv(dict_list, info_local_file_path):
    fieldnames = set().union(*(internal_dict.keys() for internal_dict in dict_list)) if dict_list else []
    with open(info_local_file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(dict_list)


def list_to_csv(list_object, file_path):
    with open(file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        for item in list_object:
            writer.writerow([item])