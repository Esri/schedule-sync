# Sync P6 XML Schedule Workflow

The Sync P6 XML Schedule Tool is engineered to enrich and publish your schedule data. 

## Using the Sync P6 XML Schedule Tool

1. Clone the repo to a local directory accessible by ArcGIS Pro.
2. Open ArcGIS Pro.
3. Sign into your ArcGIS Enterprise or ArcGIS Online organization. [Documentation](https://pro.arcgis.com/en/pro-app/latest/help/projects/sign-in-to-your-organization.htm)
4. Open the `schedule-sync-toolbox.pyt` in ArcGIS Pro. [Documentation](https://pro.arcgis.com/en/pro-app/latest/help/projects/connect-to-a-toolbox.htm)
5. Open the Sync P6 XML Schedule tool. 
6. Populate the tool input values and run the tool. You can also use ArcGIS Pro to schedule the running of the tool to automate your update process. See the documentation on tool scheduling [here](https://pro.arcgis.com/en/pro-app/latest/help/analysis/geoprocessing/basics/schedule-geoprocessing-tools.htm).



## Sync P6 XML Schedule Tool Inputs
**P6 XML File Path:** Input your file path to the [Bloomington to Minonk 345 KV XTR Line.xml](Bloomington to Minonk 345 KV XTR Line.xml) file.

**Subject Area:** Select the `Activity` subject area.

**P6 Project:** Select the `Bloomington to Minonk 345 KV XTR Line(28401)` project.

**Standard Fields:** Select the `Name` standard fields to import.

**User Defined Fields:** Select the `join_id` user defined fields to import. 

**Include Activity Codes:** Check this box to import all Activity Code columns. This option is only relevant and available when using the actvity subject area.  

**P6 Link Field:** Select the `join_id` link field.

**Feature Class:** Provide the path to the `line_segments` sample feature class inside [bloomingtonProject.gdb](bloomingtonProject.gdb). 

**Feature Class Link Field:** Select the `join_id` feature class link field.

**Join Option:** Choose the relate option for the published content. Join is used when you have one schedule row for each one feature. More commonly people use the relate option, which is used for all other situations. In our case we have many activities associated with each feature segment, so a relationship class is required. 

**Date Fields To Group:** We skip this optional input.

**Category Fields To Group:** We skip this optional input.

**Hosted Feature Service Title:** Provide the title `Bloomfield_Powerlines` for your hosted feature service. When publishing a new hosted feature service ensure the name you use is unique. When updating an existing hosted feature service the name provide must exactly match the eisting hosted feature service name.

**Folder:** Provide the folder name `schedule_sync` where the published content will be published to or updated in. 

**Tag:** Provide the tag `schedule_sync` used to label the published content.


