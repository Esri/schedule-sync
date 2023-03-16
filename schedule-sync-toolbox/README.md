# p6_tool
The P6 Project Scheduling Integration tool provides the ability to create relationships between your P6 and GIS feature layers. In addition, those layers are published to your ArcGIS organization where they can easily be used to create web maps and dashboards. Finally, we have the ability to update the feature layers as needed. The P6 data can come from an XML or a P6 EPPM server.



## Requirements

Verify the user meets the follow requirements required to run the P6 Geoprocessing tool:

* The user has ArcGIS Pro 8.5 or newer installed.
* The user has the Standard or Advanced ArcGIS Pro license. The Basic ArcGIS Pro license is not sufficient to run the tool. 
* The ArcGIS Organization user must have a user type that allow publication of content. Both Creator and GIS Professional user types allow the publication of content. 
* The user has configured and activated a Python environment with all the needed modules. See the  Setup Python section for detailed instructions.
* The P6 Project data and ArcGIS Pro Feature Layer must each have a column that can be used to match each P6 row with a specific row in your ArcGIS Pro Feature Layer. 
* The ArcGIS Pro Feature Layer must be in a geodatabase. 
* The ArcGIS Pro Feature Layer must be one of your map layers.



### XML Requirements and Limitations

* You must have an XML file in the P6 XML format. The file can be exported from P6 Desktop, P6 Server, or Oracle Primavera Cloud.
* Data types supported include: Project Standard Fields, WBS Standard Fields, Activity Standard Fields, Activity User Defined Fields, and Activity Code Fields. 
* Data types not supported include: Project User Defined Fields, WBS User Defined Fields, and Project Code Fields. 

### P6 EPPM Requirements
* The P6 server must be accessible. You can log into the server from the browser-based interface to verify the machine has access to the P6 server. 

### Publishing Requirements

* The ArcGIS Organization user must have a user type that allow publication of content. Both Creator and GIS Professional user types allow the publication of content. 
* The ArcGIS organization must be accessible. You can log into the server from the browser-based interface to verify the machine has access to the ArcGIS Organization.
* ArcGIS Pro must be logged into your organization. 
* When updating a feature service on your organization with the tool you will need the title and ID value to provide as input parameters.

## Setup

Follow the steps in all setup sub sections to ensure the requirements above are met. 

### Setup Python

Below is the process to setup a Python environment for use with the tool.

1. Create a clone of the default ArcGIS Pro conda environment:

   ```conda create --name arcgispro-py3-zeep --clone arcgispro-py3```

2. Activate your new environment: 

   ```proswap arcgispro-py3-zeep```

3. Install zeep:

   ```conda install -c conda-forge zeep```



### Activate Python Environment

Once you have setup the Zeep Python environment all you need to do is activate the environment before running the tool with the following command in the Python Command Prompt:

```Proswap arcgispro-py3-zeep```



### Setup Tool Configuration Settings

The tool default settings live in the **p6config.ini** file. You can find this file inside the p6_tool directory. Any settings here will be loaded by default. The default settings can be changed by editing the config file. You can also override any defaults by changing the tool inputs when using the tool.

Note any text on a line after the `#` character will be ignored and is treated as a comment. 

* Under the `[GENERAL]` section you choose the default input as XML or EPPM. To use XML as default set the input variable including the line `input=XML`. To use EPPM as default set the input variable including the line `input=EPPM`. 
* Under the `[GENERAL]` section you choose the temp folder location.
* Under the `[XML]` section you can set a default path to an XML file using the line: `path=C:\path\to\my\file.xml`
* Under the `[SERVER]` section you can set a server URL with the line: `p6ws_server = http://10.49.54.172:8206/p6ws` where `http://10.49.54.172:8206/p6ws` is replaced with your server address.



### Setup Oracle Primavera

At a minimum there must be a join field in the Primavera that can be used to link the Primavera data to the desired feature class row. Refer to the Oracle documentation for information on how to add a column and populate the values. 

#### Add GIS_ID to P6 EPPM Server Project

1. Create a user field called **GIS_ID**.

   a.   Click **Administration**.

   b.   On the Administration navigation bar, click **Enterprise Data**.

   c.    On the Enterprise Data page, expand **Activities** and click **Activity UDFs**.

   d.   On the Activity UDFs page: click **Add**.

   f.    In the **User Defined Field**, double-click and type a name.

   g.   In the **Data Type** field, choose a type from the list.

   h.   Click **Save**.

2. Use the P6 browser interface to enter the GIS_ID for the geometry you want to join with your activity. 

3. Click Save to save your changes.

### Setup ArcGIS Pro

