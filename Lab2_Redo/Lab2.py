import yaml
import arcpy

from etl.GSheetsEtl import GSheetsEtl



def setup():
    with open('config_dict/wnvoutbreak.yaml') as f:
        config_dict = yaml.load(f, Loader=yaml.FullLoader)

    return config_dict


def etl():
    print("Start etl process....")
    etl_instance = GSheetsEtl(config_dict)
    etl_instance.process()

def buffer(layer, dist):
    units = " feet"

    distance = dist + units

    # Output location path for the buffered layer
    output_layer = f"{layer}_buff"

    # Buffer analysis tool (input variable name, output variable name, distance type string,"FULL", "ROUND", "ALL")
    arcpy.Buffer_analysis(layer, output_layer, distance, "FULL", "ROUND", "ALL")

    print("Buffer created " + output_layer)
    return

def intersect(inter_list):
    # print the list being passed in
    print(inter_list)

    # ask the user to define an output intersect layer and store the results in a variable
    output_layer = f"{config_dict.get('proj_dir')}WNVOutbreak.gdb\\allinter"

    # run a intersect analysis between the two buffer layer name and store the result in a variable
    # using arcpy.Intersect_analysis
    arcpy.Intersect_analysis(inter_list, output_layer)

    # print statement confirming intersect
    print("Intersect has been completed")

    # return the name of the new output layer
    return

def spatial(output_intersectlayer):
    target_feature = f"{config_dict.get('proj_dir')}WNVOutbreak.gdb\\BoulderAddresses"
    join_feature = output_intersectlayer
    spj_file = f"{config_dict.get('proj_dir')}WNVOutbreak.gdb\\spatial_join"
    arcpy.SpatialJoin_analysis(target_feature, join_feature, spj_file)
    return

def erase(output_spatialjoinglayer):
    in_features = output_spatialjoinglayer
    avoidpoint= f"{config_dict.get('proj_dir')}WNVOutbreak.gdb\\avoid_points"
    out_feature_class = f"{config_dict.get('proj_dir')}WNVOutbreak.gdb\\spj_werasedpoints_layer"
    arcpy.Erase_analysis(in_features,avoidpoint,out_feature_class)
    return out_feature_class




def main():

    arcpy.env.workspace = f"{config_dict.get('proj_dir')}WNVOutbreak.gdb"
    #aprx = arcpy.mp.ArcGISProject(f"{config_dict.get('proj_dir')}WNVOutbreak.gdb.aprx")
    arcpy.env.overwriteOutput = True

    LayerList = ["MosquitoLarvalSites", "Wetlands", "OSMPProperties", "LakesandReservoirs"]
    print(LayerList)

    #buffer
    for layer in LayerList:
        dist=1000
        bufferlayer = buffer(layer,dist)


    #intersect
    inter_list = ["MosquitoLarvalSites_buff", "Wetlands_buff", "OSMPProperties_buff", "LakesandReservoirs_buff"]
    output_intersectlayer = intersect(inter_list)

    #spatialjoin
    output_spatialjoinlayer = spatial(output_intersectlayer)
    print(f"New Spatial Join Layer named: {output_spatialjoinlayer}")

    #Erase
    erase_layer = erase(output_spatialjoinlayer)
    print(f"Erases newaddress file from spatial join: {erase_layer}")

    print("All done")


if __name__ == '__main__':
    global config_dict
    config_dict = setup()
    print(config_dict)
    etl()
    main()



