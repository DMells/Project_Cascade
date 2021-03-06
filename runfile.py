import argparse
import pandas as pd
import os
import ast
from pathlib import Path
import yaml
import settings
import datetime
import logging.config
import sys
from core.logging_config import config_stdout_root_logger_with_papertrail
from dotenv import load_dotenv
import sentry_sdk
sentry_sdk.init("https://e690e6e8120b4d38b909772ecf4380ce@sentry.io/4917852")


def createSettingsObj(rootdir, in_args, settings):

    # Silence warning for df['process_num'] = str(proc_num)
    pd.options.mode.chained_assignment = None

    if in_args.region == 'UK_entities':
        settings = settings.UK_entities

    if in_args.region == 'UK_suppliers':
        settings = settings.UK_suppliers

    # If any production flags are being called use production logger...
    if in_args.verified or in_args.unverified:
        config_stdout_root_logger_with_papertrail(app_name='entity_matching', level=logging.DEBUG)

    # ...else use local logger
    else:
        # Import logging configs
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f.read())
            logging.config.dictConfig(config)

        def exception_handler(type, value, tb):
            logging.exception('Uncaught exception: {0}'.format(str(value)))

        # Install exception handler
        sys.excepthook = exception_handler

    settings.in_args = in_args
    settings.region_dir = os.path.join(rootdir, 'Regions', in_args.region)

    # '.env_production' / '.env_staging'

    # Clear any existing db creds (in webapps these load automatically from an env file closer to the root)
    try:
        del os.environ["HOST_REMOTE"]
        del os.environ["DBNAME_REMOTE"]
        del os.environ["USER_REMOTE"]
        del os.environ["PASSWORD_REMOTE"]
    except:
        next
    # get the remote database details from .env
    if in_args.prodn:
        env_file = '.env_production'
    else:
        env_file = '.env_staging'
    load_dotenv(env_file)
    settings.host_remote = os.environ.get("HOST_REMOTE")
    settings.dbname_remote = os.environ.get("DBNAME_REMOTE")
    settings.user_remote = os.environ.get("USER_REMOTE")
    settings.password_remote = os.environ.get("PASSWORD_REMOTE")
    settings.aws_access_key_id = os.environ.get("aws_access_key_id")
    settings.aws_secret_access_key = os.environ.get("aws_secret_access_key")

    # Define config file variables and attach to settings object
    settings.config_path = Path(os.path.join(settings.region_dir, 'Config_Files'))

    return settings


