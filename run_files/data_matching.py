import pandas as pd
import os
import subprocess
import numpy as np
import sys
from shutil import copyfile
from Config_Files import config_dirs
import pdb
import runfile


def dedupe_matchTEST(priv_file, pub_file, rootdir, config_dirs, config_files, proc_type, proc_num, in_args):
    """
	Deduping - first the public and private data are matched using dedupes csvlink,
	then the matched file is put into clusters
	:param config_dirs: file/folder locations
	:param  config_files: the main config files
	:param proc_type: the 'type' of the process (Name, Name & Address)
	:param proc_num: the individual process within the config file
	:return None
	:output : matched output file
	:output : matched and clustered output file
	"""
    priv_fields = config_files['processes'][proc_type][proc_num]['dedupe_field_names']['private_data']
    pub_fields = config_files['processes'][proc_type][proc_num]['dedupe_field_names']['public_data']

    train = ['--skip_training' if in_args.training else '']
    # Matching:
    if not os.path.exists(config_dirs['match_output_file'].format(rootdir, proc_type)):
        if in_args.recycle:
            # Copy manual matching file over to build on for clustering
            copyfile(config_dirs['manual_matching_train_backup'].format(rootdir), config_dirs['manual_training_file'].format(rootdir, proc_type))

        # Remove learned_settings (created from previous runtime) file as causes dedupe to hang sometimes, but isn't required
        if os.path.exists('./learned_settings'):
            os.remove('./learned_settings')
        print("Starting matching...")

        cmd = ['csvlink '
               + str(priv_file) + ' '
               + str(pub_file)
               + ' --field_names_1 ' + ' '.join(priv_fields)
               + ' --field_names_2 ' + ' '.join(pub_fields)
               + ' --training_file ' + config_dirs['manual_training_file'].format(rootdir, proc_type)
               + ' --output_file ' + config_dirs['match_output_file'].format(rootdir, proc_type) + ' '
               + str(train[0])
               ]
        p = subprocess.Popen(cmd, shell=True)

        p.wait()
        df = pd.read_csv(config_dirs['match_output_file'].format(rootdir, proc_type),
                         usecols=['id', 'priv_name', 'priv_address', 'priv_name_adj', 'priv_address_adj', 'org_id', 'org_name',
                                  'pub_name_adj','pub_address_adj',
                                  'pub_address', 'pub_address_adj', 'privjoinfields', 'pubjoinfields'],
                         dtype={'id': np.str, 'priv_name': np.str, 'priv_address': np.str, 'priv_name_adj': np.str, 'priv_address_adj': np.str,
                                'org_id': np.str, 'org_name': np.str, 'pub_name_adj': np.str, 'pub_address': np.str, 'pub_address_adj': np.str, 'privjoinfields':np.str, 'pubjoinfields':np.str})
        df = df[pd.notnull(df['priv_name'])]
        df.to_csv(config_dirs['match_output_file'].format(rootdir, proc_type), index=False)


