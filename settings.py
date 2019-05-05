import numpy as np
import directories
from Regions.Italy import Regional_Run_Files as ITA_run_files
from Regions.UK import Regional_Run_Files as UK_run_files


class Italy_Settings:

    runfile_mods = ITA_run_files

    df_dtypes = {'Cluster ID': np.float64, 'Confidence Score': np.float, 'id': np.str, 'src_name': np.str,
                 'src_address': np.str,
                 'src_address_adj': np.str, 'src_name_adj': np.str, 'reg_id': np.str, 'reg_name_adj': np.str,
                 'reg_address': np.str,
                 'reg_address_adj': np.str, 'src_name_short': np.str, 'reg_name_short': np.str, 'leven_dist_N': np.int,
                 'leven_dist_NA': np.int,
                 'reg_name': np.str, 'srcjoinfields': np.str, 'regjoinfields': np.str}

    training_cols = ['src_name_adj', 'src_address_adj', 'reg_name_adj', 'reg_address_adj', 'Manual_Match_N',
                     'Manual_Match_NA']

    dbUpload_cols = ['src_name', 'src_address', 'reg_id', 'reg_name', 'reg_address', 'Manual_Match_N',
                     'Manual_Match_NA']

    registryTableSource = "spaziodati.sd_sample"

    directories = directories.dirs["dirs"]

    # Needed to kick start the setup dirs function
    proc_type = 'Name_Only'

    dedupe_cols = ['id', 'src_name', 'src_address', 'src_name_adj', 'src_address_adj', 'reg_id',
                    'reg_name',
                    'reg_name_adj', 'reg_address_adj',
                    'reg_address', 'reg_address_adj', 'srcjoinfields', 'regjoinfields']

    stats_cols = ['Config_File', 'Total_Matches', 'Percent_Matches', 'Optim_Matches', 'Percent_Precision',
                     'Percent_Recall', 'Leven_Dist_Avg']

    manual_matches_cols = ['Cluster ID', 'leven_dist_N', 'leven_dist_NA', 'reg_id', 'id', 'reg_name', 'reg_name_adj',
                                           'reg_address', 'src_name', 'src_name_adj', 'src_address', 'src_address_adj', 'reg_address_adj',
                                           'Manual_Match_N', 'Manual_Match_NA', 'srcjoinfields', 'regjoinfields']

    proc_num = int
    best_config = int

class UK_Settings:

    runfile_mods = UK_run_files

    df_dtypes = {'Cluster ID': np.float64, 'Confidence Score': np.float, 'id': np.float, 'src_name': np.str,
             'src_name_adj': np.str, 'CH_id': np.str, 'CH_name_adj': np.str,
                 'CH_address': np.str, 'src_name_short': np.str, 'CH_name_short': np.str, 'leven_dist_N': np.int,
                 'reg_name': np.str, 'home_page_text' : np.str, 'about_or_contact_text' : np.str}

    training_cols = ['src_name', 'CH_name', 'Manual_Match_N', 'company_url', 'CH_id', 'CH_address', 'leven_dist_N']

    manual_matches_cols = ['src_name', 'CH_name', 'Manual_Match_N', 'about_or_contact_text', 'company_url', 'home_page_text', 'CH_id',
     'CH_address', 'src_name_short', 'CH_name_short', 'leven_dist_N']

    registryTableSource = str
    # Need to define proc_num here otherwise will not be carried through as part of 'self'
    proc_num = int
    conf_file_num = int
    configs = dict
    main_proc = int
    upload_table = str

    directories = directories.dirs["dirs"]

    # Needed to kick start the setup dirs function as proc_type usually
    # defined after the directories are setup (which doesnt make sense - fix this)
    proc_type = 'Name_Only'

    stats_cols = ['Config_File', 'Total_Matches', 'Percent_Matches', 'Optim_Matches', 'Percent_Precision',
                  'Percent_Recall', 'Leven_Dist_Avg']

    dbUpload_cols = ['src_name', 'CH_name', 'Manual_Match_N', 'company_url', 'CH_id',  'CH_address',  'leven_dist_N']

    best_config = int
