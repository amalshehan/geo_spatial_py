# ArcPy Script to convert iwp shp files to sumerised table for aggregated counts 
# INPUT : iwp shape files duplicates marked <staging_du=1>, h3_tessellation_layer
# OUTPUT : Summery table with count for each Hexagonal cell in the h3_tessellation_layer
#
# Code is written to accumilate the counts for each run 
# i.e. if you do not give a new name for Summery table it will start updating the existing table
# When executing same shp file should not be processed twice

import arcpy
import os

# Set the workspace and output directory
#workspace = arcpy.env.workspace  # Use the current workspace
output_directory = "D:/ag.gdb/"  # Where to save the results
# An error was generated when the name of the file was longer due to a known issue in ArcGIS when executing SummerizeWithin

# Create a new geodatabase if it doesn't exist
if not arcpy.Exists(output_directory):
    arcpy.CreateFileGDB_management(os.path.dirname(output_directory), os.path.basename(output_directory))

# Set the workspace to the output directory
arcpy.env.workspace = output_directory

# Set the name of summery table new name to be given if you want a new run 
sum_table = "t3"

# Check if the summary table exists, if not, create it
if not arcpy.Exists(sum_table):
    print("New table created for Summary data")
    try:
        arcpy.CreateTable_management(output_directory, sum_table)
        arcpy.AddField_management(sum_table, "GRID_ID", "TEXT", field_length=50)
        arcpy.AddField_management(sum_table, "Sum_Cnt", "LONG")
    except arcpy.ExecuteError:
        print(arcpy.GetMessages(2))  # Print any error messages
else:
    print("Summary table already exists and will be used to add counts")

# Print all field names in the summary table
# Just check and see if we have the fields required for the summery
# Can commnet out later
print("Field names in summary table:")
for field in arcpy.ListFields(sum_table):
    print(field.name)
    
# Set the tessellation layer to for the summerized aggregations
h3_tessellation_layer = "arcticHexRes5"  # Name of the tessellation layer already existing

######################################################
# Loop through each polygon shapefile in the directory
######################################################
shp_directory = "D:/IWP_ag/arc_test4/"  # Directory containing polygon shapefiles
for filename in os.listdir(shp_directory):
    temp_sum = os.path.join(output_directory, "ts") #temp summary layer to keep the sumerize within
    if filename.endswith(".shp"):
        polygon_shp = os.path.join(shp_directory, filename)
        try: # Execute SummarizeWithin for the layer 
            if arcpy.Exists("input_features_lyr"): # remove layer if already exisits
                arcpy.Delete_management("input_features_lyr")
                print("old input layer deleted")
            
            if arcpy.Exists("centroid_points_lyr"): # remove layer if already exisits
                arcpy.Delete_management("centroid_points_lyr")
                print("old centroid point layer deleted")

            # Make new feature to count the polygons as arcGIS only allows SUM for aggregation
            # A new iwp cnt feature is added with "1" and later SUM ed
            # Also a check is done to see if the polygon is marked as a duplicate (not taken)
            arcpy.management.MakeFeatureLayer(polygon_shp, "input_features_lyr", "staging_du <> 1")
            
            new_field_name = "iwp_cnt"
            existing_fields = [field.name for field in arcpy.ListFields("input_features_lyr")]
            if new_field_name not in existing_fields:
                # Add the new a field to the attribute table to be used for counting the polygons using SUM
                arcpy.AddField_management("input_features_lyr", new_field_name, "SHORT")

            # Calculate the new field with the value 1 for all rows
            arcpy.CalculateField_management("input_features_lyr", new_field_name, 1, "PYTHON3")
            
            # Create a new point feature layer with centroids so the cells will not count same polygon more than once    
            arcpy.FeatureToPoint_management("input_features_lyr", "centroid_points_lyr", "INSIDE")
            
            arcpy.analysis.SummarizeWithin(h3_tessellation_layer, "centroid_points_lyr", temp_sum, "ONLY_INTERSECTING", [["iwp_cnt", "SUM"]])
            print(f"SummarizeWithin done for {filename}")
            
            # Print data collected from SummerizeWithin 
            # Just check and see if we have the fields required for the summary later
            # Can remove later
            result = arcpy.GetCount_management(temp_sum)
            polygon_count = int(result.getOutput(0))
            print("Number of H3 Cells in summary:", polygon_count)
   
        except arcpy.ExecuteError:
            print(f"Failed to execute SummarizeWithin for {filename}:")
            print(arcpy.GetMessages())
 
        # Update the summary table with the results from the current shapefile
        try:
            # Reading the cummery data for the current layer
            with arcpy.da.SearchCursor(temp_sum, ["GRID_ID", "Sum_iwp_cnt"]) as cursor:
                print("Field names:", cursor.fields) 
                # Reading the summary data table to aggregate into
                with arcpy.da.UpdateCursor(sum_table, ["GRID_ID", "Sum_Cnt"]) as update_cursor:
                    print("Field names:", update_cursor.fields)  # Print field names
                    for row in cursor:
                        print(u'GRID_ID:{0}, iwp_cnt:{1},'.format(row[0], row[1]))
                        grid_id, sum_cnt = row
                        # Check if the H3_ID already exists in the summary table 
                        row_found = False
                        for update_row in update_cursor:
                            if update_row[0] == grid_id:
                                update_row[1] += sum_cnt
                                update_cursor.updateRow(update_row)
                                row_found = True
                                print("Updated:",grid_id, "with+:",sum_cnt)
                                break
                        if not row_found: # if not create new entry and add the row
                            with arcpy.da.InsertCursor(sum_table, ["GRID_ID", "Sum_Cnt"]) as insert_cursor:
                                insert_cursor.insertRow((grid_id, sum_cnt))              
        except arcpy.ExecuteError:
            print(arcpy.GetMessages())
        print(f"SummarizeWithin completed for {filename}")
        # Clean up temporary layer
        arcpy.Delete_management(temp_sum)

print("===========================================================")
print("SummarizeWithin for all shapefiles completed. Output saved ")
print("Final Counts summary table.")
with arcpy.da.SearchCursor(sum_table, ["GRID_ID", "Sum_Cnt"]) as search_cursor:
    print("Field names:", search_cursor.fields)  # Print field names
    for row in search_cursor:
        print(u'GRID_ID:{0}, iwp_cnt:{1},'.format(row[0], row[1]))