def dedupe_match_cluster(priv_file, pub_file, rootdir, config_dirs, config_files, proc_type, proc_num, in_args):
    """
	Deduping - first the public and private data are matched using dedupes csvlink,
	then the matched file is put into clusters
    :param pub_file:
    :param priv_file:
	:param config_dirs: file/folder locations
	:param  config_files: the main config files
	:param proc_type: the 'type' of the process (Name, Name & Address)
	:param proc_num: the individual process within the config file
	:return None
	:output : matched output file
	:output : matched and clustered output file
	"""

    priv_fields = config_files['processes'][proc_type][proc_num]['dedupe_field_names']['private_data']
    pub_fields = config_files['processes'][proc_type][proc_num]['dedupe_field_names']['public_data']

    train = ['--skip_training' if in_args.training else '']
    # Matching:
    if not os.path.exists(config_dirs['match_output_file'].format(rootdir, proc_type)):
        if in_args.recycle:
            # Copy manual matching file over to build on for clustering
            copyfile(config_dirs['manual_matching_train_backup'].format(rootdir), config_dirs['manual_training_file'].format(rootdir, proc_type))

        # Remove learned_settings (created from previous runtime) file as causes dedupe to hang sometimes, but isn't required
        if os.path.exists('./learned_settings'):
            os.remove('./learned_settings')
        print("Starting matching...")

        cmd = ['csvlink '
               + str(priv_file) + ' '
               + str(pub_file)
               + ' --field_names_1 ' + ' '.join(priv_fields)
               + ' --field_names_2 ' + ' '.join(pub_fields)
               + ' --training_file ' + config_dirs['manual_training_file'].format(rootdir, proc_type)
               + ' --output_file ' + config_dirs['match_output_file'].format(rootdir, proc_type) + ' '
               + str(train[0])
               ]
        p = subprocess.Popen(cmd, shell=True)

        p.wait()
        df = pd.read_csv(config_dirs['match_output_file'].format(rootdir, proc_type),
                         usecols=['id', 'priv_name', 'priv_address', 'priv_name_adj', 'priv_address_adj', 'org_id', 'org_name',
                                  'pub_name_adj', 'pub_address_adj',
                                  'pub_address', 'pub_address_adj', 'privjoinfields', 'pubjoinfields'],
                         dtype={'id': np.str, 'priv_name': np.str, 'priv_address': np.str, 'priv_name_adj': np.str, 'priv_address_adj': np.str,
                                'org_id': np.str, 'org_name': np.str, 'pub_name_adj': np.str, 'pub_address': np.str, 'pub_address_adj': np.str, 'privjoinfields':np.str, 'pubjoinfields':np.str})
        df = df[pd.notnull(df['priv_name'])]
        df.to_csv(config_dirs['match_output_file'].format(rootdir, proc_type), index=False)

    # Clustering:
    if not os.path.exists(config_dirs['cluster_output_file'].format(rootdir, proc_type)):
        # Copy training file from first clustering session if recycle mode
        if in_args.recycle:
            copyfile(config_dirs['cluster_training_backup'].format(rootdir), config_dirs['cluster_training_file'].format(rootdir, proc_type))

        print("Starting clustering...")
        cmd = ['python csvdedupe.py '
               + config_dirs['match_output_file'].format(rootdir, proc_type) + ' '
               + ' --field_names ' + ' '.join(priv_fields) + ' '
               + str(train[0])
               + ' --training_file ' + config_dirs['cluster_training_file'].format(rootdir, proc_type)
               + ' --output_file ' + config_dirs['cluster_output_file'].format(rootdir, proc_type)]
        p = subprocess.Popen(cmd, cwd=os.getcwd() + '/csvdedupe/csvdedupe', shell=True)
        p.wait()  # wait for subprocess to finish

        if not in_args.recycle:
            # Copy training file to backup, so it can be found and copied into recycle phase clustering
            copyfile(config_dirs['cluster_training_file'].format(rootdir, proc_type), config_dirs['cluster_training_backup'].format(rootdir))
    else:
        pass


def extract_matches(rootdir, clustdf, config_files, config_dirs, proc_num, proc_type, conf_file_num, in_args):
    """
	Import config file containing variable assignments for i.e. char length, match ratio
	Based on the 'cascading' config details, extract matches to new csv

	:return extracts_file: contains dataframe with possible acceptable matches
	"""

    if in_args.recycle:
        levendist = str('leven_dist_NA')
    else:
        levendist = str('leven_dist_N')


    # Round confidence scores to 2dp :
    # pdb.set_trace()
    clustdf['Confidence Score'] = clustdf['Confidence Score'].map(lambda x: round(x, 2))

    # Filter by current match_score:
    clustdf = clustdf[clustdf[levendist] >= config_files['processes'][proc_type][proc_num]['min_match_score']]

    # if the earliest process, accept current clustdf as matches, if not (>min):
    if proc_num > min(config_files['processes'][proc_type]):
        try:
            # Filter by char count and previous count (if exists):
            clustdf = clustdf[
                clustdf.priv_name_short.str.len() <= config_files['processes'][proc_type][proc_num]['char_counts']]
            clustdf = clustdf[
                clustdf.priv_name_short.str.len() > config_files['processes'][proc_type][proc_num - 1]['char_counts']]
            # Filter by < 99 as first proc_num includes all lengths leading to duplicates
            clustdf = clustdf[clustdf[levendist] <= 99]
        except:
            clustdf = clustdf[
                clustdf.priv_name_short.str.len() <= config_files['processes'][proc_type][proc_num]['char_counts']]
    else:
        if os.path.exists(config_dirs['extract_matches_file'].format(rootdir, proc_type) + '_' + str(conf_file_num) + '.csv'):
            # Clear any previous extraction file for this config:
            os.remove(config_dirs['extract_matches_file'].format(rootdir, proc_type) + '_' + str(conf_file_num) + '.csv')

    # Add process number to column for calculating stats purposes:
    clustdf['process_num'] = str(proc_num)

    if not os.path.exists(config_dirs['extract_matches_file'].format(rootdir, proc_type) + '_' + str(conf_file_num) + '.csv'):
        clustdf.to_csv(config_dirs['extract_matches_file'].format(rootdir, proc_type) + '_' + str(conf_file_num) + '.csv',
                       index=False)
        return clustdf
    else:
        extracts_file = pd.read_csv(
            config_dirs['extract_matches_file'].format(rootdir, proc_type) + '_' + str(conf_file_num) + '.csv', index_col=None)
        extracts_file = pd.concat([extracts_file, clustdf], ignore_index=True, sort=True)
        extracts_file.sort_values(by=['Cluster ID'], inplace=True, axis=0, ascending=True)
        extracts_file.to_csv(config_dirs['extract_matches_file'].format(rootdir, proc_type) + '_' + str(conf_file_num) + '.csv',
                             index=False)
        return extracts_file