1. We will first login to our organization. The organization you use for the login is where your content will be published. The user used to login will be the owner of the content published. You can see documentation now how to login to your organization [here](https://pro.arcgis.com/en/pro-app/latest/help/projects/sign-in-to-your-organization.htm). You click on the figure in the top right corner of ArcGIS Pro, using the drop-down menu you can login. You will need your username and password. The ArcGIS Organization user must have a user type that allow publication of content. Both Creator and GIS Professional user types allow the publication of content. 

2. Check that the feature class you would like to join with is in a geodatabase, which is a requirement for the tool to run properly. The feature class must also be added as a layer to your ArcGIS Pro project Map.

3. In your Map properties under the General section you must check off **Allow assignment of unique numeric IDs for sharing web layers**. If this checkbox is not checked you will not be able to publish. 

### Setup ArcGIS Pro Feature Class

At a minimum there must be a column in your ArcGIS Pro feature class that can be used as a join field. See the ArcGIS Pro documentation for information on how to add a column and populate the values.

## Tool Inputs

Below we describe all the input fields. 

### Input Type

The first section of the tool allow you to select the input type. The value will be prepopulated with the default value from the `.ini` file. Select `XML` to pull your Primavera data from an XML file. Select `EPPM` to pull your Primavera data directly from a P6 EPPM server. 

### P6 XML

The P6 XML section becomes accessible when the chosen input is XML. 

#### P6 XML File Path

The P6 XML File Path value is prepopulated with a default value from the `.ini` file. You can can use the file browser to select your XML file or enter the path directly into the text box.

### P6 Authentication

When EPPM is chosen as the data source the P6 Authentication section appears. In this section you can input the P6 EPPM user name, password, and URL used to access the P6 EPPM server. 

### P6 Subject Area
For the subject area, you have the options Projects, WBS, or Activities. Choosing Projects will pull all the projects. Each project will be linked with a given feature class row or rows using the specified link fields. Alternatively, you have the option to choose WBS. In this case, each feature class row will be matched with one or more WBS rows from a single Primavera project. Finally, you have the option to choose Activities, where each feature class row will be matched with one or more Activities from a single Primavera project. 

### P6 Projects
If a subject area of WBS or Activity is chosen, you will choose from a list of projects and baseline projects. The chosen project or baseline project is where the WBS or Activity data will be pulled from. 

### P6 Fields
A list of standard fields is presented under the **Standard Field** input, where you can check off all the fields you would like to include. 

User defined fields are listed under the **User Defied Fields** section. Check off all the fields you would like to include in the output. 

If you would like to include activity code or project code fields check the box. *Note: Project Codes are not currently supported for the XML input type.*

### Join Parameters

Under the Join Parameters section, you specify the P6 link field, feature layer, feature layer link field, and join option. A **Join - One to One** will create a new feature class joined with P6 data for one-to-one data. A **Relationship Class - Many to One** will create a relationship class and table for many-to-one data.  

### Output

Under the output section you control the output of the tool. The table name is optional and allows you to use a custom table name for the imported P6 data. The relationship class name provides a name for the relationship created by the tool. Map is a required value. You must select the map containing your feature class. There are three publishing options: do not publish, publish, and update existing. If you are publishing be sure to include all the values including the title, tags, and folder. If you are updating an existing feature service be sure to use the same title, folder, and item ID. 

The tool will have different outputs depending on your choices for **Join Option**. 

* **Map:**
  * **Join – One to One/Map**: This will create a feature layer with joined data. 
  * **Relationship Class – Many to One/Map**: This will create a feature layer with accompanying relationship class and table. This may be opened in a web map or a web scene, but relationship classes will not be honored in the web scene. 

### Grouping
The grouping section of the tool allow us to group values on feature class rows. 

#### Date Grouping
When grouping by the date field, two columns will be added to the feature class. One for the earliest date and one column for the last date. So for example with your example data we could group each building with its earliest PlannedStartDate and latest PlannedFinishedDate to see what buildings are being worked on at any given time. 
Check off any date fields you want to group by. 

#### Category Grouping
When grouping by a category field, a new column will be added for each category. Then, each row will be assigned a TRUE or FALSE to represent if the row is associated with the given category. So for example if a building has activities that are all complete then you can use the TRUE value under the complete column to symbolize the building as complete. 

Check off any category fields you would like to group by. Be sure to only use this option on a field with a limited number of values, because a new column is created for every unique value in a column. 

## Trouble Shooting

* Issue: The tool does not want to run. 
  * Solution 1: Usually restarting the to or ArcGIS Pro is enough to resolve the issue.
  * Solution 2: If the Python environment is not correctly created or activated the tool will not run. See the section on creating and activating your Python environment. 
* Issue: Problems publishing a new feature service. 
  * Solution 1: If there is already a feature service `.sd`  or `.slpk` file with the same name locally or on the server the tool will not let you overwrite the file. Simply delete the local `.sd` or `.slpk` file locally and on the server. Alternatively, you can choose a new unique name to avoid the conflict. 


## Limitations

* Scenes are not supported.


## Version History

// 1.0.8 // December 26, 2022

* Check if field names start with valid character and fix if needed.
* Check if field names are a valid length and fix if needed.

// 1.0.7 // November 29, 2022

* Simplify inputs.

// 1.0.6 // October 7, 2022

* Split P6 Integration, Symbology cloning, and publishing into 3 separate tools.
* Add support for `Activity Steps` 

// 1.0.5 // May 11, 2022

* Fix bug preventing publication.
* Simplify update input.
* Remove support of scenes.

// 1.0.4 // May 6, 2022

* Fix bug preventing publication of one-to-one join.

// 1.0.3 // January 18, 2022

* Update documentation.

// 1.0.2 // January 05, 2022

* Fix split error for None grouping input.

// 1.0.1 // January 04, 2022

* Add date and category grouping to tool.

// 1.0.0 // December 28, 2021

* Use Python tempfile to hold and cleanup temporary files.









