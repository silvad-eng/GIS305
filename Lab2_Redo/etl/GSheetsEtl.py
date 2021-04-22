import arcpy
import requests
import csv

from etl.SpatialEtl import SpatialEtl



class GSheetsEtl(SpatialEtl):

    config_dict = None

    def __init__(self, config_dict):
        super().__init__(self.config_dict)

    def extract(self):
        print("Extracting addresses from google form spreadsheet")


        r = requests.get(self.config_dict.get('remote_url'))
        r.encoding = "utf-8"
        data = r.text
        with open(f"{self.config_dict.get('proj_dir')}addresses.csv", "w") as output_file:
            output_file.write(data)

    # transform function
    def transform(self):
        print("Add City, State")
        geocoder_prefix_url = self.config_dict.get('geocoder_prefix_url')
        geocoder_suffix_url = self.config_dict.get('geocoder_suffix_url')
        transformed_file = open(f"{self.config_dict.get('proj_dir')}new_addresses.csv", "w")
        transformed_file.write("X,Y,Type\n")
        with open(f"{self.config_dict.get('proj_dir')}addresses.csv", "r") as partial_file:
            csv_dict = csv.DictReader(partial_file, delimiter=',')
            for row in csv_dict:
                address = row["Street Address"] + " Boulder CO"
                print(address)
                geocode_url = f"{geocoder_prefix_url}{address}{geocoder_suffix_url}"
                print(geocode_url)
                r = requests.get(geocode_url)

                resp_dist = r.json()
                x = resp_dist['result']['addressMatches'][0]['coordinates']['x']
                y = resp_dist['result']['addressMatches'][0]['coordinates']['y']
                transformed_file.write(f"{x},{y}, Residential\n")

        transformed_file.close()

    # load function
    def load(self):
        # Description: Creates a point feature class from input table

        # Set Environment Settings
        arcpy.env.workspace = f"{self.config_dict.get('proj_dir')}"
        arcpy.env.overwriteOutput = True

        in_table = f"{self.config_dict.get('proj_dir')}new_addresses.csv"
        out_feature_class = f"{self.config_dict.get('proj_dir')}\WNVOutbreak.gdb\\avoid_points"
        print("avoid points file has been created")
        x_coords = "X"
        y_coords = "Y"

        #     Make the XY event layer....
        arcpy.management.XYTableToPoint(in_table, out_feature_class, x_coords, y_coords)

        #     Print the total rows
        print(arcpy.GetCount_management(out_feature_class))

    def process(self):
        self.extract()
        self.transform()
        self.load()