import os
from typing import List
import errno
from datetime import datetime
from random import SystemRandom
import numpy as np
import pandas as pd


class DataCollector:
    """Class responsible for collecting data from the simulation and saving it to csv files.

    Args:
        sim_filename (str): Name of the simulation for saving purposes
        steps_to_measure (int, optional): Steps to calculate moving average. Defaults to 100.
        custom_path (str, optional): Custom path to save the files. Defaults to ''.
        additional_folders (List[str], optional): additional folders to add in path to distingish simulations.
        Defaults to None.
        debug (bool, optional): Debug flag to save debuging data. Defaults to False.
    """

    def __init__(self, sim_filename: str = "default",
                 steps_to_measure: int = 100,
                 custom_path: str = '',
                 additional_folders: List[str] = None,
                 debug: bool = False) -> None:
        if sim_filename == "default":
            print("Warning: using 'default' as simulation name since the data collector wasn't informed.")
            print("Results will be saved in a default folder and might not be distinguishable from other simulations")
        self.__sim_filename = sim_filename
        self.__steps_to_measure = steps_to_measure
        self.__path = custom_path if custom_path != '' else f"{os.getcwd()}/results"
        self.__additional_folders = additional_folders
        self.__debug = debug
        self.__travel_times = np.array([])
        self.__travel_avg_df = pd.DataFrame({"Step": [], "Average travel time": []})
        self.__start_time = datetime.now()
        self.__random = SystemRandom()

    def append_travel_times(self, travel_times: List[int], step: int) -> None:
        """Method that receives a list of travel times and the step they were retrieved and saves them to calculate the
        moving average.

        Args:
            travel_times (List[int]): list containing all travel times retrieved in the step given.
            step (int): step in which the travel times were retrieved.
        """
        self.__travel_times = np.append(self.__travel_times, travel_times)
        self.__update_df(step)

    def save(self):
        """Method that saves the data stored to csv file.
        """
        if self.__debug:  # TODO implement debuging structures as necessary
            print("No debug structure is defined yet!")

        self.__save_to_csv("MovingAverage", self.__travel_avg_df)

    def reset(self) -> None:
        """Method that resets the collector data to make a new run.
        """
        self.__start_time = datetime.now()
        self.__travel_times = np.array([])
        self.__travel_avg_df = pd.DataFrame({"Step": [], "Average travel time": []})

    def __update_df(self, step: int) -> None:
        """Method that updates the internal dataframe with the new moving average if the current step is the one to make
        the measurement.

        Args:
            step (int): current step
        """
        if step % self.__steps_to_measure == 0 and self.__travel_times.size != 0:
            avg_travel_time = self.__travel_times.mean()
            df_update = pd.DataFrame({"Step": [step], "Average travel time": [avg_travel_time]})
            self.__travel_avg_df = self.__travel_avg_df.append(df_update, ignore_index=True)
            self.__travel_times = np.array([])

    def __create_folder(self, folder_name: str) -> None:
        """Method that creates a folder to save the files if it wasn't created yet.

        Args:
            folder_name (str): name/path to folder

        Raises:
            OSError: if the folder can't be created, it raises an OSError.
        """
        try:
            os.mkdir(folder_name)
        except OSError as error:
            if error.errno != errno.EEXIST:
                print(f"Couldn't create folder {folder_name}, error message: {error.strerror}")
                raise OSError(error).with_traceback(error.__traceback__)

    def __verify_and_create_folder_path(self, folder_name: str) -> str:
        """Method that creates the folder hierarchy where the simulation files will be stored. 

        Args:
            folder_name (str): Main simulation folder name

        Returns:
            str: Complete path to the final folder.
        """
        date_folder = self.__start_time.strftime("%m_%d_%y")
        folder_str = self.__path
        self.__create_folder(folder_str)
        folder_str += f"/{folder_name}"
        self.__create_folder(folder_str)
        folder_str += f"/{self.__sim_filename}"
        self.__create_folder(folder_str)
        folder_str += f"/{date_folder}"
        self.__create_folder(folder_str)

        if self.__additional_folders is not None:
            for additional_folder in self.__additional_folders:
                folder_str += f"/{additional_folder}"
                self.__create_folder(folder_str)

        return folder_str


    def __save_to_csv(self, folder_name: str, data_frame: pd.DataFrame) -> None:
        """Method that saves the data collected to a csv file.

        Args:
            folder_name (str): Main simulation folder name to save the file in.
            data_frame (pd.DataFrame): dataframe that stores the data to be saved.
        """
        folder_str = self.__verify_and_create_folder_path(folder_name)
        file_signature = f"{self.__start_time.strftime('%H-%M-%S')}_{self.__random.randint(0, 1000):03}"
        csv_filename = folder_str + f"/sim_{file_signature}.csv"
        data_frame.to_csv(csv_filename, index=False)
