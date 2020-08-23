import random 
import os
import time

import pandas as pd
import numpy as np

import filepath
from DataDescriber import DataDescriber
from DataGenerator import DataGenerator
from ModelInspector import ModelInspector
from lib.utils import read_json_file

attribute_datatype = {
    'sex': 'String',
    'age': 'Integer',
    'loc': 'String',
    'salary': 'Integer'
}

attribute_categorical = {
    'sex': True,
    'age': True,
    'loc': True,
    'salary': False
}

def describe_synthetic_data(
    mode: str, 
    data_filepath: str,
    description_filepath:str
    ):
    
    describer = DataDescriber()

    epsilon = 0
    degree_of_bayesian_network = 1

    describer.describe_dataset_in_correlated_attribute_mode(
        dataset_file=data_filepath,
        epsilon=epsilon,
        k=degree_of_bayesian_network,
        attribute_to_datatype=attribute_datatype,
        attribute_to_is_categorical=attribute_categorical
    )

    describer.save_dataset_description_to_file(description_filepath)

def generate_synthetic_data(
    mode: str,
    num_rows: int,
    description_filepath: str,
    synthetic_data_filepath: str
    ):

    generator = DataGenerator()

    generator.generate_dataset_in_correlated_attribute_mode(num_rows, description_filepath)
    generator.save_synthetic_data(synthetic_data_filepath)

def compare_histograms(
        mode: str, 
        data_df: pd.DataFrame, 
        description_filepath: str,
        synthetic_data_filepath: str,
        plot_filepath: str
    ):

    synthetic_df = pd.read_csv(synthetic_data_filepath)
    print(data_df.columns)
    print(synthetic_df.columns)
    attribute_description = read_json_file(description_filepath)['attribute_description']
    inspector = ModelInspector(data_df, synthetic_df, attribute_description)
    print(data_df.columns)
    print(synthetic_df.columns)
    
    for attribute in synthetic_df.columns:
        figure_filepath = os.path.join(plot_filepath, mode + '_' + attribute + '.png')
        inspector.compare_histograms(attribute, figure_filepath)
    
    mutual_figure_filepath = os.path.join(plot_filepath, 'mutual_information_heatmap_' + mode + '.png')
    inspector.mutual_information_heatmap(mutual_figure_filepath)

def main():
    
    data_df = pd.read_csv(filepath.data_file)
    num_rows = len(data_df)
    print(data_df.columns)

    describe_synthetic_data('full', filepath.data_file, filepath.json_file)
    generate_synthetic_data('full', num_rows, filepath.json_file, filepath.synthetic_data_file)
    compare_histograms('full', data_df, filepath.json_file, filepath.synthetic_data_file, filepath.plot_dir)
    
# multiprocessing guard for Windows.
# REMEMBER! DO NOT REMOVE THIS CODE!!!
if __name__ == "__main__":
    start = time.time()
    main()
    elapsed = round(time.time() - start, 2)
    print('done in ' + str(elapsed) + ' seconds.')