def manual_matching(rootdir, config_dirs, best_config, proc_type, in_args):
    """
	Provides user-input functionality for manual matching based on the extracted records
	:return manual_match_file: extracted file with added column (Y/N/Unsure)
	"""

    manual_match_file = pd.read_csv(
        config_dirs['extract_matches_file'].format(rootdir, proc_type) + '_' + str(best_config) + '.csv', index_col=None)
    manual_match_file['Manual_Match_N'] = ''
    manual_match_file['Manual_Match_NA'] = ''

    # Automatically confirm rows with leven dist of 100
    for index, row in manual_match_file.iterrows():
        if row.leven_dist_N == 100:
            manual_match_file.at[index, 'Manual_Match_N'] = str('Y')
        if row.leven_dist_NA == 100:
            manual_match_file.at[index, 'Manual_Match_NA'] = str('Y')

    if in_args.terminal_matching:
        choices = ['n', 'na']
        choice = input("\nMatching name only or name and address? (N / NA):")
        while choice.lower() not in choices:
            choice = input("\nMatching name only or name and address? (N / NA):")

        # Iterate over the file, shuffled with sample, as best matches otherwise would show first:
        for index, row in manual_match_file.sample(frac=1).iterrows():
            if choice.lower() == 'n':
                print("\nPrivate name: " + str(row.priv_name_adj))
                print("\nPublic name: " + str(row.pub_name_adj))
                print("\nLevenshtein distance: " + str(row.leven_dist_N))
            else:
                print("\nPrivate name: " + str(row.priv_name_adj))
                print("Private address: " + str(row.priv_address_adj))
                print("\nPublic name: " + str(row.pub_name_adj))
                print("Public address: " + str(row.pub_address_adj))
                print("\nLevenshtein distance : " + str(row.leven_dist_NA))

            match_options = ["y", "n", "u", "f"]
            match = input("\nMatch? Yes, No, Unsure, Finished (Y/N/U/F):")
            while match.lower() not in match_options:
                match = input("\nMatch? Yes, No, Unsure, Finished (Y/N/U/F):")

            if str(match).lower() != "f":
                manual_match_file.at[index, 'Manual_Match_N'] = str(match).capitalize()
                # Need to add in NA version ? Might just remove terminal matching altogether...
                continue
            else:
                break

        manual_match_file.sort_values(by=['Cluster ID'], inplace=True, axis=0, ascending=True)

        print("Saving...")
        manual_match_file.to_csv(config_dirs['manual_matches_file'].format(rootdir, proc_type) + '_' + str(best_config) + '.csv',
                                 index=False,
                                 # columns=['org_id', 'id', 'org_name',
                                 #          'priv_name','pub_address', 'priv_address', 'leven_dist_N', 'leven_dist_NA','Manual_Match_N','Manual_Match_NA'])
                                columns = ['Cluster ID', 'leven_dist_N', 'leven_dist_NA', 'org_id', 'id', 'org_name', 'pub_name_adj',
                                           'pub_address', 'priv_name', 'priv_name_adj', 'priv_address', 'priv_address_adj', 'pub_address_adj',
                                           'Manual_Match_N', 'Manual_Match_NA', 'privjoinfields', 'pubjoinfields'])
        return manual_match_file

    else:
        manual_match_file.to_csv(config_dirs['manual_matches_file'].format(rootdir, proc_type) + '_' + str(best_config) + '.csv',
                                 index=False,
                                 # columns=['org_id', 'id', 'org_name',
                                 #          'priv_name', 'pub_address', 'priv_address', 'leven_dist_N', 'leven_dist_NA',
                                 #          'Manual_Match_N', 'Manual_Match_NA'])
                                 columns=['Cluster ID', 'leven_dist_N', 'leven_dist_NA', 'org_id', 'id', 'org_name', 'pub_name_adj',
                                          'pub_address','priv_name', 'priv_name_adj', 'priv_address', 'priv_address_adj', 'pub_address_adj', 'Manual_Match_N','Manual_Match_NA', 'privjoinfields', 'pubjoinfields'])
        if not in_args.recycle:
            if not in_args.upload_to_db:
                print("\nIf required, please perform manual matching process in {} and then run 'python runfile.py --convert_training --upload_to_db".format(
                config_dirs['manual_matches_file'].format(rootdir, proc_type) + '_' + str(best_config) + '.csv'))
        else:
            if not in_args.upload_to_db:
                print("\nIf required, please perform manual matching process in {} and then run 'python runfile.py --recycle --upload_to_db".format(
                    config_dirs['manual_matches_file'].format(rootdir, proc_type) + '_' + str(best_config) + '.csv'))