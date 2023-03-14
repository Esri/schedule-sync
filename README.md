# schedule-sync

Schedules often do not contain a spatial component. Schedules are continually changing and time specific. The schedule-sync repository gives you a series of methods to sync your schedule data to your ArcGIS Enterprise or ArcGIS Online account. You will now be able to plainly see the spatial nature of your schedule. By running these automated workflows you can automatically keep your published schedule data up-to-date. Date datatypes are preserved so your published layers can be time-enabled allowing all the Esri time-enabled functionality. 

There are two workflows and three data sources. The best workflow for you will depend on the source of your schedule data.

1. Schedule as Excel File
2. Schedue from P6 XML file or P6 EPPM Server


## Features

**Features of all wokflows**
* Interactive and automation friendly ArcGIS Pro Tool
* Creation of relationship class between the schedule table and a feature class using configurable join fields.
* Publishing of a new feature service with the schedule table, feature service, and relationship class. 
* Updating of a feature service with a schedule table, feature service, and relationship class.

**Excel Schedule Workflow Specific Features**
* Support for reading Excel schedule files and creation of a schedule feature table
* Support for the input of display friendly, alias field names

**P6 Schedule Workflow Specific Features**
* Support using data P6 XML data exported from Primavera Cloud, Primavera P6 EPPM Servers, and Primavera P6 Professional.
* Supports pulling schedule data directly from Primavera P6 EPPM server. Please note the Primavera P6 EPPM server must meet the required settings. If you cannot use the supported settings consider exporting your data to the P6 XML or Excel format. Primavera P6 EPPM supports the setup of automated file exports, which can allow for a fully automated sync data pipeline. You have many options, consider what will be best or your organization.
* Supports the joining of the schedule table and a feature class. The join is best when you have a one-to-one type join. 
* Supports the creations of a relationship class between the schedule table and feature class. The relationship is best when you do not have a one-to-one relationship.
* Supports the the cloning of map symbology from a source map to a target map.
* Supports the publishing of a specified map, which includes the schedule table, feature class, and relationship class as a feature service.

## Instructions

1. Clone the repo to a local directory
2. Navigate to the subdiretory for the workflow you would like to use. The proper workflow will depend on your schedule data source.
3. Read the Readme located in the sub directory for your workflow and follow the rest of the instructions there.

## Requirements

* ArcGIS Pro the application used to run many of the automation tools
* ArcGIS Online or ArcGIS Enterprise organization where the content will be published
* ArcGIS Online or ArcGIS Enterprise user with user type and role, which will allow running the ArcGIS Pro tools and publishing the content

## Resources

List of links here...

## Issues

Find a bug or want to request a new feature? Please let us know by submitting an issue.

## Contributing

Esri welcomes contributions from anyone and everyone. Please see our [guidelines for contributing](https://github.com/esri/contributing).

## Licensing
Copyright 2021 Esri

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
