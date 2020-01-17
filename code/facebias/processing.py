"""
Functions to process the bfw data
"""
import sys
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics.pairwise import cosine_similarity

if __name__=="__main__":
    sys.path.append("..")

from facebias.io import load_features_from_image_list


def get_attribute_gender_ethnicity(data, path_col, col_suffix=""):
    attribute_col = f"att{col_suffix}"
    ethnicity_col = f"e{col_suffix}"
    gender_col = f"g{col_suffix}"
    label_col = f"a{col_suffix}"

    data[attribute_col] = data[path_col].apply(lambda x: x.split("/")[0])
    data[ethnicity_col] = data[attribute_col].apply(lambda x: x.split("_")[0][0].upper())
    data[gender_col] = data[attribute_col].apply(lambda x: x.split("_")[1][0].upper())
    data[label_col] = data[ethnicity_col] + data[gender_col]

    for col in [attribute_col, ethnicity_col, gender_col, label_col]:
        data[col] = data[col].astype("category")

    return data


def assign_person_unique_id(data):
    le = LabelEncoder()

    subject_names = list(set(
        ["/".join(p1.split('/')[:-1]) for p1 in data["p1"].unique()] +
        ["/".join(p2.split('/')[:-1]) for p2 in data["p2"].unique()]))
    le.fit(subject_names)

    data["ids1"] = le.transform(data["p1"].apply(lambda x: "/".join(x.split("/")[:-1])))
    data["ids2"] = le.transform(data["p2"].apply(lambda x: "/".join(x.split("/")[:-1])))

    return data


def compute_score_into_table(data, dir_features):
    # create ali_images list of all faces (i.e., unique set)
    image_list = list(np.unique(data["p1"].to_list() + data["p2"].to_list()))

    # read features as a dictionary, with keys set as the filepath of the image with values set as the face encodings
    features = load_features_from_image_list(image_list, dir_features, ext_feat="npy")

    # score all feature pairs by calculating cosine similarity of the features
    data["score"] = data.apply(lambda x: cosine_similarity(features[x["p1"]], features[x["p2"]])[0][0], axis=1)

    return data


def load_image_pair_with_attribute_and_score(image_pair_path, dir_features):
    data = pd.read_csv(image_pair_path)
    data = get_attribute_gender_ethnicity(data, "p1", "1")
    data = get_attribute_gender_ethnicity(data, "p2", "2")
    data = assign_person_unique_id(data)
    data = compute_score_into_table(data, dir_features)

    return data
