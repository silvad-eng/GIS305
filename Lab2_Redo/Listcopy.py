import arcpy
import os
from arcpy import env

env.workspace = r"E:\GIS\GIS305\Lab2\AllData"
env.overwriteOutput = True

fclist= arcpy.ListFeatureClasses()
print(fclist)

for fc in fclist:
    out_featureclass = os.path.join(r"C:\Users\chica\Documents\ArcGIS\Projects\WNVOutbreak\WNVOutbreak.gdb", os.path.splitext(fc)[0])
    arcpy.CopyFeatures_management(fc, out_featureclass)