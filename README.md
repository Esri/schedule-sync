# schedule-sync

Schedules are inherently spatial. However, schedules often do not contain a spatial component. In addition, schedules are continually changing and time specific. The schedule-sync repository gives you a series of tools to sync your schedule data to your ArcGIS Enterprise or ArcGIS Online account. 

You will now be able to plainly see the spatial nature of your schedule. By running these automated workflows you can automatically keep your published schedule data up-to-date. Date datatypes are preserved so your published layers can be time-enabled allowing all the Esri time-enabled functionality. 

Here we provide three ArcGIS Pro tools, one for each of three data sources. The best workflow for you will depend on the source of your schedule data. Inside the schedule-sync-toolbox you will find the following tools:

1. Sync CSV Schedule
1. Sync Excel Schedule
1. Sync P6 XML Schedule




## Features

**Features of all tools**

* Interactive and automation friendly ArcGIS Pro Tool
* Creation of relationship class or join between the schedule table and a feature class using configurable link fields.
* Publishing of a new feature service with the schedule table, and feature service with a relationship class or join. 
* Updating of a feature service with a schedule table, feature service, and relationship class.
* Autodetection of existing feature service. If the feature service does not exist we publish, otherwise we update.



**Sync Excel Schedule Tool Features**

* Support for reading Excel schedule files and creation of a schedule feature table. It is assumed the schedule is in the first worksheet. See the example [activities.xlsx](./data/activities.xlsx) for a template to follow.
* Support for pulling the field names from the Excel worksheet. The field names must be provided on the first row of the spreadsheet.
* Support for the input of display friendly, alias field names. The alias names must be provided on the second row of the spreadsheet.



**Sync CSV Schedule Tool Features**

* Support for reading CSV schedule files and creation of a schedule feature table. See the example [activities.csv](./data/activities.csv) for a template to follow.
* Support for pulling the field names from the CSV file. The field names must be provided on the first row.
* Support for the input of display friendly, alias field names. The alias names must be provided on the second row.



**Sync P6 XML Schedule Tool Features**

* Support using data P6 XML files. P6 XML files can be exported from Primavera Cloud, Primavera P6 EPPM Servers, and Primavera P6 Professional.
* Supports the creation of schedule tables from the P6 Project, Activity, and WBS subject areas.
* Supports the joining of the schedule table and a feature class. The join is best when you have a one-to-one type join. 
* Supports the creations of a relationship class between the schedule table and feature class. The relationship is best when you do not have a one-to-one relationship.



## Instructions

1. Clone the repo to a local directory
2. Navigate to the subdiretory for the workflow you would like to use. The proper workflow will depend on your schedule data source.
3. Read the Readme located in the sub directory for your workflow and follow the rest of the instructions there.



## Requirements

* ArcGIS Pro the application used to run many of the automation tools
* ArcGIS Online or ArcGIS Enterprise organization where the content will be published
* ArcGIS Online or ArcGIS Enterprise user with user type and role, which will allow running the ArcGIS Pro tools and publishing the content



## Resources

* [Connecting ArcGIS Pro to a toolbox](https://pro.arcgis.com/en/pro-app/latest/help/projects/connect-to-a-toolbox.htm)



## Issues

Find a bug or want to request a new feature? Please let us know by submitting an issue.



## Contributing

Esri welcomes contributions from anyone and everyone. Please see our [guidelines for contributing](https://github.com/esri/contributing).



## Licensing
Copyright 2023 Esri

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

A copy of the license is available in the repository's [license.txt](./license.txt) file.