def getInputArgs(rootdir, args=None):
    """
	Assign arguments including defaults to pass to the python call

	:return: arguments variable for both directory and the data file
	"""
    parser = argparse.ArgumentParser(conflict_handler='resolve') # conflict_handler allows overriding of args (for pytest purposes : see conftest.py::in_args())
    parser.add_argument('--region', default='UK_entities', type=str, help='Define the region/country (Italy/UK)')
    parser.add_argument('--src', default='source_data.csv', type=str,
                        help='Set raw source/source datafile name')
    parser.add_argument('--reg', default='registry_data.csv', type=str, help='Set raw registry datafile name')
    parser.add_argument('--src_adj', default='src_data_adj.csv', type=str,
                        help='Set cleaned source/source datafile name')
    parser.add_argument('--reg_adj', default='reg_data_adj.csv', type=str, help='Set cleaned registry datafile name')
    parser.add_argument('--recycle', action='store_true', help='Recycle the manual training data')
    parser.add_argument('--mtraining', action='store_true', help='Modify/contribute to the matching training data')
    parser.add_argument('--ctraining', action='store_true', help='Modify/contribute to the clustering training data')
    parser.add_argument('--convert_training', action='store_true',
                        help='Convert confirmed matches to training file for recycle phase')
    parser.add_argument('--config_review', action='store_true', help='Manually review/choose best config file results')
    parser.add_argument('--terminal_matching', action='store_true', help='Perform manual matching in terminal')
    parser.add_argument('--upload', action='store_true', help='Add confirmed matches to database')
    parser.add_argument('--clear_all', action='store_true', help='Clear all datafiles')
    parser.add_argument('--clear_adj', action='store_true', help='Clear all files except raw data')
    parser.add_argument('--clear_outputs', action='store_true', help='Clear all files except inputs')
    parser.add_argument('--clear_filtered', action='store_true', help='Clear all files after manual clustering phase')
    parser.add_argument('--clear_clustered', action='store_true', help='Clear all files after matching phase')
    parser.add_argument('--clear_manclustered', action='store_true', help='Clear all files after entire dedupe phase')
    parser.add_argument('--data_from_date', type=str,
                        default=(datetime.date.today() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
                        , help='Set source data start date to be downloaded from (inclusive)')
    parser.add_argument('--data_to_date', type=str, default=datetime.date.today().strftime('%Y-%m-%d'),
                        help='Set source data end date to be downloaded (inclusive)')
    parser.add_argument('--unverified', action='store_true', help='DO NOT USE - for production scripts only to transfer matches to s3 buckets ')
    parser.add_argument('--verified', action='store_true', help='DO NOT USE - for production scripts only to transfer matches to s3 buckets ')
    parser.add_argument('--split', action='store_true', help='split source file and initiate segmented matching')
    parser.add_argument('--splitsize', default=1000, type=int, help='split source file and initiate segmented matching')
    parser.add_argument('--prodn',action='store_true', help='used to obtain production env database settings. If not used, staging db creds used')
    # Added args as a parameter per https://stackoverflow.com/questions/55259371/pytest-testing-parser-error-unrecognised-arguments/55260580#55260 580
    pargs = parser.parse_args(args)

    return pargs, parser


class Main:
    def __init__(self, settings):
        # Defined in __main__
        self.directories = settings.directories
        self.in_args = settings.in_args
        self.region_dir = settings.region_dir
        self.config_path = settings.config_path
        self.settings = settings

        # Defined in settings file
        self.df_dtypes = settings.df_dtypes
        self.stats_cols = settings.stats_cols
        self.training_cols = settings.training_cols
        self.manual_matches_cols = settings.manual_matches_cols
        self.dbUpload_cols = settings.dbUpload_cols
        self.proc_type = settings.proc_type
        self.dedupe_cols = settings.dedupe_cols
        self.reg_data_source = settings.reg_data_source
        self.src_data_source = settings.src_data_source
        self.raw_src_data_cols = settings.raw_src_data_cols

        # Runfile modules
        self.runfile_mods = settings.runfile_mods
        self.data_processing = self.runfile_mods.data_processing
        self.data_analysis = self.runfile_mods.data_analysis
        self.db_calls = self.runfile_mods.db_calls
        self.setup = self.runfile_mods.setup
        self.data_matching = self.runfile_mods.data_matching
        self.convert_training = self.runfile_mods.convert_training
        self.org_suffixes = self.runfile_mods.org_suffixes
        self.match_filtering = self.runfile_mods.match_filtering

        # Defined during runtime
        self.main_proc = settings.main_proc
        self.configs = settings.configs
        self.conf_file_num = settings.conf_file_num
        self.proc_num = settings.proc_num
        self.upload_table = settings.upload_table
        self.transfer_table = settings.transfer_table
        self.best_config = settings.best_config

        # Dotenv vars
        # self.dotenv_file = settings.dotenv_file
        self.host_remote = settings.host_remote
        self.dbname_remote = settings.dbname_remote
        self.user_remote = settings.user_remote
        self.password_remote = settings.password_remote
        self.aws_access_key_id = settings.aws_access_key_id
        self.aws_secret_access_key = settings.aws_secret_access_key

    def run_main(self):
        if self.in_args.unverified:
            # Build project folders
            self.setup.Setup(self).setupRawDirs()

            # Delete csvs from previous runs
            self.setup.ClearFiles(self).clearFiles()

            # If not using recycle mode
            if not in_args.recycle:

                try:
                    # If registry/registry data file doesn't exist, pull from database
                    self.db_calls.FetchData.checkDataExists(self)
                except:
                    # Will fail if checkDataExists function doesn't exist (i.e. registry data sourced externally (not from db))
                    pass

            try:
                # For each config file read it and convert to dictionary for accessing
                pyfiles = "*_config.py"
                for conf_file in self.config_path.glob(pyfiles):
                    with open(conf_file) as config_file:
                        file_contents = []
                        file_contents.append(config_file.read())

                        # Convert list to dictionary
                        configs = ast.literal_eval(file_contents[0])
                        self.configs = configs

                        conf_file_num = int(conf_file.name[0])
                        self.conf_file_num = conf_file_num

                        # Clean registry and source datasets for linking
                        # source df needed in memory for stats
                        self.data_processing.ProcessSourceData(self).clean()

                        try:
                            self.data_processing.ProcessRegistryData(self).clean()
                        except FileNotFoundError:
                            # Skip if registry data not downloaded yet (i.e. UK)
                            next

                        # For each process type (eg: Name & Add, Name only) outlined in the configs file:
                        for proc_type in configs['processes']:
                            self.proc_type = proc_type

                            # Get first process number from config file
                            main_proc_num = min(configs['processes'][proc_type].keys())
                            main_proc_configs = configs['processes'][proc_type][main_proc_num]

                            # If args.recycle matches the recycle setting for the first process type
                            if in_args.recycle == main_proc_configs['recycle_phase']:

                                # Create working directories if don't exist
                                self.setup.Setup(self).SetupDirs()

                                # Iterate over each process number in the config file
                                for proc_num in configs['processes'][proc_type]:
                                    self.proc_num = proc_num

                                    # Run dedupe for matching and calculate related stats for comparison
                                    self.data_matching.Matching(self).dedupe()

                                    self.match_filtering.MatchFiltering(self).filter()

                                    self.match_filtering.MatchFiltering(self).getExcludedandNonMatches()

                                break
                            else:
                                continue
                        # Output stats files:
                        self.data_analysis.StatsCalculations(self).calculate_internals()

            except StopIteration:
                # Continue if no more config files found
                print("Done")

            self.data_analysis.StatsCalculations(self).calculate_externals() # long runtime - use concurrency here?
            self.best_config = self.match_filtering.VerificationAndUploads(self).verify()


        self.AWS_calls = self.runfile_mods.AWS_calls
        self.AWS_calls.AwsTransfers(self).transfer()


if __name__ == '__main__':
    rootdir = os.path.dirname(os.path.abspath(__file__))
    in_args, _ = getInputArgs(rootdir)
    settingsobj = createSettingsObj(rootdir, in_args, settings)
    Main(settingsobj).run_main()