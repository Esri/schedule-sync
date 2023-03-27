# Sync CSV Schedule Workflow

The Sync CSV Schedule Tool is engineered to enrich and publish your schedule data. 

## Using the Sync CSV Schedule Tool

1. Clone the repo to a local directory accessible by ArcGIS Pro.
2. Open ArcGIS Pro.
3. Sign into your ArcGIS Enterprise or ArcGIS Online organization. [Documentation](https://pro.arcgis.com/en/pro-app/latest/help/projects/sign-in-to-your-organization.htm)
4. Open the `schedule-sync-toolbox.pyt` in ArcGIS Pro. [Documentation](https://pro.arcgis.com/en/pro-app/latest/help/projects/connect-to-a-toolbox.htm)
5. Open the Sync CSV Schedule tool.
6. Populate the tool input values and run the tool. You can also use ArcGIS Pro to schedule the running of the tool to automate your update process. See the documentation on tool scheduling [here](https://pro.arcgis.com/en/pro-app/latest/help/analysis/geoprocessing/basics/schedule-geoprocessing-tools.htm).


## Sync CSV Schedule Tool Inputs

**Schedule File:** Provide the path to our sample CSV file [activities.csv](activities.csv). Use the file browser to select your CSV schedule file. The first row of values in the file will be used as the field names. The field name values must follow all the standard requirements for a geodatabase table field name. The second row of the values in the file will be used as the alias names. The alias names must follow all the standard requirements for geodatabase table field alias names.

**Schedule Link Field:** Select the field in your schedule used to link the schedule table to the feature class feature. Our example workflow uses the `join_id` field.

**Feature Class:** Provide the path to the `line_segments` sample feature class inside [bloomingtonProject.gdb](bloomingtonProject.gdb).

**Feature Class Link Field:** Select the field in your feature class used to link the schedule table to the feature class feature. Our example workflow uses the `join_id` field.

**Schedule Date Fields:** Select the fields you would like to be the Esri datetime datatype. Our example workflow uses the `start_date` field.

**Date Format String:** Provide the datetime format string `%m/%d/%Y`. See the Python documentation on datetime formatting strings [here](https://docs.python.org/3/library/datetime.html).

**Hosted Feature Service Title:** Provide the title `Bloomington Powerline Project` for the feature service to be published to your ArcGIS Enterprise or ArcGIS Online organization.

**Schedule Table Name:** Provide the name `bloomtington_schedule` to be used for your published table. The name must follow the conventions for a geodatabase table name. 

**Geodatabase Name:** Provide the name `bloomington.gdb` to be used for your published geodatabase. The name must follow the conventions for a geodatabase name.

**Folder:** Provide the folder name `schedule_sync` where the published content will be published to or updated in. 

**Tag:** Provide the tag `schedule_sync` used to label the published content.

**Select Relate or Join:** Choose the relate option for the published content. Join is used when you have one schedule row for each one feature. More commonly people use the relate option, which is used for all other situations. In our case we have many activities associated with each feature segment, so a relationship class is required. 

