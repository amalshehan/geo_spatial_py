import arcpy
import os

# Set the workspace and output directory
workspace = arcpy.env.workspace  # Use the current workspace
output_directory = "D:/ag.gdb/"  # Update with the directory where you want to save the results

# Set the tessellation layer
h3_tessellation_layer = "arcticHexRes5"  # Update with the name of your tessellation layer

# Create an empty summary table to accumulate results
sum_table = os.path.join(output_directory, "t")

# Check if the summary table exists, if not, create it
if not arcpy.Exists(sum_table):
    arcpy.CreateTable_management(output_directory, "sum_table")
    arcpy.AddField_management(summary_table, "GRID_ID", "TEXT", field_length=50)
    arcpy.AddField_management(summary_table, "Sum_Area", "DOUBLE")

# Print all field names in the summary table
print("Field names in summary table:")
for field in arcpy.ListFields(sum_table):
    print(field.name)

temp_sum4 = os.path.join(output_directory, "ts")    

# Loop through each polygon shapefile in the directory
shp_directory = "D:/IWP_ag/arcgis_test/"  # Update with the directory containing your polygon shapefiles
for filename in os.listdir(shp_directory):
    if filename.endswith(".shp"):
        polygon_shp = os.path.join(shp_directory, filename)

        # Execute SummarizeWithin
        # Execute SummarizeWithin
        try:
            arcpy.analysis.SummarizeWithin(h3_tessellation_layer, polygon_shp, temp_sum4, "ONLY_INTERSECTING", [["AREA", "SUM"]])
            print(f"SummarizeWithin started for {filename}")
        except arcpy.ExecuteError:
            print(f"Failed to execute SummarizeWithin for {filename}:")
            print(arcpy.GetMessages())


        print(f"SummarizeWithin started for {filename}")
        
        
        # Update the summary table with the results from the current shapefile
        try:
            with arcpy.da.SearchCursor(temp_sum4, ["GRID_ID", "Sum_Area"]) as cursor:
                print("Field names:", cursor.fields) 
                with arcpy.da.UpdateCursor(sum_table, ["GRID_ID", "Sum_Area"]) as update_cursor:
                    #print("Field names:", update_cursor.fields)  # Print field names
                    for row in cursor:
                        print(u'{0}, {1},'.format(row[0], row[1]))
                        grid_id, sum_area = row
                        # Check if the H3_ID already exists in the summary table
                        row_found = False
                        for update_row in update_cursor:
                            if update_row[0] == grid_id:
                                update_row[1] += sum_area
                                update_cursor.updateRow(update_row)
                                row_found = True
                                break
                        if not row_found:
                            with arcpy.da.InsertCursor(sum_table, ["GRID_ID", "Sum_Area"]) as insert_cursor:
                                insert_cursor.insertRow((grid_id, sum_area))              
        except arcpy.ExecuteError:
            print(arcpy.GetMessages())

        print(f"SummarizeWithin completed for {filename}")

print("SummarizeWithin for all shapefiles completed. Output saved to summary_all table.")

# Clean up temporary table
arcpy.Delete_management(temp_sum4)
