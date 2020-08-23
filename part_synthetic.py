import random 
import os
import time

import pandas as pd
import numpy as np
from sklearn.metrics import normalized_mutual_info_score

import filepath
from DataDescriber import DataDescriber
from DataGenerator import DataGenerator
from ModelInspector import ModelInspector
from lib.utils import read_json_file

part_attribute_datatype = {
    'age': 'Integer'
}


part_attribute_categorical = {
    'age': False
}

def describe_ori_synthetic_data(
    mode: str, 
    data_filepath: str,
    description_filepath:str
    ):

    attribute_datatype = {
        'sex': 'String',
        'age': 'Integer',
        'loc': 'String',
        'salary': 'Integer'
    }

    attribute_categorical = {
        'sex': True,
        'age': False,
        'loc': True,
        'salary': False
    }
    
    describer = DataDescriber()

    describer.describe_dataset_in_independent_attribute_mode(
        dataset_file=data_filepath,
        attribute_to_datatype=attribute_datatype,
        attribute_to_is_categorical=attribute_categorical
    )

    describer.save_dataset_description_to_file(description_filepath)

def describe_part_synthetic_data(
    mode: str, 
    data_filepath: str,
    description_filepath:str
    ):
    
    describer = DataDescriber()

    describer.describe_dataset_in_independent_attribute_mode(
        dataset_file=data_filepath,
        attribute_to_datatype=part_attribute_datatype,
        attribute_to_is_categorical=part_attribute_categorical
    )

    describer.save_dataset_description_to_file(description_filepath)

def generate_part_synthetic_data(
    mode: str,
    num_rows: int,
    description_filepath: str,
    synthetic_data_filepath: str,
    rseed=0
    ):

    generator = DataGenerator()

    generator.generate_dataset_in_independent_mode(num_rows, description_filepath, seed=rseed)
    generator.save_synthetic_data(synthetic_data_filepath)

def compare_histograms_part(
        mode: str, 
        data_df: pd.DataFrame, 
        description_filepath: str,
        synthetic_data_filepath: str,
        plot_filepath: str
    ):

    synthetic_df = pd.read_csv(synthetic_data_filepath)
    attribute_description = read_json_file(description_filepath)['attribute_description']
    print(data_df.columns)
    print(synthetic_df.columns)
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
    data_df['age'].to_csv(filepath.column_data_file, header=['age'], index=False)
    num_rows = len(data_df)

    describe_part_synthetic_data('part', filepath.column_data_file, filepath.json_file)

    # generation start 
    generate_part_synthetic_data('part', num_rows, filepath.json_file, filepath.synthetic_data_file)
    min_synth_df = pd.read_csv(filepath.synthetic_data_file)
    min_similar = normalized_mutual_info_score(data_df['age'].astype(str), min_synth_df['age'].astype(str), average_method='arithmetic')
    
    for i in range(1,10):
        generate_part_synthetic_data('part', num_rows, filepath.json_file, filepath.synthetic_data_file, i)

        synth_df = pd.read_csv(filepath.synthetic_data_file)
        similar = normalized_mutual_info_score(data_df['age'].astype(str), synth_df['age'].astype(str), average_method='arithmetic')

        if min_similar < similar:
            min_synth_df = synth_df
            min_similar = similar
        print(min_similar)

    synth_df = data_df
    synth_df['age'] = min_synth_df['age']
    synth_df.to_csv(filepath.synthetic_data_file, index=False)

    describe_ori_synthetic_data('part', filepath.data_file, filepath.json_file)
    compare_histograms_part('part', data_df, filepath.json_file, filepath.synthetic_data_file, filepath.plot_dir)

if __name__ == "__main__":
    start = time.time()
    main()
    elapsed = round(time.time() - start, 2)
    print('done in ' + str(elapsed) + ' seconds.')
