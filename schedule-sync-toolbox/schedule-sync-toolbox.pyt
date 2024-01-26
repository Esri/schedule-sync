# -*- coding: utf-8 -*-

import os
import pandas as pd
from pathlib import Path
import sys
from shutil import make_archive
import tempfile

from arcgis import GeoAccessor
from arcgis.gis import GIS
import arcpy
import xml.etree.ElementTree as ET
# from zeep import Client
# from zeep.wsse.username import UsernameToken
import datetime

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "ScheduleSyncToolbox"
        self.alias = "Schedule Sync Toolbox"

        # List of tool classes associated with this toolbox
        self.tools = [P6IntegTool, ExcelTool, CsvTool]


class P6IntegTool(object):

    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Sync P6 XML Schedule"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Function defines the tool UI parameters.""" 

        params = []

        # Option to Choose Input P6 XML or P6 EPPM
        param0 = arcpy.Parameter( 
            displayName="Input Type", 
            name="input_type", 
            datatype="GPString",
            parameterType="Optional", 
            direction="Input")               
        param0.filter.type = "ValueList"
        param0.filter.list = ["XML", "EPPM"]
        # param0.category = "Input Type"
        param0.value = "XML"
        param0.enabled = False
        params.append(param0)

        param1 = arcpy.Parameter( 
            displayName="P6 XML File Path", 
            name="xml_file_path", 
            datatype="DEFile",
            parameterType="Optional", 
            direction="Input")               
        param1.filter.list = ["xml"]
        param1.category = "P6 XML"
        params.append(param1)

        param2 = arcpy.Parameter( 
            displayName="User Name", 
            name="user_name", 
            datatype="GPString",
            parameterType="Optional", 
            direction="Input")
        param2.value = ""
        param2.value = "admin"
        # param2.category = "P6 Authentication"
        param2.enabled = False
        params.append(param2)
        
        param3 = arcpy.Parameter( 
            displayName="Password", 
            name="password", 
            datatype="GPStringHidden",
            parameterType="Optional", 
            direction="Input")                              
        # param3.value = ""
        # param3.value = "admin"
        # param3.category = "P6 Authentication"
        param3.enabled = False
        params.append(param3)
        
        param4 = arcpy.Parameter( 
            displayName="P6 Host Name", 
            name="host_name", 
            datatype="GPString",
            parameterType="Optional", 
            direction="Input")               

        # server = self.getP6Server()
        # param4.value = server 
        # param4.category = "P6 Authentication"
        param4.enabled = False
        params.append(param4)
        
        param5 = arcpy.Parameter( 
            displayName="Subject Area", 
            name="subject_area", 
            datatype="GPString",
            parameterType="Required", 
            direction="Input")               
        param5.filter.type = "ValueList"
        param5.filter.list = ["Project", "WBS", "Activity"]
        param5.value = "Activity"
        param5.category = "P6 Subject Area"
        params.append(param5)
        
        param6 = arcpy.Parameter( 
            displayName="P6 Project", 
            name="p6_projects", 
            datatype="GPString",
            parameterType="Optional", 
            direction="Input")               
        param6.filter.type = "ValueList"
        param6.category = "P6 Projects"
        params.append(param6)
        
        param7 = arcpy.Parameter( 
            displayName="Standard Fields", 
            name="standard_fields", 
            datatype="GPString",
            parameterType="Optional", 
            direction="Input", 
            multiValue=True)               
        param7.filter.type = "ValueList"
        param7.category = "P6 Fields"
        params.append(param7)

        param8 = arcpy.Parameter( 
            displayName="User Defined Fields", 
            name="userDefined_fields", 
            datatype="GPString",
            parameterType="Optional", 
            direction="Input", 
            multiValue=True)               
        param8.filter.type = "ValueList"
        param8.category = "P6 Fields"
        params.append(param8)

        param9 = arcpy.Parameter ( 
            displayName="Include Activity Codes", 
            name="p6_codes", 
            datatype="GPBoolean",
            parameterType="Optional", 
            direction="Input")
        param9.value = False
        param9.category = "P6 Fields"
        params.append(param9)

        param10 = arcpy.Parameter( 
            displayName="P6 Link Field", 
            name="p6link_field", 
            datatype="GPString",
            parameterType="Required", 
            direction="Input")               
        param10.filter.type = "ValueList"
        param10.value = ""
        param10.category = "Join Parameters"
        params.append(param10)
        
        param11 = arcpy.Parameter( 
            displayName="Feature Class", 
            name="feat_class", 
            datatype="DEFeatureClass",
            parameterType="Required", 
            direction="Input")
        param11.category = "Join Parameters"
        params.append(param11)
        
        param12 = arcpy.Parameter( 
            displayName="Feature Class Link Field", 
            name="featlayer_link_field", 
            datatype="Field",
            parameterType="Required", 
            direction="Input")               
        param12.parameterDependencies = [param11.name]
        param12.value = ""
        param12.category = "Join Parameters"
        params.append(param12)

        param13 = arcpy.Parameter( 
            displayName="Join Option", 
            name="join_option", 
            datatype="GPString",
            parameterType="Required", 
            direction="Input")               
        param13.filter.type = "ValueList"
        param13.filter.list = ["Join Data - One to One", "Relationship Class - Many to One"]
        param13.category = "Join Parameters"
        params.append(param13)

        param14 = arcpy.Parameter( 
            displayName="P6 Table Output Name (Optional)", 
            name="p6_output_name", 
            datatype="GPString",
            parameterType="Optional", 
            direction="Output")
        # param14.value = ""
        param14.category = "Output"
        param14.enabled = False
        params.append(param14)

        param15 = arcpy.Parameter( 
            displayName="Relationship Class Name", 
            name="rel_class", 
            datatype="GPString",
            parameterType="Optional", 
            direction="Output")
        param15.value = "my_rel_class"
        param15.category = "Output"
        param15.enabled = False
        params.append(param15)

        # TODO: Remove Map
        param16 = arcpy.Parameter( 
            displayName="Map", 
            name="pro_map", 
            datatype="GPMap", 
            parameterType="Optional", 
            direction="Input")
        # param16.value = ""
        # param16.category = "Output"
        param16.enabled = False
        params.append(param16)

        param17 = arcpy.Parameter( 
            displayName="Date Fields To Group", 
            name="date_fields", 
            datatype="GPString",
            parameterType="Optional", 
            direction="Input", 
            multiValue=True)
        param17.filter.type = "ValueList"
        param17.value = ""
        param17.category = "Grouping"
        params.append(param17)

        param18 = arcpy.Parameter( 
            displayName="Category Fields To Group", 
            name="cat_fields", 
            datatype="GPString",
            parameterType="Optional", 
            direction="Input", 
            multiValue=True)
        param18.filter.type = "ValueList"
        param18.value = ""
        param18.category = "Grouping"
        params.append(param18)

        # Get hosted feature service title
        param19 = arcpy.Parameter( 
            displayName="Hosted Feature Service Title",
            name="title",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        param19.category = "Publishing"
        params.append(param19)

        # Get folder
        param20 = arcpy.Parameter( 
            displayName="Folder",
            name="folder",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        param20.category = "Publishing"
        param20.value = "schedule_sync"
        params.append(param20)

        # Get tag
        param21 = arcpy.Parameter( 
            displayName="Tag",
            name="tag",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        param21.category = "Publishing"
        param21.value = "schedule_sync"
        params.append(param21)

        return params


    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True


    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        input_type = parameters[0].valueAsText
        xml_file_path = parameters[1].valueAsText

        # if input_type == "XML":
        #     # All Subject Areas supported for XML must be included in this list
        #     parameters[5].filter.list = ["Project", "WBS", "Activity"]
        #     parameters[1].enabled = True

        #     parameters[2].enabled = False
        #     parameters[3].enabled = False
        #     parameters[4].enabled = False

        # else:
        #     # All subject areas supported for EPPM must be include in this list
        #     parameters[5].filter.list = ["Project", "WBS", "Activity", "Activity Step"]
        #     parameters[1].enabled = False
        #     parameters[2].enabled = True
        #     parameters[3].enabled = True
        #     parameters[4].enabled = True
            
        # username = parameters[2].value
        # password = parameters[3].value
        # hostname = parameters[4].value
        username = None
        password = None
        hostname = None
        subjectArea = parameters[5].value

        stdFlds = self.getStandardFields(parameters[5].value)
        parameters[7].filter.list = stdFlds

        if parameters[5].value == "Project":
            parameters[6].value = None
            parameters[6].enabled = False
        else:
            parameters[6].enabled = True
            if xml_file_path:
                projs, projoids = self.readProjects(username, password, hostname, input_type, xml_file_path)
                parameters[6].filter.list =  projs
                udfFlds = self.getUDFFields(username, password, hostname, parameters[5].value, input_type, xml_file_path)
                parameters[8].filter.list = udfFlds 
                project = parameters[6].valueAsText
                codeFields = []
                if subjectArea == "Activity" and parameters[9].value:
                    if project is None:            
                        project = "*"
                    else:
                        projectIndex = parameters[6].filter.list.index(project)
                        codeFields, _ = self.retrieveCodeData(username, password, hostname, subjectArea, project, projectIndex, input_type, xml_file_path)
                flds = []
                if isinstance(parameters[7].valueAsText, str) and isinstance(parameters[8].valueAsText, str):
                    flds = parameters[7].valueAsText + ";" + parameters[8].valueAsText
                    flds = flds.split(";")
                elif (not isinstance(parameters[7].valueAsText, str)) and isinstance(parameters[8].valueAsText, str):
                    flds = parameters[8].valueAsText
                    flds = flds.split(";")
                elif isinstance(parameters[7].valueAsText, str) and (not isinstance(parameters[8].valueAsText, str)):
                    flds = parameters[7].valueAsText
                    flds = flds.split(";")
                for i, fld in enumerate(flds):
                    if fld.startswith("'") and fld.endswith("'"):
                        flds[i] = fld[1:-1]
                p6LinkFlds = flds + codeFields          
                parameters[10].filter.list = p6LinkFlds
                parameters[17].filter.list = p6LinkFlds
                parameters[18].filter.list = p6LinkFlds

        if parameters[5].value:
            if parameters[5].value == "Activity":
                parameters[9].enabled = True
        else:
            parameters[9].enabled = False
        # else:
        #     if parameters[5].value:
        #         if parameters[5].value == "Activity":
        #             parameters[9].enabled = True
        #     else:
        #         parameters[9].enabled = False

        # if parameters[13].value:
        #     if parameters[13].value == "Join Data - One to One":
        #         parameters[15].enabled = False
            # else:
            #     parameters[15].enabled = True

        if parameters[5].value != "Activity":
            parameters[9].enabled = False
        else:
            parameters[9].enabled = True

        return
    
    
    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""

        xml_file_path = parameters[1].valueAsText
        if not xml_file_path:
            parameters[1].setErrorMessage("Please provide an XML path.")
        # username = parameters[2].value
        # if not username:
        #     parameters[2].setErrorMessage("Please provide a username.")
        # password = parameters[3].value
        # if not password:
        #     parameters[3].setErrorMessage("Please provide a password.")
        # hostname = parameters[4].value
        # if not hostname:
        #     parameters[4].setErrorMessage("Please provide a host URL.")
    
        return


    def execute(self, parameters, messages):
        """The source code of the tool."""
        with tempfile.TemporaryDirectory() as path:
            arcpy.AddMessage("Temporary directory created.")

            arcpy.SetProgressor("step", "Loading parameters...",0, 11, 1)
            arcpy.SetProgressorPosition()

            input_type = parameters[0].valueAsText
            xml_path = parameters[1].valueAsText

            username = parameters[2].valueAsText
            password = parameters[3].valueAsText
            hostname = parameters[4].valueAsText

            # TODO: Change to feature class. No feature layers.
            # set workspace parameter from FC in map
            fc_source = parameters[11].valueAsText
            fc_name = str(Path(fc_source).name)
            temp_gdb = "sync_{}.gdb".format(fc_name)

            arcpy.SetProgressorPosition()
            arcpy.SetProgressorLabel("Creating temp gdb...")
            arcpy.CreateFileGDB_management(path, temp_gdb)
            out_gdb_path = os.path.join(path, temp_gdb)
            # arcpy.env.workspace = out_gdb_path

            p6_table = "p6table_{}".format(fc_name)
            # p6_table = cleanName(p6_table)
            table_path = os.path.join(out_gdb_path, p6_table)

            subjectArea = parameters[5].valueAsText

            project = parameters[6].valueAsText
            projectIndex = ""

            if project is None:
                project = "*"
            else:
                projectIndex = parameters[6].filter.list.index(project)

            stdFlds = parameters[7].valueAsText

            udfFlds = parameters[8].valueAsText

            includeCodes = parameters[9].valueAsText

            p6LinkFld = parameters[10].valueAsText
            p6LinkFld = cleanName(p6LinkFld)
            
            fcLinkFld = parameters[12].valueAsText

            rel_class_name = "rel_class_{}".format(fc_name)
            rel_class_name = cleanName(rel_class_name)

            date_fields = parameters[17].valueAsText

            cat_fields = parameters[18].valueAsText

            title = parameters[19].valueAsText
            folder_name = parameters[20].valueAsText
            tag = parameters[21].valueAsText

            join_status = ""
            if parameters[13].value == "Join Data - One to One":
                join_status = True
            elif parameters[13].value == "Relationship Class - Many to One":
                join_status = False

            arcpy.SetProgressorPosition()
            arcpy.SetProgressorLabel("Copying feature class to GDB...")
            arcpy.FeatureClassToFeatureClass_conversion(in_features=fc_source,
                                                        out_path=out_gdb_path,
                                                        out_name=fc_name)
            
            fc_path = os.path.join(out_gdb_path, fc_name)

            arcpy.SetProgressorPosition()
            arcpy.SetProgressorLabel("Retrieving data for standard fields...")
            standardData = self.retrieveStandardData(username, password, hostname, subjectArea, project, projectIndex, stdFlds, input_type, xml_path)  
            
            arcpy.SetProgressorPosition()
            arcpy.SetProgressorLabel("Standard fields table...")
            standardTable = self.createPopulateStandardFldsTable(out_gdb_path, p6_table, standardData )

            # retrieve data for user defined fields   
            arcpy.SetProgressorLabel("Retrieving data for user defined fields...")
            arcpy.SetProgressorPosition()
            if (udfFlds != None): 
                #arcpy.AddMessage(udfFlds)
                
                udfFldsAndData = []
                udfFldsAndData = self.retrieveUDFData(username, password, hostname, subjectArea, project, projectIndex, udfFlds, input_type, xml_path)
                if len(udfFldsAndData[1]) > 0:
                    udfTable = self.createPopulateUDFTable(out_gdb_path, "UDFFieldsP6", udfFldsAndData )
                    
                    # join both tables on common field
                    if subjectArea  == "Project":
                        arcpy.JoinField_management(standardTable, "ProjectId", udfTable, "ProjectObjectId" )
                    else:
                        arcpy.JoinField_management(standardTable, "ForeignObjectId", udfTable, "ForeignObjectId" ) 
                    arcpy.management.Delete(udfTable)
                else:
                    arcpy.AddMessage("No UDF data found")

            # retrieve data for code fields  
            # ActivityCodeType holds the type of Code and Name for Column/category
            # ActivityCode holds a single possible catagory values under a specific ActivityCodeType
            # Code holds the current code category for a given activity under a given code type
            arcpy.SetProgressorPosition()
            arcpy.SetProgressorLabel("Retrieving data for code fields...")
            if subjectArea == "Project" or subjectArea == "Activity":
                if includeCodes.upper() == "TRUE":
                    codeData = self.retrieveCodeData(username, password, hostname, subjectArea, project, projectIndex, input_type, xml_path)  
                    codeTable = self.createPopulateCodeFldsTable(out_gdb_path, "CodeFieldsP6", codeData )
                    if (codeTable is not None):
                        if subjectArea  == "Project":
                            arcpy.JoinField_management(standardTable, "ProjectId", codeTable, "ProjectObjectId" )
                        elif subjectArea  == "Activity":
                            arcpy.JoinField_management(standardTable, "ForeignObjectId", codeTable, "ActivityObjectId" )
                        arcpy.management.Delete(codeTable)

            if join_status:
                arcpy.SetProgressorPosition() 
                arcpy.SetProgressorLabel("Creating Joined Feature Class...")

                skip_col = ['ObjectID','OBJECTID','ProjectId','ForeignObjectId','CodeFieldsP6','ProjectObjectId','ActivityObjectId']

                for f in arcpy.ListFields(standardTable):
                    if f.name in skip_col:
                        continue
                    newName = f.name + "_p6"
                    newAlias = f.aliasName + "_p6"
                    if len(newName) > 30:
                        newName = f.name[:28] + "_p6"
                    if len(newAlias) > 30:
                        newAlias = f.aliasName[:28] + "_p6"
                    arcpy.AlterField_management(standardTable, f.name, newName, newAlias)
                p6LinkFld = p6LinkFld + "_p6"
                if len(p6LinkFld) > 30:
                    p6LinkFld = p6LinkFld[:28] + "_p6"

                allFields = []
                for f in arcpy.ListFields(standardTable):
                    found = False
                    for skip in skip_col:
                        if skip.lower() in f.name.lower():
                            found = True
                    if not found:
                        allFields.append(f.name)

                arcpy.DeleteField_management(fc_path, allFields)

                arcpy.JoinField_management(fc_path, 
                                            fcLinkFld, 
                                            standardTable, 
                                            p6LinkFld, 
                                            fields=allFields)

                arcpy.AddMessage("Finished joining data")

            elif not join_status:
                # Create Relationship Class
                arcpy.SetProgressorPosition() 
                arcpy.SetProgressorLabel("Creating Relationship Class...")
                arcpy.AddMessage("Will be creating relationship class")
                rel_path = os.path.join(out_gdb_path, rel_class_name)
                arcpy.CreateRelationshipClass_management(
                    origin_table=table_path,
                    destination_table=fc_path,
                    out_relationship_class=rel_path,
                    relationship_type="SIMPLE",
                    forward_label='P6',
                    backward_label='FC',
                    cardinality="ONE_TO_MANY",
                    origin_primary_key=p6LinkFld,
                    origin_foreign_key=fcLinkFld
                    )

            if isinstance(date_fields, str):
                date_fields = date_fields.split(";")
                for f in date_fields:
                    self.group_by_date(table_path,fc_path,p6LinkFld, fcLinkFld, f)

            if isinstance(cat_fields, str):
                cat_fields = cat_fields.split(";")
                for f in cat_fields:
                    self.group_by_category(table_path,fc_path,p6LinkFld, fcLinkFld, f)

            # Connect to gis
            g = GIS('pro')
            arcpy.AddMessage("Authentification complete.")
            arcpy.AddMessage("Starting sync to ArcGIS Organization.")
            published_item = syncSchedule(out_gdb_path, path, temp_gdb, g, title, folder_name, tag)
            arcpy.AddMessage("Sync to ArcGIS Organization complete.")
            
            validatePublishedTable(
                n_table_rows_source=int(arcpy.management.GetCount(table_path)[0]), 
                published_item=published_item)

            # Validate published feature service data
            validatePublishedFeatureClass(
                source_fc_path=fc_path, 
                published_item=published_item)
            
            arcpy.AddMessage("Tool complete")
            arcpy.SetProgressorPosition() 
            arcpy.AddMessage("Start cleanup")
            try:
                arcpy.management.Delete(table_path)
                arcpy.management.Delete(fc_path)
                arcpy.management.Delete(fc_path)
                arcpy.management.Delete(out_gdb_path)
                arcpy.AddMessage("Temp file cleanup complete.")
            except:
                arcpy.AddMessage("System did not allow file cleanup.")
        return


    def retrieveCodeData(self, username:str, password:str, hostname:str, subjectArea:str, project:str, projectIndex:int, input_type: str, xml_file_path:str) -> list:
        """
        Get the Code Data for the chosen subject area.
        Return a list containing two lists. 
        The first list is the unique subject area code names.
        The second list is all rows in the project dictionary.
        """
        if input_type == "XML":
            """lstUniqSubjectAreaCodeNames is a list with all ProjectCodeType or ActivityCodeType Names to use as field names.
            allRows is a list of lists. Each sublist represents one row. The row follows the order of lstUniqSubjectAreaCodeNames.
            So each index is associated with a given column."""
            lstUniqSubjectAreaCodeNames = []
            allRows = []
            if subjectArea == "Activity":
                projs, projoids = self.readProjects(username, password, hostname, input_type, xml_file_path)            
                projId = projoids[projectIndex]
                tree = ET.parse(xml_file_path)
                root = tree.getroot()

                # Get the Project object from the XML file
                proj_obj = ''
                for c in root: 
                    obj_id = ''
                    if c.tag.split('}')[-1].strip() in ['Project','BaselineProject']:
                        obj_id = [gc.text for gc in c if gc.tag.split('}')[-1].strip() == 'ObjectId'][0]
                        if obj_id == projId:
                            proj_obj = c  # store our project object
 
                # Get the ActivtyCodeType objects
                aCodeTypeNodes = [c for c in proj_obj if "ActivityCodeType" == c.tag.split('}')[-1].strip()]
                codeTypes = {}
                for c in aCodeTypeNodes:
                    oid = [x.text for x in c if "ObjectId"==x.tag.split("}")[-1].strip()][0]
                    name = [x.text for x in c if "Name"==x.tag.split("}")[-1].strip()][0]
                    codeTypes[oid] = {"CodeType_Name":name, 
                                      "CodeValues":{}}

                # Get the ActivtyCode objects
                aCodeNodes = [c for c in proj_obj if "ActivityCode" == c.tag.split('}')[-1].strip()]
                for c in aCodeNodes:
                    oid = [x.text for x in c if "ObjectId"==x.tag.split("}")[-1].strip()][0]
                    type_oid = [x.text for x in c if "CodeTypeObjectId"==x.tag.split("}")[-1].strip()][0]
                    code_value = [x.text for x in c if "CodeValue"==x.tag.split("}")[-1].strip()][0]
                    codeTypes[type_oid]["CodeValues"][oid] = code_value

                # Get the Activity objects
                aNodes = [c for c in proj_obj if "Activity" == c.tag.split('}')[-1].strip()]

                # Get list of unique field names
                code_type_oids = []
                lstUniqSubjectAreaCodeNames = ["ActivityObjectId"]
                for type_oid,v in codeTypes.items():
                    type_name = v["CodeType_Name"]
                    # Check field names for validity
                    # add underscore if starts with number
                    if type_name[0] in ['0','1','2','3','4','5','6','7','8','9']:
                        type_name = "_" + type_name
                        type_name = type_name.replace(" ", "_")
                        type_name = type_name.replace("-", "_")

                    if not type_name == "ProjectObjectId" and not type_name == "ActivityObjectId":
                        if not type_name in lstUniqSubjectAreaCodeNames:
                            code_type_oids.append(type_oid)
                            lstUniqSubjectAreaCodeNames.append(type_name)

                # Get list of activities
                # For each activity get all code values
                # Append values in same order based on order of field names list
                for c in aNodes:
                    oid = [x.text for x in c if "ObjectId"==x.tag.split("}")[-1].strip()][0]
                    codes = {}
                    codeNodes = [x for x in c if "Code"==x.tag.split("}")[-1].strip()]
                    for n in codeNodes:
                        TypeObjectId = [x.text for x in n if "TypeObjectId"==x.tag.split("}")[-1].strip()][0]
                        ValueObjectId = [x.text for x in n if "ValueObjectId"==x.tag.split("}")[-1].strip()][0]
                        codes[TypeObjectId] = ValueObjectId  # Key is type. Value is value.

                    row = [oid]
                    for type_oid in code_type_oids:
                        v = codeTypes[type_oid]
                        type_name = v["CodeType_Name"]
                        # ignore if ProjectObjectId or ActivityObjectId as oid already added
                        if not type_name == "ProjectObjectId" and not type_name == "ActivityObjectId":
                            if type_oid in codes:
                                value = v["CodeValues"][codes[type_oid]]
                                row.append(value)
                            else:
                                row.append(None)
                    allRows.append(row)
            return [lstUniqSubjectAreaCodeNames, allRows]

        # if project == "*": # Projects
        #     filter = ""
        #     flds = ["ProjectCodeTypeName", "ProjectCodeValue", "ProjectObjectId"]
        # else:
        #     # get project ID from within parentheses at end of string
        #     #projId = project[project.find('(') + 1:project.find(')')]
        #     projs, projoids = self.readProjects(username, password, hostname, input_type, xml_file_path)            
        #     projId = projoids[projectIndex]
        #     filter = "ProjectObjectId='" + projId + "'"            
        #     flds = ["ActivityCodeTypeName", "ActivityCodeValue", "ActivityObjectId", "ProjectObjectId"]

        # url = ""
        # if subjectArea == "Project":
        #     url = hostname + "/services/ProjectCodeAssignmentService?wsdl"                  
        # elif subjectArea == "Activity":
        #     url = hostname + "/services/ActivityCodeAssignmentService?wsdl"

        # # client = Client(url, wsse=UsernameToken(username, password))  

        # if subjectArea == "Project":            
        #     resp = client.service.ReadProjectCodeAssignments(flds,Filter=filter) 
        #     # get all projectObjectIDs
        #     OIDs = [i["ProjectObjectId"] for i in resp if i["ProjectObjectId"] ]
        #     # get all possible code field names
        #     subjectAreaCodeNames = [i["ProjectCodeTypeName"] for i in resp if i["ProjectCodeTypeName"] ]

        # elif subjectArea == "Activity":            
        #     resp = client.service.ReadActivityCodeAssignments(flds,Filter=filter)    
        #     # get all activityObjectIDs
        #     OIDs = [i["ActivityObjectId"] for i in resp if i["ActivityObjectId"] ]
        #     # get all possible code field names
        #     subjectAreaCodeNames = [i["ActivityCodeTypeName"] for i in resp if i["ActivityCodeTypeName"] ]

        # # get unique values
        # uniqOIDs = set(OIDs)
        # # arcpy.AddMessage(uniqOIDs)
        
        # # get unique values
        # uniqSubjectAreaCodeNames = set(subjectAreaCodeNames)
        # lstUniqSubjectAreaCodeNames = list(uniqSubjectAreaCodeNames)
        # if subjectArea == "Project":
        #     lstUniqSubjectAreaCodeNames.insert(0, "ProjectObjectId")
        # elif subjectArea == "Activity":
        #     lstUniqSubjectAreaCodeNames.insert(0, "ActivityObjectId")
        # # arcpy.AddMessage(lstUniqSubjectAreaCodeNames)  
           
        # # a dictionary whose value is another dictionary - stores all proj and their data
        # oidDataDict = {}
        
        # for item in resp:
        #     if subjectArea == "Project":
        #         oid = item["ProjectObjectId"]
        #     elif subjectArea == "Activity":
        #         oid = item["ActivityObjectId"]
            
        #     # if OID already exists , get the corresponding dictionary
        #     if oid in oidDataDict.keys():
        #         oidFldsDict = oidDataDict[oid]
        #         # arcpy.AddMessage("in keys")
        #     else:
        #         oidFldsDict = {}
                           
        #     if subjectArea == "Project":                
        #         oidFldsDict[item["ProjectCodeTypeName"]] = item["ProjectCodeValue"]                
        #     elif subjectArea == "Activity":               
        #         oidFldsDict[item["ActivityCodeTypeName"]] = item["ActivityCodeValue"]
            
        #     oidDataDict[oid] = oidFldsDict
            
        # # arcpy.AddMessage(oidDataDict)

        # # list of lists
        # allRows = []
        
        # # iterate over proj dictionary and copy value in respective posistion in list
        # # if proj does not have a particular field , add None as placeholder.
        # # this list will be added as row in table
        # for oid, data in oidDataDict.items():
        #     row = [oid]
        #     for fld in lstUniqSubjectAreaCodeNames:
        #         # ignore if ProjectObjectId or ActivityObjectId as oid already added
        #         if not fld == "ProjectObjectId" and not fld == "ActivityObjectId":                    
        #             # does the code field exist in this particular project
        #             if fld in data.keys():
        #                 row.append(data[fld])
        #             else:
        #                 row.append(None)
        #     allRows.append(row)
        # # arcpy.AddMessage(allRows)
        # return [lstUniqSubjectAreaCodeNames, allRows]
        
        
    def createPopulateCodeFldsTable(self, path:str, tableName:str, data:list): 
        """Create and Populate Code Fields Table.
        data: list with [lstFieldnames, rowsOfdata]
        An arcpy table object is returned.
        """
        # data is [lstFieldnames, rowsOfdata]
        if len(data) > 0:
            lstFields = data[0]
            # create valid field 
            for i,name in enumerate(lstFields):
                if not lstFields[i][0].isalpha():
                    lstFields[i] = "_" + lstFields[i]
            lstData = data[1]
            if len(lstData) > 0:
                tbl = arcpy.CreateTable_management(path, tableName)
                for fldName in lstFields:
                    # arcpy.AddMessage(fldName)
                    # add field
                    arcpy.AddField_management(tbl, fldName, "TEXT") # all TEXT for now
                # get the newly added fields since the field names may not be same as (underscore added etc)
                # for example - 'Estimated Project Size' is 'Estimated_Project_Size' in table
                tableFields = arcpy.ListFields(tbl)
                tableFieldNames = [tblFld.name for tblFld in tableFields ]                 
                tableFieldNames.remove('OBJECTID')
                    
                # populate table         
                with arcpy.da.InsertCursor(tbl,(tableFieldNames) ) as cursor:                
                    for dataRow in lstData:
                        # arcpy.AddMessage(dataRow)
                        cursor.insertRow((dataRow))  
                
                return tbl
            else:
                return None
        else:
            return None
    

    def createPopulateStandardFldsTable(self, path:str, tableName:str, data:list):
        """Create and Populate standard fields table.
        data: list of lists. 
            The first item is used to get the fields and datatypes.
            Each item in the list represents a row of data.
        Returns an arcpy table object."""
        #arcpy.AddMessage(path)
        if len(data) > 0:
            tbl = arcpy.CreateTable_management(path, tableName)
                    
            lstFldNames = []
            # get first item of list only (this is another list that has dictionaries) - need datatypes for fields
            firstItem = data[0]
            #arcpy.AddMessage(firstItem)
            for dictflds in firstItem:
                for key,val in dictflds.items():
                    #arcpy.AddMessage(key + "," + str(val))
                    if key == "DataType":
                        if val == "Text":
                            fldType = "TEXT"
                        elif val == "Double":
                            fldType = "DOUBLE"
                        elif val == "Integer":
                            fldType = "LONG"
                        else:
                            fldType = "DATE"
                    
                    if key == "Name":
                        fldName = val
                        lstFldNames.append(fldName)
                        
                # add field
                arcpy.AddField_management(tbl, fldName, fldType)
                
            # populate table         
            with arcpy.da.InsertCursor(tbl,(lstFldNames) ) as cursor:
                # list that contains lists. Each interior list has a dictionary
                for dataRow in data:
                    lstVals = []
                    for dictflds in dataRow:
                        for key,val in dictflds.items():
                            if key == "Value":
                                value = val
                        lstVals.append(value)
                    
                    cursor.insertRow((lstVals))  
            
            return tbl
        else:
            return None
            

    def createPopulateUDFTable(self, path:str, tableName:str, udfFldsAndData:list):
        """Create and populated a UDF table.
        udfFldsAndData: A list. 
            The first item represents the fields and data types. 
            The second item represents the rows of data.
        Return the table object."""
        #arcpy.AddMessage(path)
        udfTableFields = udfFldsAndData[0]
        udfRowsPerSubjectArea = udfFldsAndData[1]
        
        if len(udfRowsPerSubjectArea) > 0:
            if arcpy.Exists(os.path.join(path, tableName)):
                arcpy.management.Delete(os.path.join(path, tableName))
            tbl = arcpy.CreateTable_management(path, tableName)
                    
            lstUDFFldNames = []
            dictFldNamesAndTypes = {}
            
            for dictflds in udfTableFields:
                for key,val in dictflds.items():
                    #arcpy.AddMessage(key + "," + str(val))
                    if key == "DataType":
                        if val == "Text":
                            fldType = "TEXT"
                        elif val == "Double":
                            fldType = "DOUBLE"
                        elif val == "Integer":
                            fldType = "LONG"
                        else:
                            fldType = "DATE"
                    
                    if key == "FieldName":
                        fldName = val
                        lstUDFFldNames.append(fldName)
                
                dictFldNamesAndTypes[fldName] = fldType
                # add field
                arcpy.AddField_management(tbl, fldName, fldType)
            
            # get the newly added fields since the field names may not be same as UDF titles
            # for example - UDF field 'Six Sigma Total Savings ($)' is created as 'Six_Sigma_Total_Savings____' in table
            tableFields = arcpy.ListFields(tbl)
            tableFieldNames = [tblFld.name for tblFld in tableFields ]
            # arcpy.AddMessage(tableFieldNames)
            # for field in tableFields:
            #     arcpy.AddMessage("{0} is a type of {1} with a length of {2}"
            #         .format(field.name, field.type, field.length))
                    
            tableFieldNames.remove('OBJECTID')
            #arcpy.AddMessage(tableFieldNames)
            
            # arcpy.AddMessage(udfRowsPerSubjectArea)
            # populate table
            with arcpy.da.InsertCursor(tbl,(tableFieldNames) ) as cursor:
                # list of dictionary
                for dataDict in udfRowsPerSubjectArea:
                    lstInputValues = []
                    #arcpy.AddMessage("pop UDF table " + str(dataDict))
                    for foreignOID,lstValues in dataDict.items():     
                         
                        # SOAP call does not return UDF fields that have no values.
                        # so add empty value for fields that are not sent back
                        # so that lstInputValues has the correct number/order of entries
                            
                        for fldName in lstUDFFldNames: 
                            if fldName == "ForeignObjectId":
                                lstInputValues.append(foreignOID)   
                            else:
                                # list(fldDict)[0] - to get value of  key
                                # check if field exists - means it was returned by the SOAP call
                                fldExists = [fldDict for fldDict in lstValues if list(fldDict)[0] == fldName]   
                                if len(fldExists) == 0:
                                    lstInputValues.append(None) 
                                else:
                                    lstInputValues.append(fldExists[0][fldName])
                                           
                    cursor.insertRow((lstInputValues))   
                
                    #arcpy.AddMessage(lstInputValues)
               
            return tbl
        else:
            return None


    def retrieveUDFData(self, username:str, password:str, hostname:str, subjectArea:str, project:str, projectIndex:int, reqFlds:str, input_type:str, xml_file_path:str) -> list:
        """Get UDF Data.
        Returns a list with two lists.
        The first list us the UDF fields.
        The second list is the UDF row data.
        """
        if input_type=='XML':

            if not reqFlds:
                return [[],[]]

            tree = ET.parse(xml_file_path)
            root = tree.getroot()
            udfRowsPerSubjectArea = []  # list of Objects  
            udfTableFields = []  # list of Objects
            udfTypes = {}
            # explicitly add ForeignObjectId and ProjectObjectId fields to list of fields to be created in table
            udfTableFields.append({"FieldName": "ForeignObjectId", "DataType": "Text" })
            udfTableFields.append({"FieldName": "ProjectObjectId", "DataType": "Text" })
            for c in root: 
                if 'UDFType' == c.tag.split('}')[-1].strip():
                    udf_subject_area = [gc.text for gc in c if gc.tag.split('}')[-1].strip() == 'SubjectArea'][0]
                    if subjectArea == udf_subject_area:
                        udf_obj_id = [gc.text for gc in c if gc.tag.split('}')[-1].strip() == 'ObjectId'][0]
                        udf_data_type = [gc.text for gc in c if gc.tag.split('}')[-1].strip() == 'DataType'][0]
                        if udf_data_type == "Text":                        
                            udf_data_type = "Text"
                        elif udf_data_type == "Double":                        
                            udf_data_type = "Double"
                        elif udf_data_type == "Integer":                        
                            udf_data_type = "Integer"
                        elif udf_data_type == "Start Date":                                           
                            udf_data_type = "Date"
                        elif udf_data_type == "Finish Date":                        
                            udf_data_type = "Date"
                        elif udf_data_type == "Cost":                        
                            udf_data_type = "Double"
                        elif udf_data_type == "Indicator":                        
                            udf_data_type = "Text"
                        elif udf_data_type == "Code":                        
                            udf_data_type = "Text"
                        udf_title = [gc.text for gc in c if gc.tag.split('}')[-1].strip() == 'Title'][0]
                        if udf_title.startswith("'") == True and udf_title.endswith("'") == True:
                            udf_title = udf_title[1:-1]
                        field_count = len([x for x in udfTableFields if x["FieldName"]==udf_title])
                        if field_count == 0:
                            udfTableFields.append({"FieldName": udf_title, "DataType": udf_data_type })
                            udfTypes[int(udf_obj_id)] = {"FieldName": udf_title, "DataType": udf_data_type}

            # Get udfRowsPerSubjectArea values
                # udfRowsPerSubjectArea is a list of dictionaries
                # Each dictionary represents one row
                # Each dictionary has one key, which is the ProjectId for project, or ForignId for WBS and activity
                # The value is a list of dictionaries.
                # Each dictonary has the field title as the key and the value as the dictionary value.
                # ForeignObjectId and ProjectObjectId are always included.
                # There will also be a dictionary for each UDF value
            
            flds = reqFlds.split(";") 
            fldsWithoutQuotes = []
            for fld in flds:
                if fld.startswith("'") == True and fld.endswith("'") == True:
                    fldsWithoutQuotes.append(fld[1:-1])
                else:
                    fldsWithoutQuotes.append(fld)

            reservedFields = ['ObjectId', 'ProjectObjectId', 'ForeignObjectId']
            for f in reservedFields:
                while f in fldsWithoutQuotes:
                    fldsWithoutQuotes.remove(f)

            if subjectArea == "Project":
                # Loop through all projects and baseline projects
                tree = ET.parse(xml_file_path)
                root = tree.getroot()
                for c in root:
                    if c.tag.split("}")[-1].strip() in ['Project','BaselineProject']:
                        proj_ObjectId = [x for x in c if 'ObjectId' == x.tag.split("}")[-1]][0].text
                        row = {int(proj_ObjectId): [{'ProjectObjectId': int(proj_ObjectId)}] }
                        # Get list of UDF values and TypeId values
                        udfs = [x for x in c if 'UDF' == x.tag.split("}")[-1]]  # VERIFY this the UDF organization
                        udfs_dict = {}
                        for udf in udfs:
                            typeObjectId = [x for x in udf if 'TypeObjectId' == x.tag.split("}")[-1]][0].text
                            textValue = [x for x in udf if not 'TypeObjectId' == x.tag.split("}")[-1]][0].text
                            udfFieldName = udfTypes[int(typeObjectId)]['FieldName']
                            if udfFieldName in fldsWithoutQuotes:  # Only save the user chosen fields
                                # Get formated data
                                udfDataType = udfTypes[int(typeObjectId)]['FieldName']
                                udfValue = self.castType( textValue, udfDataType)
                                udfs_dict[udfFieldName] = udfValue
                        for f in fldsWithoutQuotes:
                            if f in udfs_dict:
                                row[int(proj_ObjectId)].append({f: udfs_dict[f]})
                            else:
                                row[int(proj_ObjectId)].append({f: None})

                        # Loop through user selected UDF and add the fields and their value to the list
                        if len(fldsWithoutQuotes) > 0:
                            udfRowsPerSubjectArea.append(row)

            else:  # we have WBS or Activity
                projs, projoids = self.readProjects(username, password, hostname, input_type, xml_file_path)
                projId = projoids[projectIndex] # Index for chosen project
                
                # Find the project root
                proj_obj = ''
                for c in root: 
                    obj_id = ''
                    if c.tag.split('}')[-1].strip() in ['Project','BaselineProject']:
                        obj_id = [gc.text for gc in c if gc.tag.split('}')[-1].strip() == 'ObjectId'][0]
                        if obj_id == projId:
                            proj_obj = c  # store our project object

                # Get the WBS or Activity objects
                nodes = [c for c in proj_obj if subjectArea == c.tag.split('}')[-1].strip()]

                # Get all fields and values for each node
                for node in nodes:
                    itemObjId = [x for x in node if x.tag.split('}')[-1].strip() == 'ObjectId'][0].text
                    row = {int(itemObjId): [{'ProjectObjectId': int(projId)}]}
                    udfs = [x for x in node if 'UDF' == x.tag.split("}")[-1]]  # VERIFY this the UDF organization
                    udfs_dict = {}
                    for udf in udfs:
                        typeObjectId = [x for x in udf if 'TypeObjectId' == x.tag.split("}")[-1]][0].text
                        textValue = [x for x in udf if not 'TypeObjectId' == x.tag.split("}")[-1]][0].text
                        udfFieldName = udfTypes[int(typeObjectId)]['FieldName']
                        if udfFieldName in fldsWithoutQuotes:  # Only save the user chosen fields
                            # Get formated data
                            udfDataType = udfTypes[int(typeObjectId)]['FieldName']
                            udfValue = self.castType( textValue, udfDataType)
                            udfs_dict[udfFieldName] = udfValue
                    for f in fldsWithoutQuotes:
                        if f in udfs_dict:
                            row[int(itemObjId)].append({f: udfs_dict[f]})
                        else:
                            row[int(itemObjId)].append({f: None})

                    # Loop through user selected UDF and add the fields and their value to the list
                    if len(fldsWithoutQuotes) > 0:
                        udfRowsPerSubjectArea.append(row)

            return [udfTableFields, udfRowsPerSubjectArea]
            # Activity example output
            # udfTableFields:
            # [{'FieldName': 'ForeignObjectId', 'DataType': 'Text'}, {'FieldName': 'ProjectObjectId', 'DataType': 'Text'}, {'FieldName': 'GIS_ID', 'DataType': 'Text'}]
            # udfRowsPerSubjectArea:
            # [{126498: [{'GIS_ID': 'A1'}, {'ProjectObjectId': 4886}]}, {126499: [{'GIS_ID': 'A1'}, {'ProjectObjectId': 4886}]}, {126500: [{'GIS_ID': 'A1'}, {'ProjectObjectId': 4886}]}, {126501: [{'GIS_ID': 'A1'}, {'ProjectObjectId': 4886}]}, {126502: [{'GIS_ID': 'A1'}, {'ProjectObjectId': 4886}]}, {126503: [{'GIS_ID': 'A1'}, {'ProjectObjectId': 4886}]}, {126504: [{'GIS_ID': 'A1'}, {'ProjectObjectId': 4886}]}, {126505: [{'GIS_ID': 'A1'}, {'ProjectObjectId': 4886}]}, {126506: [{'GIS_ID': 'A2'}, {'ProjectObjectId': 4886}]}, {126507: [{'GIS_ID': 'A2'}, {'ProjectObjectId': 4886}]}, {126508: [{'GIS_ID': 'A2'}, {'ProjectObjectId': 4886}]}, {126509: [{'GIS_ID': 'A2'}, {'ProjectObjectId': 4886}]}, {126510: [{'GIS_ID': 'A2'}, {'ProjectObjectId': 4886}]}, {126511: [{'GIS_ID': 'A2'}, {'ProjectObjectId': 4886}]}, {126512: [{'GIS_ID': 'A2'}, {'ProjectObjectId': 4886}]}, {126513: [{'GIS_ID': 'A2'}, {'ProjectObjectId': 4886}]}, {126514: [{'GIS_ID': 'A2'}, {'ProjectObjectId': 4886}]}, {126515: [{'GIS_ID': 'A2'}, {'ProjectObjectId': 4886}]}, {126516: [{'GIS_ID': 'A2'}, {'ProjectObjectId': 4886}]}, {126517: [{'GIS_ID': 'A2'}, {'ProjectObjectId': 4886}]}, {126518: [{'GIS_ID': 'A2'}, {'ProjectObjectId': 4886}]}, {126519: [{'GIS_ID': 'Int-H1'}, {'ProjectObjectId': 4886}]}, {126520: [{'GIS_ID': 'Int-H1'}, {'ProjectObjectId': 4886}]}, {126521: [{'GIS_ID': 'Int-H1'}, {'ProjectObjectId': 4886}]}, {126522: [{'GIS_ID': 'Int-H1'}, {'ProjectObjectId': 4886}]}, {126523: [{'GIS_ID': 'Int-H1'}, {'ProjectObjectId': 4886}]}, {126524: [{'GIS_ID': 'A1'}, {'ProjectObjectId': 4886}]}, {126525: [{'GIS_ID': 'A1'}, {'ProjectObjectId': 4886}]}, {126526: [{'GIS_ID': 'A1'}, {'ProjectObjectId': 4886}]}, {126527: [{'GIS_ID': 'A1'}, {'ProjectObjectId': 4886}]}, {126528: [{'GIS_ID': 'A1'}, {'ProjectObjectId': 4886}]}, {126529: [{'GIS_ID': 'A1'}, {'ProjectObjectId': 4886}]}]

        # url = hostname + "/services/UDFValueService?wsdl"
        # client = Client(url, wsse=UsernameToken(username, password))   
        
        # # some of the UDF fields have single quotes about them - remove them
        # flds = reqFlds.split(";") 
        # fldsWithoutQuotes = []
        # for fld in flds:
        #     if fld.startswith("'") == True and fld.endswith("'") == True:
        #        fldsWithoutQuotes.append(fld[1:-1])
        #     else:
        #        fldsWithoutQuotes.append(fld)
        
        # # need this additional filter - since fieldname is stored in UDFTypeTitle       
        # filterUDFTypeTitle = ""
        # for fldWithoutQuotes in fldsWithoutQuotes:
        #     filterUDFTypeTitle += "UDFTypeTitle='" + fldWithoutQuotes + "' OR "
        # filterUDFTypeTitle = filterUDFTypeTitle[:-4]
        # filterUDFTypeTitle = "(" + filterUDFTypeTitle + ")"
        # #arcpy.AddMessage(filterUDFTypeTitle)
        
        # # specify metadats fields needed
        # udfMetadataflds = ["UDFTypeTitle", "UDFTypeSubjectArea","ProjectObjectId", "Text" , "Double", "Integer", \
        #                     "Cost", "Indicator","StartDate", "FinishDate", "ForeignObjectId"]  # fails on "Code"
                   
        # #arcpy.AddMessage(udfMetadataflds)
        
        # if project == "*":
        #     filter = "UDFTypeSubjectArea='" + subjectArea + "' AND " + filterUDFTypeTitle  
        # else:
        #     # get project ID from within parentheses at end of string
        #     #projId = project[project.find('(') + 1:project.find(')')]
        #     projs, projoids = self.readProjects(username, password, hostname, input_type, xml_file_path)
        #     projId = projoids[projectIndex]
        #     filter = "ProjectObjectId='" + projId + "' AND UDFTypeSubjectArea='" + subjectArea + "' AND " + filterUDFTypeTitle  

        # resp = client.service.ReadUDFValues(udfMetadataflds,Filter=filter)
      
        # udfRowsPerSubjectArea = []    # list of Objects  
        # udfTableFields = []  # list of Objects 
        # # explicitly add ForeignObjectId and ProjectObjectId fields to list of fields to be created in table
        # udfTableFields.append({"FieldName": "ForeignObjectId", "DataType": "Text" })
        # udfTableFields.append({"FieldName": "ProjectObjectId", "DataType": "Text" })
                                 
        # for item in resp:
        #     #arcpy.AddMessage("***" + str(item))           
        #     projectData = {}
            
        #     # get the fields that have to be added to UDF table
        #     for fldWithoutQuotes in fldsWithoutQuotes:
        #         if item["UDFTypeTitle"] == fldWithoutQuotes:                    
        #             # check if field already exists in list of objects
        #             #arcpy.AddMessage("check " + fldWithoutQuotes)
        #             fldExists = [tableFld for tableFld in udfTableFields if tableFld["FieldName"] == item["UDFTypeTitle"]]
                    
        #             #arcpy.AddMessage(fldExists)
        #             #arcpy.AddMessage(len(fldExists))
        #             #arcpy.AddMessage(item["UDFTypeDataType"] + "," + item["UDFTypeTitle"])
        #             if len(fldExists) == 0:
        #                 if item["UDFTypeDataType"] == "Text":                        
        #                     datatype = "Text"
        #                 elif item["UDFTypeDataType"] == "Double":                        
        #                     datatype = "Double"
        #                 elif item["UDFTypeDataType"] == "Integer":                        
        #                     datatype = "Integer"
        #                 elif item["UDFTypeDataType"] == "Start Date":                                           
        #                     datatype = "Date"
        #                 elif item["UDFTypeDataType"] == "Finish Date":                        
        #                     datatype = "Date"
        #                 elif item["UDFTypeDataType"] == "Cost":                        
        #                     datatype = "Double"
        #                 elif item["UDFTypeDataType"] == "Indicator":                        
        #                     datatype = "Text"
        #                 elif item["UDFTypeDataType"] == "Code":                        
        #                     datatype = "Text"
                        
        #                 udfTableFields.append({"FieldName":item["UDFTypeTitle"], "DataType": datatype })
        #                 #arcpy.AddMessage(str(udfTableFields))

        #     # data response contains several field objects per project ID/ForeignObjectId. 
        #     # So create a list of rows - each row corresponds to a projectID/ForeignObjectId
        #     # and has fields for that specific project            
            
        #     # projectData is of the format {projID: [{field1: value1}, {field2: value2},{field2: value2}]}
        #     # udfRowsPerSubjectArea is of the format [projectData,projectData,projectData]
                       
        #     if item["UDFTypeDataType"] == "Start Date":                                           
        #         val = item["StartDate"]
        #     elif item["UDFTypeDataType"] == "Finish Date":                        
        #         val = item["FinishDate"]
        #     else:
        #         val = item[item["UDFTypeDataType"]]    
        #     udfTitle = item["UDFTypeTitle"]   
            
        #     #arcpy.AddMessage("*" + str(val) + "," + udfTitle + ',' + str(item["ForeignObjectId"]) + "," + str(item["ProjectObjectId"]))

        #     # check if dictionary key is same as ForeignObjectId value
        #     projRowExists = [projRow for projRow in udfRowsPerSubjectArea if list(projRow)[0] == item["ForeignObjectId"]]
            
        #     # if projectRow already exists , append to it
        #     # else create a new projectRow
        #     # arcpy.AddMessage("projRowExists " + str(projRowExists))
        #     if len(projRowExists) == 0:                                
        #         projectData[item["ForeignObjectId"]] = [{udfTitle: val}, {"ProjectObjectId": item["ProjectObjectId"]}]                               
        #         udfRowsPerSubjectArea.append(projectData)                 
        #     else:                
        #         projDict = projRowExists[0]
        #         # get the list corresponding to ForeignObjectId - dict.values() returns view
        #         # https://docs.python.org/3/library/stdtypes.html#dictionary-view-objects
        #         projectData = list(projDict.values())[0]   
        #         projectData.append({udfTitle: val})
        #         #udfRowsPerSubjectArea.append(str(projectData))                                           

        # return [udfTableFields, udfRowsPerSubjectArea]


    def retrieveStandardData(self, username:str, password:str, hostname:str, subjectArea:str, project:str, projectIndex:int, reqFlds:str, input_type:str, xml_file_path:str) -> list:
        """Get the standard data.
        Returns a list of standard data rows.
        The data format is one list with all standard data
        where each item in the list is a list representing a row.
        Each row is a list of dictionary objects.
        Each dictionary object has a Value, DataType, and Name key
        """

        reqData = []
        fldsDataTypes = self.getStandardFieldsDataTypes(subjectArea)
        flds = reqFlds.split(";")  # Get list of fields to use
        # Remove conflicting field

        resp = []  # variable to hold response from XML or EPPM

        if project == "*":
            filter = ""
            projId = ""

        else: 
            # get project ID from within parentheses at end of string
            projs, projoids = self.readProjects(username, password, hostname, input_type, xml_file_path)
            projId = projoids[projectIndex]
            # arcpy.AddMessage("The Project ID is: " + projId)
            #projId = project[project.find('(') + 1:project.find(')')]
            if subjectArea  == "Project":
                filter = "ProjectId='" + projId + "'"
            else:
                filter = "ProjectObjectId='" + projId + "'"
                flds.append("ProjectObjectId")  # have to explicitly call ProjectObjectId - else it returns None
                flds.append("ObjectId") # this will be stored as ForeignObjectId

        if input_type=='XML':
            tree = ET.parse(xml_file_path)
            root = tree.getroot()
            # If subject area Projects get list of projects
            # If subject area WBS get list of WBS
            # If subject area Actvities get list of Activities

            if subjectArea  == "Project":
                # Loop through all projects
                # Get all project fields and values for each project
                for c in root: 
                    if c.tag.split('}')[-1].strip() in ['Project','BaselineProject']:
                        row = {}
                        for gc in c:
                            field_name = gc.tag.split('}')[-1].strip()  # Get field name
                            if field_name in fldsDataTypes:  # Only use fields listed in the data types dictionary
                                d_type = fldsDataTypes[field_name]  # Get data type for field
                                field_value = gc.text  # Get value from XML
                                field_value = self.castType(field_value, d_type) # cast field to proper datatype
                                row[field_name] = field_value  # Add value to row dictionary
                        resp.append(row)
                # Response is a list of dictionaries
                # each dictionary represents a row
                # each row has all columns
                # the keys are the column names
                # the values are the row value
            else:
                # Get the Project object from the XML file
                proj_obj = ''
                for c in root: 
                    obj_id = ''
                    if c.tag.split('}')[-1].strip() in ['Project','BaselineProject']:
                        obj_id = [gc.text for gc in c if gc.tag.split('}')[-1].strip() == 'ObjectId'][0]
                        if obj_id == projId:
                            proj_obj = c  # store our project object
 
                # Get the WBS or Activity objects
                nodes = [c for c in proj_obj if subjectArea == c.tag.split('}')[-1].strip()]

                # Get all fields and values for each node
                for c in nodes:
                    row = {}
                    for gc in c:
                        field_name = gc.tag.split('}')[-1].strip()  # Get field name
                        if field_name in fldsDataTypes:  # Only use fields listed in the data types dictionary
                            d_type = fldsDataTypes[field_name]  # Get data type for field
                            field_value = gc.text  # Get value from XML
                            field_value = self.castType(field_value, d_type) # cast field to proper datatype
                            row[field_name] = field_value  # Add value to row dictionary
                    resp.append(row)
                        
        # else:
        #     # Get standard data using EPPM

        #     # all fields are retrived from the client call. However , only those fields that are specifically requested 
        #     # have values retrieved. All Other fields have a value of 'None'        
        #     url = ""
        #     if subjectArea == "Project":
        #         url = hostname + "/services/ProjectService?wsdl"
        #     elif subjectArea == "WBS":
        #         url = hostname + "/services/WBSService?wsdl"
        #     elif subjectArea == "Activity":
        #         url = hostname + "/services/ActivityService?wsdl"
        #     elif subjectArea == "Activity Step":
        #         url = hostname + "/services/ActivityStepService?wsdl"
        #     client = Client(url, wsse=UsernameToken(username, password))
                    
        #     if subjectArea  == "Project":
        #         resp = client.service.ReadProjects(flds, Filter=filter)
        #     elif subjectArea == "WBS":
        #         resp = client.service.ReadWBS(flds, Filter=filter)            
        #     elif subjectArea == "Activity":
        #         resp = client.service.ReadActivities(flds,Filter=filter)
        #     elif subjectArea == "Activity Step":
        #         resp = client.service.ReadActivitySteps(flds,Filter=filter)

        #     # Response is a list of dictionaries
        #     # each dictionary represents a row
        #     # each row has all columns 
        #     # reqData = []
        #     #arcpy.AddMessage("***" + str(resp))        
        #     #get dictionary of fldname and datatype
        #     # fldsDataTypes = self.getStandardFieldsDataTypes(subjectArea)

        # Loop through each dictionary in resp list from XML or EPPM
        while "ObjectId" in flds:
            flds.remove("ObjectId")

        # if "ObjectId" in flds:
        #     flds.remove("ObjectId")

        for item in resp:            
            row = []
            # Loop through each desired field in each dictionary
            # This is how we keep only the undesired fields
            for fld in flds:                
                rowItem = {}
                #arcpy.AddMessage(str(item[fld]))
                #row[fld] = item[fld]
                rowItem["Value"] = item[fld] if fld in item else None # Value is the field value
                rowItem["DataType"] = fldsDataTypes[fld] if fld in fldsDataTypes else "Text" # Get field datatype
                rowItem["Name"] = fld  # Key value is the field name                                
                row.append(rowItem)
                
            # explicitly add an entry for ProjectId for Project Subject Area 
            # so that corresponding field can be added to table
            if subjectArea  == "Project":
                rowItem = {}        
                rowItem["DataType"] = "Text"  # ProjectID is always text data                           
                rowItem["Name"] = "ProjectId"  # Column name is ProjectId
                rowItem["Value"] = item["ObjectId"]  # Get project ObjectId                       
                row.append(rowItem)
            else:
                rowItem = {}        
                rowItem["DataType"] = "Text"  # Datatype always text                          
                rowItem["Name"] = "ForeignObjectId" # this will store Objectid for WBS and Activity so that corresponding field can be added to table
                rowItem["Value"] = item["ObjectId"]  # Get ObjectId for join.                       
                row.append(rowItem)
            
            reqData.append(row)
                    
            #arcpy.AddMessage(reqData)     
       
        return reqData


    def readProjects(self, username:str, password:str, hostname:str, input_type:str, xml_file_path:str) -> list:
        """Get a list of projects.
        Append Project ObjectID
        Returns a list of two lists. 
        The first list is project names as strings.
        The second list is a list of project id values as strings."""

        projList = []
        projs = {}
        baselineProjs = {}
        baselineOIDs = {}
        # Get list of project names
        if input_type == 'XML':

            # Get Master Projects
            tree = ET.parse(xml_file_path)
            root = tree.getroot()
            for c in root: 
                if 'Project' == c.tag.split("}")[-1].strip():
                    proj_Name = [x for x in c if 'Name' == x.tag.split("}")[-1]][0].text
                    proj_ObjectId = [x for x in c if 'ObjectId' == x.tag.split("}")[-1]][0].text

                    projs[str(proj_ObjectId)] = proj_Name + "(" + str(proj_ObjectId) + ")"

            # Get Baseline Projects
            for c in root: 
                if 'BaselineProject' == c.tag.split("}")[-1].strip():
                    proj_Name = [x for x in c if 'Name' == x.tag.split("}")[-1].strip()][0].text
                    proj_ObjectId = [x for x in c if 'ObjectId' == x.tag.split("}")[-1].strip()][0].text
                    proj_OriginalProjectObjectId = [x for x in c if 'OriginalProjectObjectId' == x.tag.split("}")[-1].strip()][0].text

                    # store baseline proj name with OID
                    baselineProjs[str(proj_ObjectId)] = proj_Name+ "(" + str(proj_ObjectId) + ")"
                    # store baseline proj ID and master Proj ID
                    baselineOIDs[str(proj_ObjectId)] = str(proj_OriginalProjectObjectId)
        # else:
        #     url = hostname + "/services/ProjectService?wsdl"
        #     client = Client(url, wsse=UsernameToken(username, password))
            
        #     # return a list of projects with baseline projects indented under master project
            
        #     # Master projects
        #     resp = client.service.ReadProjects("Name")        
        #     projs = {}
        #     for item in resp:            
        #         projs[str(item["ObjectId"])] = item["Name"] + "(" + str(item["ObjectId"]) + ")"
            
        #     #arcpy.AddMessage(projs.keys())
            
        #     # baseline projects 
        #     url = hostname + "/services/BaselineProjectService?wsdl"
        #     client = Client(url, wsse=UsernameToken(username, password))
            
        #     baselnResp = client.service.ReadBaselineProjects(Field=["Name", "OriginalProjectObjectId", "ObjectId"])    
        #     baselineProjs = {}
        #     baselineOIDs = {}
        #     for item in baselnResp:            
        #         #baselineProjs[str(item["OriginalProjectObjectId"])] = item["Name"]+ "(" + str(item["ObjectId"]) + ")"
        #         # store baseline proj name with OID
        #         baselineProjs[str(item["ObjectId"])] = item["Name"]+ "(" + str(item["ObjectId"]) + ")"
        #         # store baseline proj ID and master Proj ID
        #         baselineOIDs[str(item["ObjectId"])] = str(item["OriginalProjectObjectId"])
                
        #     #arcpy.AddMessage(baselineOIDs)

        projoids = []
        for masterProjOID in projs:
            # append master proj to list
            projoids.append(masterProjOID)
            projList.append(projs[masterProjOID]) 
            
            # does master proj ID exist in baselineOIDs dictionary?
            #lstBaselineProj = [baselnOID for baselnOID in list(baselineOIDs) if list(baselnOID)[1] == str(masterProjOID)]  
            for k,v in baselineOIDs.items():
                if v == masterProjOID:
                    projoids.append(k)
                    projList.append("     -" + baselineProjs[k])           
                    

        #arcpy.AddMessage(str(projId))
        return [projList, projoids]
    

    def getUDFFields(self, username:str, password:str, hostname:str, filterType:str, input_type:str, xml_file_path:str) -> list:
        """Get UDF fields.
        Returns a list of strings representing UDF field titles.
        """

        udfFlds = []
        # Read UDF Field names from XML
        if input_type == 'XML':
            # read XML
            # get root
            tree = ET.parse(xml_file_path)
            root = tree.getroot()
            for c in root: 
                if 'UDFType' == c.tag.split("}")[-1].strip():
                    subject_area = [x for x in c if 'SubjectArea' == x.tag.split("}")[-1].strip()][0].text
                    if subject_area == filterType:
                        title = [x for x in c if 'Title' == x.tag.split("}")[-1].strip()][0].text
                        udfFlds.append(title)

        # else: # read from EPPM Server

        #     url = hostname + "/services/UDFTypeService?wsdl"
        #     client = Client(url, wsse=UsernameToken(username, password))
            
        #     filter = "SubjectArea='" + filterType + "'"       
            
        #     resp = client.service.ReadUDFTypes(Field=["Title", "DataType"], Filter=filter)  
            
        #     # all metadata fields for UDF are retrieved even though only 'Title' is specified
        #     for item in resp:
        #         udfFlds.append(item["Title"])
        #         # arcpy.AddMessage(item)
        return udfFlds


    def getStandardFields(self, filterType:str) -> list:
        """Get standard fields.
        Returns a list of standard field titles."""
        # hardcoding fields for now as there is no API method to retrieve fieldnames 
        # and need to get XML for WSDL to parse it for fieldnames
        
        if filterType == "Project":
            return ["ActivityDefaultActivityType",
                    "ActivityDefaultCalendarName",
                    "ActivityDefaultCalendarObjectId",
                    "ActivityDefaultCostAccountObjectId",
                    "ActivityDefaultDurationType",
                    "ActivityDefaultPercentCompleteType",
                    "ActivityDefaultPricePerUnit",
                    "ActivityDefaultReviewRequired",
                    "ActivityIdBasedOnSelectedActivity",
                    "ActivityIdIncrement",
                    "ActivityIdPrefix",
                    "ActivityIdSuffix",
                    "ActivityPercentCompleteBasedOnActivitySteps",
                    "AddActualToRemaining",
                    "AddedBy",
                    "AllowNegativeActualUnitsFlag",
                    "AllowStatusReview",
                    "AnnualDiscountRate",
                    "AnticipatedFinishDate",
                    "AnticipatedStartDate",
                    "AssignmentDefaultDrivingFlag",
                    "AssignmentDefaultRateType",
                    "CalculateFloatBasedOnFinishDate",
                    "CheckOutDate",
                    "CheckOutStatus",
                    "CheckOutUserObjectId",
                    "ComputeTotalFloatType",
                    "ContainsSummaryData",
                    "ContractManagementGroupName",
                    "ContractManagementProjectName",
                    "CostQuantityRecalculateFlag",
                    "CreateDate",
                    "CreateUser",
                    "CriticalActivityFloatLimit",
                    "CriticalActivityFloatThreshold",
                    "CriticalActivityPathType",
                    "CriticalFloatThreshold",
                    "CurrentBaselineProjectObjectId",
                    "CurrentBudget",
                    "CurrentVariance",
                    "DataDate",
                    "DateAdded",
                    "DefaultPriceTimeUnits",
                    "Description",
                    "DiscountApplicationPeriod",
                    "DistributedCurrentBudget",
                    "EarnedValueComputeType",
                    "EarnedValueETCComputeType",
                    "EarnedValueETCUserValue",
                    "EarnedValueUserPercent",
                    "EnablePrimeSycFlag",
                    "EnablePublication",
                    "EnableSummarization",
                    "EtlInterval",
                    "FinishDate",
                    "FiscalYearStartMonth",
                    "ForecastFinishDate",
                    "ForecastStartDate",
                    "GUID",
                    "HasFutureBucketData",
                    "HistoryInterval",
                    "HistoryLevel",
                    "Id",
                    "IgnoreOtherProjectRelationships",
                    "IndependentETCLaborUnits",
                    "IndependentETCTotalCost",
                    "IntegratedType",
                    "IsTemplate",
                    "LastApplyActualsDate",
                    "LastFinancialPeriodObjectId",
                    "LastLevelDate",
                    "LastPublishedOn",
                    "LastScheduleDate",
                    "LastSummarizedDate",
                    "LastUpdateDate",
                    "LastUpdateUser",
                    "LevelAllResources",
                    "LevelDateFlag",
                    "LevelFloatThresholdCount",
                    "LevelOuterAssign",
                    "LevelOuterAssignPriority",
                    "LevelOverAllocationPercent",
                    "LevelPriorityList",
                    "LevelResourceList",
                    "LevelWithinFloat",
                    "LevelingPriority",
                    "LimitMultipleFloatPaths",
                    "LinkActualToActualThisPeriod",
                    "LinkPercentCompleteWithActual",
                    "LinkPlannedAndAtCompletionFlag",
                    "LocationName",
                    "LocationObjectId",
                    "MakeOpenEndedActivitiesCritical",
                    "MaximumMultipleFloatPaths",
                    "MultipleFloatPathsEnabled",
                    "MultipleFloatPathsEndingActivityObjectId",
                    "MultipleFloatPathsUseTotalFloat",
                    "MustFinishByDate",
                    "Name",
                    "NetPresentValue",
                    "OBSName",
                    "OBSObjectId",
                    "ObjectId",
                    "OriginalBudget",
                    "OutOfSequenceScheduleType",
                    "OverallProjectScore",
                    "OwnerResourceObjectId",
                    "ParentEPSObjectId",
                    "PaybackPeriod",
                    "PerformancePercentCompleteByLaborUnits",
                    "PlannedStartDate",
                    "PostResponsePessimisticFinish",
                    "PostResponsePessimisticStart",
                    "PreResponsePessimisticFinish",
                    "PreResponsePessimisticStart",
                    "PrimaryResourcesCanMarkActivitiesAsCompleted",
                    "PrimaryResourcesCanUpdateActivityDates",
                    "ProjectForecastStartDate",
                    "ProjectScheduleType",
                    "PropertyType",
                    "ProposedBudget",
                    "PublicationPriority",
                    "PublishLevel",
                    "RelationshipLagCalendar",
                    "ResetPlannedToRemainingFlag",
                    "ResourceCanBeAssignedToSameActivityMoreThanOnce",
                    "ResourcesCanAssignThemselvesToActivities",
                    "ResourcesCanAssignThemselvesToActivitiesOutsideOBSAccess",
                    "ResourcesCanEditAssignmentPercentComplete",
                    "ResourcesCanMarkAssignmentAsCompleted",
                    "ResourcesCanViewInactiveActivities",
                    "ReturnOnInvestment",
                    "RiskExposure",
                    "RiskLevel",
                    "RiskMatrixName",
                    "RiskMatrixObjectId",
                    "RiskScore",
                    "ScheduleWBSHierarchyType",
                    "ScheduledFinishDate",
                    "SourceProjectObjectId",
                    "StartDate",
                    "StartToStartLagCalculationType",
                    "Status",
                    "StatusReviewerName",
                    "StatusReviewerObjectId",
                    "StrategicPriority",
                    "SummarizeResourcesRolesByWBS",
                    "SummarizeToWBSLevel",
                    "SummarizedDataDate",
                    "SummaryAccountingVarianceByCost",
                    "SummaryAccountingVarianceByLaborUnits",
                    "SummaryActivityCount",
                    "SummaryActualDuration",
                    "SummaryActualExpenseCost",
                    "SummaryActualFinishDate",
                    "SummaryActualLaborCost",
                    "SummaryActualLaborUnits",
                    "SummaryActualMaterialCost",
                    "SummaryActualNonLaborCost",
                    "SummaryActualNonLaborUnits",
                    "SummaryActualStartDate",
                    "SummaryActualThisPeriodCost",
                    "SummaryActualThisPeriodLaborCost",
                    "SummaryActualThisPeriodLaborUnits",
                    "SummaryActualThisPeriodMaterialCost",
                    "SummaryActualThisPeriodNonLaborCost",
                    "SummaryActualThisPeriodNonLaborUnits",
                    "SummaryActualTotalCost",
                    "SummaryActualValueByCost",
                    "SummaryActualValueByLaborUnits",
                    "SummaryAtCompletionDuration",
                    "SummaryAtCompletionExpenseCost",
                    "SummaryAtCompletionLaborCost",
                    "SummaryAtCompletionLaborUnits",
                    "SummaryAtCompletionMaterialCost",
                    "SummaryAtCompletionNonLaborCost",
                    "SummaryAtCompletionNonLaborUnits",
                    "SummaryAtCompletionTotalCost",
                    "SummaryAtCompletionTotalCostVariance",
                    "SummaryBaselineCompletedActivityCount",
                    "SummaryBaselineDuration",
                    "SummaryBaselineExpenseCost",
                    "SummaryBaselineFinishDate",
                    "SummaryBaselineInProgressActivityCount",
                    "SummaryBaselineLaborCost",
                    "SummaryBaselineLaborUnits",
                    "SummaryBaselineMaterialCost",
                    "SummaryBaselineNonLaborCost",
                    "SummaryBaselineNonLaborUnits",
                    "SummaryBaselineNotStartedActivityCount",
                    "SummaryBaselineStartDate",
                    "SummaryBaselineTotalCost",
                    "SummaryBudgetAtCompletionByCost",
                    "SummaryBudgetAtCompletionByLaborUnits",
                    "SummaryCompletedActivityCount",
                    "SummaryCostPercentComplete",
                    "SummaryCostPercentOfPlanned",
                    "SummaryCostPerformanceIndexByCost",
                    "SummaryCostPerformanceIndexByLaborUnits",
                    "SummaryCostVarianceByCost",
                    "SummaryCostVarianceByLaborUnits",
                    "SummaryCostVarianceIndex",
                    "SummaryCostVarianceIndexByCost",
                    "SummaryCostVarianceIndexByLaborUnits",
                    "SummaryDurationPercentComplete",
                    "SummaryDurationPercentOfPlanned",
                    "SummaryDurationVariance",
                    "SummaryEarnedValueByCost",
                    "SummaryEarnedValueByLaborUnits",
                    "SummaryEstimateAtCompletionByCost",
                    "SummaryEstimateAtCompletionByLaborUnits",
                    "SummaryEstimateAtCompletionHighPercentByLaborUnits",
                    "SummaryEstimateAtCompletionLowPercentByLaborUnits",
                    "SummaryEstimateToCompleteByCost",
                    "SummaryEstimateToCompleteByLaborUnits",
                    "SummaryExpenseCostPercentComplete",
                    "SummaryExpenseCostVariance",
                    "SummaryFinishDateVariance",
                    "SummaryInProgressActivityCount",
                    "SummaryLaborCostPercentComplete",
                    "SummaryLaborCostVariance",
                    "SummaryLaborUnitsPercentComplete",
                    "SummaryLaborUnitsVariance",
                    "SummaryLevel",
                    "SummaryMaterialCostPercentComplete",
                    "SummaryMaterialCostVariance",
                    "SummaryNonLaborCostPercentComplete",
                    "SummaryNonLaborCostVariance",
                    "SummaryNonLaborUnitsPercentComplete",
                    "SummaryNonLaborUnitsVariance",
                    "SummaryNotStartedActivityCount",
                    "SummaryPerformancePercentCompleteByCost",
                    "SummaryPerformancePercentCompleteByLaborUnits",
                    "SummaryPlannedCost",
                    "SummaryPlannedDuration",
                    "SummaryPlannedExpenseCost",
                    "SummaryPlannedFinishDate",
                    "SummaryPlannedLaborCost",
                    "SummaryPlannedLaborUnits",
                    "SummaryPlannedMaterialCost",
                    "SummaryPlannedNonLaborCost",
                    "SummaryPlannedNonLaborUnits",
                    "SummaryPlannedStartDate",
                    "SummaryPlannedValueByCost",
                    "SummaryPlannedValueByLaborUnits",
                    "SummaryProgressFinishDate",
                    "SummaryRemainingDuration",
                    "SummaryRemainingExpenseCost",
                    "SummaryRemainingFinishDate",
                    "SummaryRemainingLaborCost",
                    "SummaryRemainingLaborUnits",
                    "SummaryRemainingMaterialCost",
                    "SummaryRemainingNonLaborCost",
                    "SummaryRemainingNonLaborUnits",
                    "SummaryRemainingStartDate",
                    "SummaryRemainingTotalCost",
                    "SummarySchedulePercentComplete",
                    "SummarySchedulePercentCompleteByLaborUnits",
                    "SummarySchedulePerformanceIndexByCost",
                    "SummarySchedulePerformanceIndexByLaborUnits",
                    "SummaryScheduleVarianceByCost",
                    "SummaryScheduleVarianceByLaborUnits",
                    "SummaryScheduleVarianceIndex",
                    "SummaryScheduleVarianceIndexByCost",
                    "SummaryScheduleVarianceIndexByLaborUnits",
                    "SummaryStartDateVariance",
                    "SummaryToCompletePerformanceIndexByCost",
                    "SummaryTotalCostVariance",
                    "SummaryTotalFloat",
                    "SummaryUnitsPercentComplete",
                    "SummaryVarianceAtCompletionByLaborUnits",
                    "SyncWbsHierarchyFlag",
                    "TeamMemberActivityFields",
                    "TeamMemberAddNewActualUnits",
                    "TeamMemberAssignmentOption",
                    "TeamMemberCanStatusOtherResources",
                    "TeamMemberCanUpdateNotebooks",
                    "TeamMemberDisplayPlannedUnits",
                    "TeamMemberDisplayTotalFloatFlag",
                    "TeamMemberIncludePrimaryResources",
                    "TeamMemberResourceAssignmentFields",
                    "TeamMemberStepUDFViewableFields",
                    "TeamMemberStepsAddDeletable",
                    "TeamMemberViewableFields",
                    "TotalBenefitPlan",
                    "TotalBenefitPlanTally",
                    "TotalFunding",
                    "TotalSpendingPlan",
                    "TotalSpendingPlanTally",
                    "UnallocatedBudget",
                    "UndistributedCurrentVariance",
                    "UnifierCBSTasksOnlyFlag",
                    "UnifierDataMappingName",
                    "UnifierDeleteActivitiesFlag",
                    "UnifierEnabledFlag",
                    "UnifierProjectName",
                    "UnifierProjectNumber",
                    "UnifierScheduleSheetName",
                    "UseExpectedFinishDates",
                    "UseProjectBaselineForEarnedValue",
                    "WBSCodeSeparator",
                    "WBSHierarchyLevels",
                    "WBSMilestonePercentComplete",
                    "WBSObjectId",
                    "WebSiteRootDirectory",
                    "WebSiteURL"]
        
        elif filterType == "WBS":
            return ["AnticipatedFinishDate",
                    "AnticipatedStartDate",
                    "Code",
                    "ContainsSummaryData",
                    "CreateDate",
                    "CreateUser",
                    "CurrentBudget",
                    "CurrentVariance",
                    "DistributedCurrentBudget",
                    "EarnedValueComputeType",
                    "EarnedValueETCComputeType",
                    "EarnedValueETCUserValue",
                    "EarnedValueUserPercent",
                    "EstimatedWeight",
                    "FinishDate",
                    "ForecastFinishDate",
                    "ForecastStartDate",
                    "GUID",
                    "IndependentETCLaborUnits",
                    "IndependentETCTotalCost",
                    "IntegratedType",
                    "IntegratedWBS",
                    "IsBaseline",
                    "IsTemplate",
                    "IsWorkPackage",
                    "LastUpdateDate",
                    "LastUpdateUser",
                    "Name",
                    "OBSName",
                    "OBSObjectId",
                    "ObjectId",
                    "OriginalBudget",
                    "ParentObjectId",
                    "ProjectId",
                    "ProjectObjectId",
                    "ProposedBudget",
                    "RolledUpFinishDate",
                    "RolledUpStartDate",
                    "SequenceNumber",
                    "StartDate",
                    "Status",
                    "StatusReviewerName",
                    "StatusReviewerObjectId",
                    "SummaryAccountingVarianceByCost",
                    "SummaryAccountingVarianceByLaborUnits",
                    "SummaryActivityCount",
                    "SummaryActualDuration",
                    "SummaryActualExpenseCost",
                    "SummaryActualFinishDate",
                    "SummaryActualLaborCost",
                    "SummaryActualLaborUnits",
                    "SummaryActualMaterialCost",
                    "SummaryActualNonLaborCost",
                    "SummaryActualNonLaborUnits",
                    "SummaryActualStartDate",
                    "SummaryActualThisPeriodCost",
                    "SummaryActualThisPeriodLaborCost",
                    "SummaryActualThisPeriodLaborUnits",
                    "SummaryActualThisPeriodMaterialCost",
                    "SummaryActualThisPeriodNonLaborCost",
                    "SummaryActualThisPeriodNonLaborUnits",
                    "SummaryActualTotalCost",
                    "SummaryActualValueByCost",
                    "SummaryActualValueByLaborUnits",
                    "SummaryAtCompletionDuration",
                    "SummaryAtCompletionExpenseCost",
                    "SummaryAtCompletionLaborCost",
                    "SummaryAtCompletionLaborUnits",
                    "SummaryAtCompletionMaterialCost",
                    "SummaryAtCompletionNonLaborCost",
                    "SummaryAtCompletionNonLaborUnits",
                    "SummaryAtCompletionTotalCost",
                    "SummaryAtCompletionTotalCostVariance",
                    "SummaryBaselineCompletedActivityCount",
                    "SummaryBaselineDuration",
                    "SummaryBaselineExpenseCost",
                    "SummaryBaselineFinishDate",
                    "SummaryBaselineInProgressActivityCount",
                    "SummaryBaselineLaborCost",
                    "SummaryBaselineLaborUnits",
                    "SummaryBaselineMaterialCost",
                    "SummaryBaselineNonLaborCost",
                    "SummaryBaselineNonLaborUnits",
                    "SummaryBaselineNotStartedActivityCount",
                    "SummaryBaselineStartDate",
                    "SummaryBaselineTotalCost",
                    "SummaryBudgetAtCompletionByCost",
                    "SummaryBudgetAtCompletionByLaborUnits",
                    "SummaryCompletedActivityCount",
                    "SummaryCostPercentComplete",
                    "SummaryCostPercentOfPlanned",
                    "SummaryCostPerformanceIndexByCost",
                    "SummaryCostPerformanceIndexByLaborUnits",
                    "SummaryCostVarianceByCost",
                    "SummaryCostVarianceByLaborUnits",
                    "SummaryCostVarianceIndex",
                    "SummaryCostVarianceIndexByCost",
                    "SummaryCostVarianceIndexByLaborUnits",
                    "SummaryDurationPercentComplete",
                    "SummaryDurationPercentOfPlanned",
                    "SummaryDurationVariance",
                    "SummaryEarnedValueByCost",
                    "SummaryEarnedValueByLaborUnits",
                    "SummaryEstimateAtCompletionByCost",
                    "SummaryEstimateAtCompletionByLaborUnits",
                    "SummaryEstimateAtCompletionHighPercentByLaborUnits",
                    "SummaryEstimateAtCompletionLowPercentByLaborUnits",
                    "SummaryEstimateToCompleteByCost",
                    "SummaryEstimateToCompleteByLaborUnits",
                    "SummaryExpenseCostPercentComplete",
                    "SummaryExpenseCostVariance",
                    "SummaryFinishDateVariance",
                    "SummaryInProgressActivityCount",
                    "SummaryLaborCostPercentComplete",
                    "SummaryLaborCostVariance",
                    "SummaryLaborUnitsPercentComplete",
                    "SummaryLaborUnitsVariance",
                    "SummaryMaterialCostPercentComplete",
                    "SummaryMaterialCostVariance",
                    "SummaryNonLaborCostPercentComplete",
                    "SummaryNonLaborCostVariance",
                    "SummaryNonLaborUnitsPercentComplete",
                    "SummaryNonLaborUnitsVariance",
                    "SummaryNotStartedActivityCount",
                    "SummaryPerformancePercentCompleteByCost",
                    "SummaryPerformancePercentCompleteByLaborUnits",
                    "SummaryPlannedCost",
                    "SummaryPlannedDuration",
                    "SummaryPlannedExpenseCost",
                    "SummaryPlannedFinishDate",
                    "SummaryPlannedLaborCost",
                    "SummaryPlannedLaborUnits",
                    "SummaryPlannedMaterialCost",
                    "SummaryPlannedNonLaborCost",
                    "SummaryPlannedNonLaborUnits",
                    "SummaryPlannedStartDate",
                    "SummaryPlannedValueByCost",
                    "SummaryPlannedValueByLaborUnits",
                    "SummaryProgressFinishDate",
                    "SummaryRemainingDuration",
                    "SummaryRemainingExpenseCost",
                    "SummaryRemainingFinishDate",
                    "SummaryRemainingLaborCost",
                    "SummaryRemainingLaborUnits",
                    "SummaryRemainingMaterialCost",
                    "SummaryRemainingNonLaborCost",
                    "SummaryRemainingNonLaborUnits",
                    "SummaryRemainingStartDate",
                    "SummaryRemainingTotalCost",
                    "SummarySchedulePercentComplete",
                    "SummarySchedulePercentCompleteByLaborUnits",
                    "SummarySchedulePerformanceIndexByCost",
                    "SummarySchedulePerformanceIndexByLaborUnits",
                    "SummaryScheduleVarianceByCost",
                    "SummaryScheduleVarianceByLaborUnits",
                    "SummaryScheduleVarianceIndex",
                    "SummaryScheduleVarianceIndexByCost",
                    "SummaryScheduleVarianceIndexByLaborUnits",
                    "SummaryStartDateVariance",
                    "SummaryToCompletePerformanceIndexByCost",
                    "SummaryTotalCostVariance",
                    "SummaryTotalFloat",
                    "SummaryUnitsPercentComplete",
                    "SummaryVarianceAtCompletionByLaborUnits",
                    "TotalBenefitPlan",
                    "TotalBenefitPlanTally",
                    "TotalSpendingPlan",
                    "TotalSpendingPlanTally",
                    "UnallocatedBudget",
                    "UndistributedCurrentVariance",
                    "WBSCategoryObjectId",
                    "WBSMilestonePercentComplete"]
        
        elif filterType == "Activity":
            return ["AccountingVariance",
                    "AccountingVarianceLaborUnits",
                    "ActivityOwnerUserId",
                    "ActualDuration",
                    "ActualExpenseCost",
                    "ActualFinishDate",
                    "ActualLaborCost",
                    "ActualLaborUnits",
                    "ActualMaterialCost",
                    "ActualNonLaborCost",
                    "ActualNonLaborUnits",
                    "ActualStartDate",
                    "ActualThisPeriodLaborCost",
                    "ActualThisPeriodLaborUnits",
                    "ActualThisPeriodMaterialCost",
                    "ActualThisPeriodNonLaborCost",
                    "ActualThisPeriodNonLaborUnits",
                    "ActualTotalCost",
                    "ActualTotalUnits",
                    "AtCompletionDuration",
                    "AtCompletionExpenseCost",
                    "AtCompletionLaborCost",
                    "AtCompletionLaborUnits",
                    "AtCompletionLaborUnitsVariance",
                    "AtCompletionMaterialCost",
                    "AtCompletionNonLaborCost",
                    "AtCompletionNonLaborUnits",
                    "AtCompletionTotalCost",
                    "AtCompletionTotalUnits",
                    "AtCompletionVariance",
                    "AutoComputeActuals",
                    "Baseline1Duration",
                    "Baseline1FinishDate",
                    "Baseline1PlannedDuration",
                    "Baseline1PlannedExpenseCost",
                    "Baseline1PlannedLaborCost",
                    "Baseline1PlannedLaborUnits",
                    "Baseline1PlannedMaterialCost",
                    "Baseline1PlannedNonLaborCost",
                    "Baseline1PlannedNonLaborUnits",
                    "Baseline1PlannedTotalCost",
                    "Baseline1StartDate",
                    "BaselineDuration",
                    "BaselineFinishDate",
                    "BaselinePlannedDuration",
                    "BaselinePlannedExpenseCost",
                    "BaselinePlannedLaborCost",
                    "BaselinePlannedLaborUnits",
                    "BaselinePlannedMaterialCost",
                    "BaselinePlannedNonLaborCost",
                    "BaselinePlannedNonLaborUnits",
                    "BaselinePlannedTotalCost",
                    "BaselineStartDate",
                    "BudgetAtCompletion",
                    "CBSCode",
                    "CBSId",
                    "CBSObjectId",
                    "CalendarName",
                    "CalendarObjectId",
                    "CostPercentComplete",
                    "CostPercentOfPlanned",
                    "CostPerformanceIndex",
                    "CostPerformanceIndexLaborUnits",
                    "CostVariance",
                    "CostVarianceIndex",
                    "CostVarianceIndexLaborUnits",
                    "CostVarianceLaborUnits",
                    "CreateDate",
                    "CreateUser",
                    "DataDate",
                    "Duration1Variance",
                    "DurationPercentComplete",
                    "DurationPercentOfPlanned",
                    "DurationType",
                    "DurationVariance",
                    "EarlyFinishDate",
                    "EarlyStartDate",
                    "EarnedValueCost",
                    "EarnedValueLaborUnits",
                    "EstimateAtCompletionCost",
                    "EstimateAtCompletionLaborUnits",
                    "EstimateToComplete",
                    "EstimateToCompleteLaborUnits",
                    "EstimatedWeight",
                    "ExpectedFinishDate",
                    "ExpenseCost1Variance",
                    "ExpenseCostPercentComplete",
                    "ExpenseCostVariance",
                    "ExternalEarlyStartDate",
                    "ExternalLateFinishDate",
                    "Feedback",
                    "FinishDate",
                    "FinishDate1Variance",
                    "FinishDateVariance",
                    "FloatPath",
                    "FloatPathOrder",
                    "FreeFloat",
                    "GUID",
                    "HasFutureBucketData",
                    "Id",
                    "IsBaseline",
                    "IsCritical",
                    "IsLongestPath",
                    "IsNewFeedback",
                    "IsStarred",
                    "IsTemplate",
                    "IsWorkPackage",
                    "LaborCost1Variance",
                    "LaborCostPercentComplete",
                    "LaborCostVariance",
                    "LaborUnits1Variance",
                    "LaborUnitsPercentComplete",
                    "LaborUnitsVariance",
                    "LastUpdateDate",
                    "LastUpdateUser",
                    "LateFinishDate",
                    "LateStartDate",
                    "LevelingPriority",
                    "LocationName",
                    "LocationObjectId",
                    "MaterialCost1Variance",
                    "MaterialCostPercentComplete",
                    "MaterialCostVariance",
                    "MaximumDuration",
                    "MinimumDuration",
                    "MostLikelyDuration",
                    "Name",
                    "NonLaborCost1Variance",
                    "NonLaborCostPercentComplete",
                    "NonLaborCostVariance",
                    "NonLaborUnits1Variance",
                    "NonLaborUnitsPercentComplete",
                    "NonLaborUnitsVariance",
                    "NotesToResources",
                    "ObjectId",
                    "OwnerIDArray",
                    "OwnerNamesArray",
                    "PercentComplete",
                    "PercentCompleteType",
                    "PerformancePercentComplete",
                    "PerformancePercentCompleteByLaborUnits",
                    "PhysicalPercentComplete",
                    "PlannedDuration",
                    "PlannedExpenseCost",
                    "PlannedFinishDate",
                    "PlannedLaborCost",
                    "PlannedLaborUnits",
                    "PlannedMaterialCost",
                    "PlannedNonLaborCost",
                    "PlannedNonLaborUnits",
                    "PlannedStartDate",
                    "PlannedTotalCost",
                    "PlannedTotalUnits",
                    "PlannedValueCost",
                    "PlannedValueLaborUnits",
                    "PostRespCriticalityIndex",
                    "PostResponsePessimisticFinish",
                    "PostResponsePessimisticStart",
                    "PreRespCriticalityIndex",
                    "PreResponsePessimisticFinish",
                    "PreResponsePessimisticStart",
                    "PrimaryConstraintDate",
                    "PrimaryConstraintType",
                    "PrimaryResourceId",
                    "PrimaryResourceName",
                    "PrimaryResourceObjectId",
                    "ProjectFlag",
                    "ProjectId",
                    "ProjectName",
                    "ProjectObjectId",
                    "ProjectProjectFlag",
                    "RemainingDuration",
                    "RemainingEarlyFinishDate",
                    "RemainingEarlyStartDate",
                    "RemainingExpenseCost",
                    "RemainingFloat",
                    "RemainingLaborCost",
                    "RemainingLaborUnits",
                    "RemainingLateFinishDate",
                    "RemainingLateStartDate",
                    "RemainingMaterialCost",
                    "RemainingNonLaborCost",
                    "RemainingNonLaborUnits",
                    "RemainingTotalCost",
                    "RemainingTotalUnits",
                    "ResumeDate",
                    "ReviewFinishDate",
                    "ReviewRequired",
                    "ReviewStatus",
                    "SchedulePercentComplete",
                    "SchedulePerformanceIndex",
                    "SchedulePerformanceIndexLaborUnits",
                    "ScheduleVariance",
                    "ScheduleVarianceIndex",
                    "ScheduleVarianceIndexLaborUnits",
                    "ScheduleVarianceLaborUnits",
                    "ScopePercentComplete",
                    "SecondaryConstraintDate",
                    "SecondaryConstraintType",
                    "StartDate",
                    "StartDate1Variance",
                    "StartDateVariance",
                    "Status",
                    "StatusCode",
                    "SuspendDate",
                    "TaskStatusCompletion",
                    "TaskStatusDates",
                    "TaskStatusIndicator",
                    "ToCompletePerformanceIndex",
                    "TotalCost1Variance",
                    "TotalCostVariance",
                    "TotalFloat",
                    "Type",
                    "UnitsPercentComplete",
                    "UnreadCommentCount",
                    "WBSCode",
                    "WBSName",
                    "WBSNamePath",
                    "WBSObjectId",
                    "WBSPath",
                    "WorkPackageId",
                    "WorkPackageName"]   

        elif filterType == "Activity Step":
            return ["ActivityId",
                    "ActivityName",
                    "ActivityObjectId",
                    "CreateDate",
                    "CreateUser",
                    "Description",
                    "IsBaseline",
                    "IsCompleted",
                    "IsTemplate",
                    "LastUpdateDate",
                    "LastUpdateUser",
                    "Name",
                    "ObjectId",
                    "PercentComplete",
                    "ProjectId",
                    "ProjectObjectId",
                    "SequenceNumber",
                    "WBSObjectId",
                    "Weight",
                    "WeightPercent"]
         

    def getStandardFieldsDataTypes(self, filterType:str) -> dict:
        """Get standard field data types.
        Takes Project, WBS, or Activity as the filterType Input.
        Returns a dictionary where the keys are the field title and the values are the data types."""
        # hardcoding fields for now as there is no API method to retrieve fieldnames 
        # and need to get XML for WSDL to parse it for fieldnames
        
        # added data types for fields
        if filterType == "Project":
            return {"ActivityDefaultActivityType":"Text",
                "ActivityDefaultCalendarName":"Text",
                "ActivityDefaultCalendarObjectId":"Integer",
                "ActivityDefaultCostAccountObjectId":"Integer",
                "ActivityDefaultDurationType":"Text",
                "ActivityDefaultPercentCompleteType":"Text",
                "ActivityDefaultPricePerUnit":"Double",
                "ActivityDefaultReviewRequired":"Text",
                "ActivityIdBasedOnSelectedActivity":"Text",
                "ActivityIdIncrement":"Integer",
                "ActivityIdPrefix":"Text",
                "ActivityIdSuffix":"Integer",
                "ActivityPercentCompleteBasedOnActivitySteps":"Text",
                "AddActualToRemaining":"Text",
                "AddedBy":"Text",
                "AllowNegativeActualUnitsFlag":"Text",
                "AllowStatusReview":"Text",
                "AnnualDiscountRate":"Double",
                "AnticipatedFinishDate":"Date",
                "AnticipatedStartDate":"Date",
                "AssignmentDefaultDrivingFlag":"Text",
                "AssignmentDefaultRateType":"Text",
                "CalculateFloatBasedOnFinishDate":"Text",
                "CheckOutDate":"Date",
                "CheckOutStatus":"Text",
                "CheckOutUserObjectId":"Integer",
                "ComputeTotalFloatType":"Text",
                "ContainsSummaryData":"Text",
                "CostQuantityRecalculateFlag":"Text",
                "CreateDate":"Date",
                "CreateUser":"Text",
                "CriticalActivityFloatLimit":"Double",
                "CriticalActivityFloatThreshold":"Double",
                "CriticalActivityPathType":"Text",
                "CriticalFloatThreshold":"Double",
                "CurrentBaselineProjectObjectId":"Integer",
                "CurrentBudget":"Double",
                "CurrentVariance":"Double",
                "DataDate":"Date",
                "DateAdded":"Date",
                "DefaultPriceTimeUnits":"Text",
                "Description":"Text",
                "DiscountApplicationPeriod":"Text",
                "DistributedCurrentBudget":"Double",
                "EarnedValueComputeType":"Text",
                "EarnedValueETCComputeType":"Text",
                "EarnedValueETCUserValue":"Double",
                "EarnedValueUserPercent":"Double",
                "EnablePublication":"Text",
                "EnableSummarization":"Text",
                "EtlInterval":"Text",
                "FinishDate":"Date",
                "FiscalYearStartMonth":"Integer",
                "ForecastFinishDate":"Date",
                "ForecastStartDate":"Date",
                "GUID":"Text",
                "HasFutureBucketData":"Text",
                "HistoryInterval":"Text",
                "HistoryLevel":"Text",
                "Id":"Text",
                "IgnoreOtherProjectRelationships":"Text",
                "IndependentETCLaborUnits":"Double",
                "IndependentETCTotalCost":"Double",
                "IntegratedType":"Text",
                "IsTemplate":"Text",
                "LastApplyActualsDate":"Date",
                "LastFinancialPeriodObjectId":"Integer",
                "LastLevelDate":"Date",
                "LastPublishedOn":"Date",
                "LastScheduleDate":"Date",
                "LastSummarizedDate":"Date",
                "LastUpdateDate":"Date",
                "LastUpdateUser":"Text",
                "LevelAllResources":"Text",
                "LevelDateFlag":"Text",
                "LevelFloatThresholdCount":"Integer",
                "LevelOuterAssign":"Text",
                "LevelOuterAssignPriority":"Integer",
                "LevelOverAllocationPercent":"Double",
                "LevelPriorityList":"Text",
                "LevelResourceList":"Text",
                "LevelWithinFloat":"Text",
                "LevelingPriority":"Integer",
                "LimitMultipleFloatPaths":"Text",
                "LinkActualToActualThisPeriod":"Text",
                "LinkPercentCompleteWithActual":"Text",
                "LinkPlannedAndAtCompletionFlag":"Text",
                "LocationName":"Text",
                "LocationObjectId":"Integer",
                "MakeOpenEndedActivitiesCritical":"Text",
                "MaximumMultipleFloatPaths":"Integer",
                "MultipleFloatPathsEnabled":"Text",
                "MultipleFloatPathsEndingActivityObjectId":"Integer",
                "MultipleFloatPathsUseTotalFloat":"Text",
                "MustFinishByDate":"Date",
                "Name":"Text",
                "NetPresentValue":"Double",
                "OBSName":"Text",
                "OBSObjectId":"Integer",
                "ObjectId":"Integer",
                "OriginalBudget":"Double",
                "OutOfSequenceScheduleType":"Text",
                "OverallProjectScore":"Integer",
                "OwnerResourceObjectId":"Integer",
                "ParentEPSObjectId":"Integer",
                "PaybackPeriod":"Integer",
                "PerformancePercentCompleteByLaborUnits":"Double",
                "PlannedStartDate":"Date",
                "PostResponsePessimisticStart":"Date",
                "PreResponsePessimisticFinish":"Date",
                "PreResponsePessimisticStart":"Date",
                "PrimaryResourcesCanMarkActivitiesAsCompleted":"Text",
                "PrimaryResourcesCanUpdateActivityDates":"Text",
                "ProjectForecastStartDate":"Date",
                "ProjectScheduleType":"Text",
                "PropertyType":"Text",
                "ProposedBudget":"Double",
                "PublicationPriority":"Integer",
                "PublishLevel":"Text",
                "RelationshipLagCalendar":"Text",
                "ResetPlannedToRemainingFlag":"Text",
                "ResourceCanBeAssignedToSameActivityMoreThanOnce":"Text",
                "ResourcesCanAssignThemselvesToActivities":"Text",
                "ResourcesCanAssignThemselvesToActivitiesOutsideOBSAccess":"Text",
                "ResourcesCanEditAssignmentPercentComplete":"Text",
                "ResourcesCanMarkAssignmentAsCompleted":"Text",
                "ResourcesCanViewInactiveActivities":"Text",
                "ReturnOnInvestment":"Double",
                "RiskExposure":"Double",
                "RiskLevel":"Text",
                "RiskMatrixName":"Text",
                "RiskMatrixObjectId":"Integer",
                "RiskScore":"Integer",
                "ScheduleWBSHierarchyType":"Text",
                "ScheduledFinishDate":"Date",
                "SourceProjectObjectId":"Integer",
                "StartDate":"Date",
                "StartToStartLagCalculationType":"Text",
                "Status":"Text",
                "StatusReviewerName":"Text",
                "StatusReviewerObjectId":"Integer",
                "StrategicPriority":"Integer",
                "SummarizeResourcesRolesByWBS":"Text",
                "SummarizeToWBSLevel":"Integer",
                "SummarizedDataDate":"Date",
                "SummaryAccountingVarianceByCost":"Double",
                "SummaryAccountingVarianceByLaborUnits":"Double",
                "SummaryActivityCount":"Integer",
                "SummaryActualDuration":"Double",
                "SummaryActualExpenseCost":"Double",
                "SummaryActualFinishDate":"Date",
                "SummaryActualLaborCost":"Double",
                "SummaryActualLaborUnits":"Double",
                "SummaryActualMaterialCost":"Double",
                "SummaryActualNonLaborCost":"Double",
                "SummaryActualNonLaborUnits":"Double",
                "SummaryActualStartDate":"Date",
                "SummaryActualThisPeriodCost":"Double",
                "SummaryActualThisPeriodLaborCost":"Double",
                "SummaryActualThisPeriodLaborUnits":"Double",
                "SummaryActualThisPeriodMaterialCost":"Double",
                "SummaryActualThisPeriodNonLaborCost":"Double",
                "SummaryActualThisPeriodNonLaborUnits":"Double",
                "SummaryActualTotalCost":"Double",
                "SummaryActualValueByCost":"Double",
                "SummaryActualValueByLaborUnits":"Double",
                "SummaryAtCompletionDuration":"Double",
                "SummaryAtCompletionExpenseCost":"Double",
                "SummaryAtCompletionLaborCost":"Double",
                "SummaryAtCompletionLaborUnits":"Double",
                "SummaryAtCompletionMaterialCost":"Double",
                "SummaryAtCompletionNonLaborCost":"Double",
                "SummaryAtCompletionNonLaborUnits":"Double",
                "SummaryAtCompletionTotalCost":"Double",
                "SummaryAtCompletionTotalCostVariance":"Double",
                "SummaryBaselineCompletedActivityCount":"Integer",
                "SummaryBaselineDuration":"Double",
                "SummaryBaselineExpenseCost":"Double",
                "SummaryBaselineFinishDate":"Date",
                "SummaryBaselineInProgressActivityCount":"Integer",
                "SummaryBaselineLaborCost":"Double",
                "SummaryBaselineLaborUnits":"Double",
                "SummaryBaselineMaterialCost":"Double",
                "SummaryBaselineNonLaborCost":"Double",
                "SummaryBaselineNonLaborUnits":"Double",
                "SummaryBaselineNotStartedActivityCount":"Integer",
                "SummaryBaselineStartDate":"Date",
                "SummaryBaselineTotalCost":"Double",
                "SummaryBudgetAtCompletionByCost":"Double",
                "SummaryBudgetAtCompletionByLaborUnits":"Double",
                "SummaryCompletedActivityCount":"Integer",
                "SummaryCostPercentComplete":"Double",
                "SummaryCostPercentOfPlanned":"Double",
                "SummaryCostPerformanceIndexByCost":"Double",
                "SummaryCostPerformanceIndexByLaborUnits":"Double",
                "SummaryCostVarianceByCost":"Double",
                "SummaryCostVarianceByLaborUnits":"Double",
                "SummaryCostVarianceIndex":"Double",
                "SummaryCostVarianceIndexByCost":"Double",
                "SummaryCostVarianceIndexByLaborUnits":"Double",
                "SummaryDurationPercentComplete":"Double",
                "SummaryDurationPercentOfPlanned":"Double",
                "SummaryDurationVariance":"Double",
                "SummaryEarnedValueByCost":"Double",
                "SummaryEarnedValueByLaborUnits":"Double",
                "SummaryEstimateAtCompletionByCost":"Double",
                "SummaryEstimateAtCompletionByLaborUnits":"Double",
                "SummaryEstimateAtCompletionHighPercentByLaborUnits":"Double",
                "SummaryEstimateAtCompletionLowPercentByLaborUnits":"Double",
                "SummaryEstimateToCompleteByCost":"Double",
                "SummaryEstimateToCompleteByLaborUnits":"Double",
                "SummaryExpenseCostPercentComplete":"Double",
                "SummaryExpenseCostVariance":"Double",
                "SummaryFinishDateVariance":"Double",
                "SummaryInProgressActivityCount":"Integer",
                "SummaryLaborCostPercentComplete":"Double",
                "SummaryLaborCostVariance":"Double",
                "SummaryLaborUnitsPercentComplete":"Double",
                "SummaryLaborUnitsVariance":"Double",
                "SummaryLevel":"Text",
                "SummaryNonLaborCostPercentComplete":"Double",
                "SummaryNonLaborUnitsPercentComplete":"Double",
                "SummaryNonLaborUnitsVariance":"Double",
                "SummaryNotStartedActivityCount":"Integer",
                "SummaryPerformancePercentCompleteByCost":"Double",
                "SummaryPerformancePercentCompleteByLaborUnits":"Double",
                "SummaryPlannedCost":"Double",
                "SummaryPlannedDuration":"Double",
                "SummaryPlannedExpenseCost":"Double",
                "SummaryPlannedFinishDate":"Date",
                "SummaryPlannedLaborCost":"Double",
                "SummaryPlannedLaborUnits":"Double",
                "SummaryPlannedMaterialCost":"Double",
                "SummaryPlannedNonLaborCost":"Double",
                "SummaryPlannedNonLaborUnits":"Double",
                "SummaryPlannedStartDate":"Date",
                "SummaryPlannedValueByCost":"Double",
                "SummaryPlannedValueByLaborUnits":"Double",
                "SummaryProgressFinishDate":"Date",
                "SummaryRemainingDuration":"Double",
                "SummaryRemainingExpenseCost":"Double",
                "SummaryRemainingFinishDate":"Date",
                "SummaryRemainingLaborCost":"Double",
                "SummaryRemainingLaborUnits":"Double",
                "SummaryRemainingMaterialCost":"Double",
                "SummaryRemainingNonLaborCost":"Double",
                "SummaryRemainingNonLaborUnits":"Double",
                "SummaryRemainingStartDate":"Date",
                "SummaryRemainingTotalCost":"Double",
                "SummarySchedulePercentComplete":"Double",
                "SummarySchedulePercentCompleteByLaborUnits":"Double",
                "SummarySchedulePerformanceIndexByCost":"Double",
                "SummarySchedulePerformanceIndexByLaborUnits":"Double",
                "SummaryScheduleVarianceByCost":"Double",
                "SummaryScheduleVarianceByLaborUnits":"Double",
                "SummaryScheduleVarianceIndex":"Double",
                "SummaryScheduleVarianceIndexByCost":"Double",
                "SummaryScheduleVarianceIndexByLaborUnits":"Double",
                "SummaryStartDateVariance":"Double",
                "SummaryToCompletePerformanceIndexByCost":"Double",
                "SummaryTotalCostVariance":"Double",
                "SummaryTotalFloat":"Double",
                "SummaryUnitsPercentComplete":"Double",
                "SummaryVarianceAtCompletionByLaborUnits":"Double",
                "SyncWbsHierarchyFlag":"Text",
                "TeamMemberActivityFields":"Text",
                "TeamMemberAddNewActualUnits":"Text",
                "TeamMemberAssignmentOption":"Text",
                "TeamMemberCanStatusOtherResources":"Text",
                "TeamMemberCanUpdateNotebooks":"Text",
                "TeamMemberDisplayPlannedUnit":"Text",
                "TeamMemberDisplayTotalFloatFlag":"Text",
                "TeamMemberIncludePrimaryResources":"Text",
                "TeamMemberResourceAssignmentFields":"Text",
                "TeamMemberStepUDFViewableFields":"Text",
                "TeamMemberStepsAddDeletable":"Text",
                "TeamMemberViewableFields":"Text",
                "TotalBenefitPlan":"Double",
                "TotalBenefitPlanTally":"Double",
                "TotalFunding":"Double",
                "TotalSpendingPlan":"Double",
                "TotalSpendingPlanTally":"Double",
                "UnallocatedBudget":"Double",
                "UndistributedCurrentVariance":"Double",
                "UnifierCBSTasksOnlyFlag":"Text",
                "UnifierDataMappingName":"Text",
                "UnifierDeleteActivitiesFlag":"Text",
                "UnifierEnabledFlag":"Text",
                "UnifierProjectName":"Text",
                "UnifierProjectNumber":"Text",
                "UnifierScheduleSheetName":"Text",
                "UseExpectedFinishDates":"Text",
                "UseProjectBaselineForEarnedValue":"Text",
                "WBSCodeSeparator":"Text",
                "WBSHierarchyLevels":"Integer",
                "WBSMilestonePercentComplete":"Double",
                "WBSObjectId":"Integer",
                "WebSiteRootDirectory":"Text",
                "WebSiteURL":"Text"
            }
        
        elif filterType == "WBS":
            return {
                "AnticipatedFinishDate":"Date",
                "AnticipatedStartDate":"Date",
                "Code":"Text",
                "ContainsSummaryData":"Text",
                "CreateDate":"Date",
                "CreateUser":"Text",
                "CurrentBudget":"Double",
                "CurrentVariance":"Double",
                "DistributedCurrentBudget":"Double",
                "EarnedValueComputeType":"Text",
                "EarnedValueETCComputeType":"Text",
                "EarnedValueETCUserValue":"Double",
                "EarnedValueUserPercent":"Double",
                "EstimatedWeight":"Double",
                "FinishDate":"Date",
                "ForecastFinishDate":"Date",
                "ForecastStartDate":"Date",
                "GUID":"Text",
                "IndependentETCLaborUnits":"Double",
                "IndependentETCTotalCost":"Double",
                "IntegratedType":"Text",
                "IntegratedWBS":"Text",
                "IsBaseline":"Text",
                "IsTemplate":"Text",
                "IsWorkPackage":"Text",
                "LastUpdateDate":"Date",
                "LastUpdateUser":"Text",
                "Name":"Text",
                "OBSName":"Text",
                "OBSObjectId":"Integer",
                "ObjectId":"Integer",
                "OriginalBudget":"Double",
                "ParentObjectId":"Integer",
                "ProjectId":"Text",
                "ProjectObjectId":"Text",
                "ProposedBudget":"Double",
                "RolledUpFinishDate":"Date",
                "RolledUpStartDate":"Date",
                "SequenceNumber":"Integer",
                "StartDate":"Date",
                "Status":"Text",
                "StatusReviewerName":"Text",
                "StatusReviewerObjectId":"Integer",
                "SummaryAccountingVarianceByCost":"Double",
                "SummaryAccountingVarianceByLaborUnits":"Double",
                "SummaryActivityCount":"Integer",
                "SummaryActualDuration":"Double",
                "SummaryActualExpenseCost":"Double",
                "SummaryActualFinishDate":"Date",
                "SummaryActualLaborCost":"Double",
                "SummaryActualLaborUnits":"Double",
                "SummaryActualMaterialCost":"Double",
                "SummaryActualNonLaborCost":"Double",
                "SummaryActualNonLaborUnits":"Double",
                "SummaryActualStartDate":"Date",
                "SummaryActualThisPeriodCost":"Double",
                "SummaryActualThisPeriodLaborCost":"Double",
                "SummaryActualThisPeriodLaborUnits":"Double",
                "SummaryActualThisPeriodMaterialCost":"Double",
                "SummaryActualThisPeriodNonLaborCost":"Double",
                "SummaryActualThisPeriodNonLaborUnits":"Double",
                "SummaryActualTotalCost":"Double",
                "SummaryActualValueByCost":"Double",
                "SummaryActualValueByLaborUnits":"Double",
                "SummaryAtCompletionDuration":"Double",
                "SummaryAtCompletionExpenseCost":"Double",
                "SummaryAtCompletionLaborCost":"Double",
                "SummaryAtCompletionLaborUnits":"Double",
                "SummaryAtCompletionMaterialCost":"Double",
                "SummaryAtCompletionNonLaborCost":"Double",
                "SummaryAtCompletionNonLaborUnits":"Double",
                "SummaryAtCompletionTotalCost":"Double",
                "SummaryAtCompletionTotalCostVariance":"Double",
                "SummaryBaselineCompletedActivityCount":"Integer",
                "SummaryBaselineDuration":"Double",
                "SummaryBaselineExpenseCost":"Double",
                "SummaryBaselineFinishDate":"Date",
                "SummaryBaselineInProgressActivityCount":"Integer",
                "SummaryBaselineLaborCost":"Double",
                "SummaryBaselineLaborUnits":"Double",
                "SummaryBaselineMaterialCost":"Double",
                "SummaryBaselineNonLaborCost":"Double",
                "SummaryBaselineNonLaborUnits":"Double",
                "SummaryBaselineNotStartedActivityCount":"Integer",
                "SummaryBaselineStartDate":"Date",
                "SummaryBaselineTotalCost":"Double",
                "SummaryBudgetAtCompletionByCost":"Double",
                "SummaryBudgetAtCompletionByLaborUnits":"Double",
                "SummaryCompletedActivityCount":"Integer",
                "SummaryCostPercentComplete":"Double",
                "SummaryCostPercentOfPlanned":"Double",
                "SummaryCostPerformanceIndexByCost":"Double",
                "SummaryCostPerformanceIndexByLaborUnits":"Double",
                "SummaryCostVarianceByCost":"Double",
                "SummaryCostVarianceByLaborUnits":"Double",
                "SummaryCostVarianceIndex":"Double",
                "SummaryCostVarianceIndexByCost":"Double",
                "SummaryCostVarianceIndexByLaborUnits":"Double",
                "SummaryDurationPercentComplete":"Double",
                "SummaryDurationPercentOfPlanned":"Double",
                "SummaryDurationVariance":"Double",
                "SummaryEarnedValueByCost":"Double",
                "SummaryEarnedValueByLaborUnits":"Double",
                "SummaryEstimateAtCompletionByCost":"Double",
                "SummaryEstimateAtCompletionByLaborUnits":"Double",
                "SummaryEstimateAtCompletionHighPercentByLaborUnits":"Double",
                "SummaryEstimateAtCompletionLowPercentByLaborUnits":"Double",
                "SummaryEstimateToCompleteByCost":"Double",
                "SummaryEstimateToCompleteByLaborUnits":"Double",
                "SummaryExpenseCostPercentComplete":"Double",
                "SummaryExpenseCostVariance":"Double",
                "SummaryFinishDateVariance":"Double",
                "SummaryInProgressActivityCount":"Integer",
                "SummaryLaborCostPercentComplete":"Double",
                "SummaryLaborCostVariance":"Double",
                "SummaryLaborUnitsPercentComplete":"Double",
                "SummaryLaborUnitsVariance":"Double",
                "SummaryMaterialCostPercentComplete":"Double",
                "SummaryMaterialCostVariance":"Double",
                "SummaryNonLaborCostPercentComplete":"Double",
                "SummaryNonLaborCostVariance":"Double",
                "SummaryNonLaborUnitsPercentComplete":"Double",
                "SummaryNonLaborUnitsVariance":"Double",
                "SummaryNotStartedActivityCount":"Integer",
                "SummaryPerformancePercentCompleteByCost":"Double",
                "SummaryPerformancePercentCompleteByLaborUnits":"Double",
                "SummaryPlannedCost":"Double",
                "SummaryPlannedDuration":"Double",
                "SummaryPlannedExpenseCost":"Double",
                "SummaryPlannedFinishDate":"Date",
                "SummaryPlannedLaborCost":"Double",
                "SummaryPlannedLaborUnits":"Double",
                "SummaryPlannedMaterialCost":"Double",
                "SummaryPlannedNonLaborCost":"Double",
                "SummaryPlannedNonLaborUnits":"Double",
                "SummaryPlannedStartDate":"Date",
                "SummaryPlannedValueByCost":"Double",
                "SummaryPlannedValueByLaborUnits":"Double",
                "SummaryProgressFinishDate":"Date",
                "SummaryRemainingDuration":"Double",
                "SummaryRemainingExpenseCost":"Double",
                "SummaryRemainingFinishDate":"Date",
                "SummaryRemainingLaborCost":"Double",
                "SummaryRemainingLaborUnits":"Double",
                "SummaryRemainingMaterialCost":"Double",
                "SummaryRemainingNonLaborCost":"Double",
                "SummaryRemainingNonLaborUnits":"Double",
                "SummaryRemainingStartDate":"Date",
                "SummaryRemainingTotalCost":"Double",
                "SummarySchedulePercentComplete":"Double",
                "SummarySchedulePercentCompleteByLaborUnits":"Double",
                "SummarySchedulePerformanceIndexByCost":"Double",
                "SummarySchedulePerformanceIndexByLaborUnits":"Double",
                "SummaryScheduleVarianceByCost":"Double",
                "SummaryScheduleVarianceByLaborUnits":"Double",
                "SummaryScheduleVarianceIndex":"Double",
                "SummaryScheduleVarianceIndexByCost":"Double",
                "SummaryScheduleVarianceIndexByLaborUnits":"Double",
                "SummaryStartDateVariance":"Double",
                "SummaryToCompletePerformanceIndexByCost":"Double",
                "SummaryTotalCostVariance":"Double",
                "SummaryTotalFloat":"Double",
                "SummaryUnitsPercentComplete":"Double",
                "SummaryVarianceAtCompletionByLaborUnits":"Double",
                "TotalBenefitPlan":"Double",
                "TotalBenefitPlanTally":"Double",
                "TotalSpendingPlan":"Double",
                "TotalSpendingPlanTally":"Double",
                "UnallocatedBudget":"Double",
                "UndistributedCurrentVariance":"Double",
                "WBSCategoryObjectId":"Integer",
                "WBSMilestonePercentComplete":"Double"
            }
        
        elif filterType == "Activity":
            return {
                "AccountingVariance":"Double",
                "AccountingVarianceLaborUnits":"Double",
                "ActivityOwnerUserId":"Integer",
                "ActualDuration":"Double",
                "ActualExpenseCost":"Double",
                "ActualFinishDate":"Date",
                "ActualLaborCost":"Double",
                "ActualLaborUnits":"Double",
                "ActualMaterialCost":"Double",
                "ActualNonLaborCost":"Double",
                "ActualNonLaborUnits":"Double",
                "ActualStartDate":"Date",
                "ActualThisPeriodLaborCost":"Double",
                "ActualThisPeriodLaborUnits":"Double",
                "ActualThisPeriodMaterialCost":"Double",
                "ActualThisPeriodNonLaborCost":"Double",
                "ActualThisPeriodNonLaborUnits":"Double",
                "ActualTotalCost":"Double",
                "ActualTotalUnits":"Double",
                "AtCompletionDuration":"Double",
                "AtCompletionExpenseCost":"Double",
                "AtCompletionLaborCost":"Double",
                "AtCompletionLaborUnits":"Double",
                "AtCompletionLaborUnitsVariance":"Double",
                "AtCompletionMaterialCost":"Double",
                "AtCompletionNonLaborCost":"Double",
                "AtCompletionNonLaborUnits":"Double",
                "AtCompletionTotalCost":"Double",
                "AtCompletionTotalUnits":"Double",
                "AtCompletionVariance":"Double",
                "AutoComputeActuals":"Text",
                "Baseline1Duration":"Double",
                "Baseline1FinishDate":"Date",
                "Baseline1PlannedDuration":"Double",
                "Baseline1PlannedExpenseCost":"Double",
                "Baseline1PlannedLaborCost":"Double",
                "Baseline1PlannedLaborUnits":"Double",
                "Baseline1PlannedMaterialCost":"Double",
                "Baseline1PlannedNonLaborCost":"Double",
                "Baseline1PlannedNonLaborUnits":"Double",
                "Baseline1PlannedTotalCost":"Double",
                "Baseline1StartDate":"Date",
                "BaselineDuration":"Double",
                "BaselineFinishDate":"Date",
                "BaselinePlannedDuration":"Double",
                "BaselinePlannedExpenseCost":"Double",
                "BaselinePlannedLaborCost":"Double",
                "BaselinePlannedLaborUnits":"Double",
                "BaselinePlannedMaterialCost":"Double",
                "BaselinePlannedNonLaborCost":"Double",
                "BaselinePlannedNonLaborUnits":"Double",
                "BaselinePlannedTotalCost":"Double",
                "BaselineStartDate":"Date",
                "BudgetAtCompletion":"Double",
                "CBSCode":"Text",
                "CBSId":"Integer",
                "CBSObjectId":"Integer",
                "CalendarName":"Text",
                "CalendarObjectId":"Integer",
                "CostPercentComplete":"Double",
                "CostPercentOfPlanned":"Double",
                "CostPerformanceIndex":"Double",
                "CostPerformanceIndexLaborUnits":"Double",
                "CostVariance":"Double",
                "CostVarianceIndex":"Double",
                "CostVarianceIndexLaborUnits":"Double",
                "CostVarianceLaborUnits":"Double",
                "CreateDate":"Date",
                "CreateUser":"Text",
                "DataDate":"Date",
                "Duration1Variance":"Double",
                "DurationPercentComplete":"Double",
                "DurationPercentOfPlanned":"Double",
                "DurationType":"Text",
                "DurationVariance":"Double",
                "EarlyFinishDate":"Date",
                "EarlyStartDate":"Date",
                "EarnedValueCost":"Double",
                "EarnedValueLaborUnits":"Double",
                "EstimateAtCompletionCost":"Double",
                "EstimateAtCompletionLaborUnits":"Double",
                "EstimateToComplete":"Double",
                "EstimateToCompleteLaborUnits":"Double",
                "ExpectedFinishDate":"Date",
                "ExpenseCost1Variance":"Double",
                "ExpenseCostPercentComplete":"Double",
                "ExpenseCostVariance":"Double",
                "ExternalEarlyStartDate":"Date",
                "ExternalLateFinishDate":"Date",
                "Feedback":"Text",
                "FinishDate":"Date",
                "FinishDate1Variance":"Double",
                "FinishDateVariance":"Double",
                "FloatPath":"Integer",
                "FloatPathOrder":"Integer",
                "FreeFloat":"Double",
                "GUID":"Text",
                "HasFutureBucketData":"Text",
                "Id":"Text",
                "IsBaseline":"Text",
                "IsCritical":"Text",
                "IsLongestPath":"Text",
                "IsNewFeedback":"Text",
                "IsTemplate":"Text",
                "IsWorkPackage":"Text",
                "IsStarred":"Text",
                "LaborCost1Variance":"Double",
                "LaborCostPercentComplete":"Double",
                "LaborCostVariance":"Double",
                "LaborUnits1Variance":"Double",
                "LaborUnitsPercentComplete":"Double",
                "LaborUnitsVariance":"Double",
                "LastUpdateDate":"Date",
                "LastUpdateUser":"Text",
                "LateFinishDate":"Date",
                "LateStartDate":"Date",
                "LevelingPriority":"Text",
                "LocationName":"Text",
                "LocationObjectId":"Integer",
                "MaterialCost1Variance":"Double",
                "MaterialCostPercentComplete":"Double",
                "MaterialCostVariance":"Double",
                "MaximumDuration":"Double",
                "MinimumDuration":"Double",
                "MostLikelyDuration":"Double",
                "Name":"Text",
                "NonLaborCost1Variance":"Double",
                "NonLaborCostPercentComplete":"Double",
                "NonLaborCostVariance":"Double",
                "NonLaborUnits1Variance":"Double",
                "NonLaborUnitsPercentComplete":"Double",
                "NonLaborUnitsVariance":"Double",
                "NotesToResources":"Text",
                "ObjectId":"Integer",
                "PercentComplete":"Double",
                "PercentCompleteType":"Text",
                "PerformancePercentComplete":"Double",
                "PerformancePercentCompleteByLaborUnits":"Double",
                "PhysicalPercentComplete":"Double",
                "PlannedDuration":"Double",
                "PlannedExpenseCost":"Double",
                "PlannedFinishDate":"Date",
                "PlannedLaborCost":"Double",
                "PlannedLaborUnits":"Double",
                "PlannedMaterialCost":"Double",
                "PlannedNonLaborCost":"Double",
                "PlannedNonLaborUnits":"Double",
                "PlannedStartDate":"Date",
                "PlannedTotalCost":"Double",
                "PlannedTotalUnits":"Double",
                "PlannedValueCost":"Double",
                "PlannedValueLaborUnits":"Double",
                "PostRespCriticalityIndex":"Double",
                "PostResponsePessimisticFinish":"Date",
                "PostResponsePessimisticStart":"Date",
                "PreRespCriticalityIndex":"Double",
                "PreResponsePessimisticFinish":"Date",
                "PreResponsePessimisticStart":"Date",
                "PrimaryConstraintDate":"Date",
                "PrimaryConstraintType":"Text",
                "PrimaryResourceId":"Text",
                "PrimaryResourceName":"Text",
                "PrimaryResourceObjectId":"Integer",
                "ProjectFlag":"Text",
                "ProjectId":"Text",
                "ProjectName":"Text",
                "ProjectObjectId":"Text",
                "ProjectProjectFlag":"Text",
                "RemainingDuration":"Double",
                "RemainingEarlyFinishDate":"Date",
                "RemainingEarlyStartDate":"Date",
                "RemainingExpenseCost":"Double",
                "RemainingFloat":"Double",
                "RemainingLaborCost":"Double",
                "RemainingLaborUnits":"Double",
                "RemainingLateFinishDate":"Date",
                "RemainingLateStartDate":"Date",
                "RemainingMaterialCost":"Double",
                "RemainingNonLaborCost":"Double",
                "RemainingNonLaborUnits":"Double",
                "RemainingTotalCost":"Double",
                "RemainingTotalUnits":"Double",
                "ResumeDate":"Date",
                "ReviewFinishDate":"Date",
                "ReviewRequired":"Text",
                "ReviewStatus":"Text",
                "SchedulePercentComplete":"Double",
                "SchedulePerformanceIndex":"Double",
                "SchedulePerformanceIndexLaborUnits":"Double",
                "ScheduleVariance":"Double",
                "ScheduleVarianceIndex":"Double",
                "ScheduleVarianceIndexLaborUnits":"Double",
                "ScheduleVarianceLaborUnits":"Double",
                "ScopePercentComplete":"Double",
                "SecondaryConstraintDate":"Date",
                "SecondaryConstraintType":"Text",
                "StartDate":"Date",
                "StartDate1Variance":"Double",
                "StartDateVariance":"Double",
                "Status":"Text",
                "StatusCode":"Text",
                "SuspendDate":"Date",
                "TaskStatusCompletion":"Text",
                "TaskStatusDates":"Text",
                "TaskStatusIndicator":"Text",
                "ToCompletePerformanceIndex":"Double",
                "TotalCost1Variance":"Double",
                "TotalCostVariance":"Double",
                "TotalFloat":"Double",
                "Type":"Text",
                "UnitsPercentComplete":"Double",
                "UnreadCommentCount":"Integer",
                "WBSCode":"Text",
                "WBSName":"Text",
                "WBSNamePath":"Text",
                "WBSObjectId":"Integer",
                "WBSPath":"Text",
                "WorkPackageId":"Text",
                "WorkPackageName":"Text"
            }
        
        elif filterType == "Activity Step":
            return {
                'ActivityId': "Text",
                'ActivityName': "Text",
                'ActivityObjectId': "Integer",
                'CreateDate': "Date",
                'CreateUser': "Text",
                'Description': "Text",
                'IsBaseline': "Text",
                'IsCompleted': "Text",
                'IsTemplate': "Text",
                'LastUpdateDate': "Date",
                'LastUpdateUser': "Text",
                'Name': "Text",
                'ObjectId': "Integer",
                'PercentComplete': "Double",
                'ProjectId': "Text",
                'ProjectObjectId': "Text",
                'SequenceNumber': "Text",
                'WBSObjectId': "Integer",
                'Weight': "Double",
                'WeightPercent': "Double"
            }


    def castType(self, value, d_type):
        """Given a d_type and value cast the value and return."""
        if value == None:
            return value
        elif d_type == "Text":
            value = str(value)
        elif d_type == "Integer":
            value = int(value)
        elif d_type == "Double":
            value = float(value)
        elif d_type == "Date":
            value = datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
        return value


    def group_by_date(self, table,fc,join_table_field, join_feature_field, group_field):
        """group_by_date applies a grouping opperation 
        finding the earliest and latest dates from a given table and field.
        table (string): path to the p6 table
        fc (string): path to the feature class that is being grouped on.
        join_table_field: The join field to group on.
        join_feature_field: The join field to group on.
        group_field: The date field from table where we find the oldest date and the newest.
        """
        first = group_field+"_first"
        last = group_field+"_last"
        fields = arcpy.ListFields(fc)
        fields = [f.name for f in fields]
        
        # add new date fields if needed
        if not first in fields:
            arcpy.AddField_management(in_table=fc, 
                                    field_name= first, 
                                    field_type="DATE")
        if not last in fields:
            arcpy.AddField_management(in_table=fc, 
                                    field_name= last, 
                                    field_type="DATE")
        
        # Loop through all fc rows
        fields = [join_feature_field, first, last]
        with arcpy.da.UpdateCursor(fc, fields) as fc_cursor:
            for fc_row in fc_cursor:
                if fc_row[0] == None:
                    continue  # Skip rows with None value for join_field
                
                # Loop through all table rows to find matches
                fields = [join_table_field, group_field]
                dates = []
                with arcpy.da.SearchCursor(table, fields) as table_cursor:
                    for t_row in table_cursor:
                        if t_row[0] == None or t_row[1] == None:
                            continue
                        if fc_row[0] == t_row[0]:
                            dates.append(t_row[1])
                dates = sorted(dates)
                if len(dates) > 0:
                    first_date = dates[0]
                    last_date = dates[-1]
                    fc_row[1], fc_row[2] = first_date, last_date
                    print(first_date, last_date)
                    fc_cursor.updateRow(fc_row)

        return

    def group_by_category(self, table,fc,join_table_field, join_feature_field, group_field):
        """group_by_category creates a column for each value of the specified field.
        Each row of the fc is populated with a True or False.
        True means there is at least one matching row included in category.
        table (string): path to the p6 table
        fc (string): path to the feature class that is being grouped on.
        join_table_field: The join field to group on.
        join_feature_field: The join field to group on.
        group_field: The date field from table where we find the oldest date and the newest.
        """
        # Loop through the given table field to get all possible categories.
        fields = [group_field]
        categories = []
        with arcpy.da.SearchCursor(table, fields) as table_cursor:
            for t_row in table_cursor:
                if t_row[0] == None:
                    continue
                categories.append(t_row[0])
        categories = list(set(categories))
        idxs = list(range(1,len(categories)+1))
    #     print(idxs)
    #     print(categories)
    #     cat2idx = {cat:i+1 for i,cat in enumerate(categories)}
        columns = []
        for c,i in zip(categories,idxs):
            f_name = group_field + "_cat" + str(i) + "_" + c.replace(" ","_").replace("-","_")
            clean_name = ""
            for l in f_name:
                if l.isalpha() or l.isnumeric() or l=="_":
                    clean_name += l
                else:
                    clean_name += "_"
            f_name = clean_name
            if len(f_name) > 64:
                f_name = f_name[:65]
            columns.append(f_name)
        assert len(list(set(columns))) == len(categories), "Error: Not all columns names unique."
    #     print(len(columns))
    #     print(list(zip(categories, columns)))
        
        # Add all columns to the fc.
        fields = arcpy.ListFields(fc)
        fields = [f.name for f in fields]
        
        for col in columns:
    #         print(col)

            # add new text fields if needed
            if not col in fields:
                arcpy.AddField_management(in_table=fc, 
                                        field_name= col, 
                                        field_type="TEXT",
                                        field_length=255)
                
        # Loop through all fc rows.
        fields = [join_feature_field] + columns
        with arcpy.da.UpdateCursor(fc, fields) as fc_cursor:
            for fc_row in fc_cursor:
                if fc_row[0] == None:
                    continue  # Skip rows with None value for join_field
                cats = []
                fields = [join_table_field, group_field]
                with arcpy.da.SearchCursor(table, fields) as table_cursor:
                    for t_row in table_cursor:
                        if t_row[0] == None or t_row[1] == None:
                            continue
                        if fc_row[0] == t_row[0]:
                            cats.append(t_row[1])
                cats = list(set(cats))
                for cat,col,idx in zip(categories,columns,idxs):
                    fc_row[idx] = "FALSE"
                for cat,col,idx in zip(categories,columns,idxs):
                    if cat in cats:
                        value = "TRUE"
                        fc_row[idx] = value
                        print("fc_row: {} cat: {} idx: {} col: {}".format(fc_row[0], cat, idx, col))
    #                 print(fc_row)
                fc_cursor.updateRow(fc_row)
        return


class ExcelTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Sync Excel Schedule"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        params = []

        # Get P6 excel schedule
        param0 = arcpy.Parameter(
            displayName="Schedule File",
            name="schedule_path",
            datatype="DEFile",
            parameterType="Required",
            direction="Input"
        )
        param0.filter.list = ["xlsx"]
        params.append(param0)

        # Get p6 join field
        param1 = arcpy.Parameter( 
            displayName="Schedule Link Field", 
            name="schedule_link_field", 
            datatype="GPString",
            parameterType="Required", 
            direction="Input")
        param1.filter.type = "ValueList"
        param1.value = ""
        params.append(param1)

        # Get source feature class
        param2 = arcpy.Parameter( 
            displayName="Feature Class", 
            name="feat_class", 
            datatype="DEFeatureClass",
            parameterType="Required", 
            direction="Input")
        params.append(param2)

        # Get feature class join field
        param3 = arcpy.Parameter( 
            displayName="Feature Class Link Field", 
            name="fc_link_field", 
            datatype="Field",
            parameterType="Required", 
            direction="Input")
        param3.parameterDependencies = [param2.name]
        param3.value = ""
        params.append(param3)

        # Get field date fields
        param4 = arcpy.Parameter( 
            displayName="Schedule Date Fields", 
            name="date_fields", 
            datatype="GPValueTable",
            parameterType="Optional", 
            direction="Input",
            multiValue=True)
        param4.columns = [['GPString', 'Statistic Type']]
        param4.filters[0].type = 'ValueList'
        params.append(param4)

        # Get input date format
        param5 = arcpy.Parameter( 
            displayName="Date Format String",
            name="date_format",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        params.append(param5)

        # Get hosted feature service title
        param6 = arcpy.Parameter( 
            displayName="Hosted Feature Service Title",
            name="title",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        params.append(param6)

        # Get hosted feature service title
        param7 = arcpy.Parameter( 
            displayName="Schedule Table Name",
            name="table_name",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        params.append(param7)

        # Get geodatabase name
        param8 = arcpy.Parameter( 
            displayName="Geodatabase Name",
            name="gdb_name",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        params.append(param8)

        # Get folder
        param9 = arcpy.Parameter( 
            displayName="Folder",
            name="folder",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        param9.value = "schedule_sync"
        params.append(param9)

        # Get tag
        param10 = arcpy.Parameter( 
            displayName="Tag",
            name="tag",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        param10.value = "schedule_sync"
        params.append(param10)

        # Get relate or join
        param11 = arcpy.Parameter( 
            displayName="Select Relate or Join", 
            name="relate_or_join", 
            datatype="GPString",
            parameterType="Required", 
            direction="Input")
        param11.filter.type = "ValueList"
        param11.filter.list = ["relate","join"]
        param11.value = "relate"
        params.append(param11)

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        # Check if we have excel file
        if parameters[0].valueAsText:
            # Get excel file columns
            cols = getColumns(parameters[0].valueAsText)
            # Set Schedule Link field col list
            parameters[1].filter.list = cols
            # Set fields with date datatype
            parameters[4].filters[0].list = cols

        if parameters[8].valueAsText and (not Path(parameters[8].valueAsText).suffix == ".gdb"):
            parameters[8].value = parameters[8].value + ".gdb"
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        # Validate P6 Excel file
        if parameters[0].valueAsText:
            if not Path(parameters[0].valueAsText).is_file():
                parameters[0].setErrorMessage("Error: File does not exist. Please select excel file.")
            if not Path(parameters[0].valueAsText).suffix == ".xlsx":
                parameters[0].setErrorMessage("Error: Please select excel file with an xlsx extension.")
            # Get excel file columns
            cols = getColumns(parameters[0].valueAsText)
            for col in cols:
                if not col.replace("_","").isalnum():
                    parameters[0].setErrorMessage(
                        f"Error: Column {col} has invalid characters." + \
                        "Please change the column name to use alpha, numeric, and underscore characters only.")
                if not (col[0].isalpha() or col[0]=='_'):
                    parameters[0].setErrorMessage(f"Error: Column {col} starts with an invalid character. Please change the column to start with a letter.")

        # Validate Table name
        if parameters[7].valueAsText:
            if not parameters[7].valueAsText.replace("_","").isalnum():
                parameters[7].setErrorMessage(
                    f"Error: Table name has invalid characters." + \
                    "Please change the table name to use alpha, numeric, and underscore characters only.")
            if not (parameters[7].valueAsText[0].isalpha() or parameters[7].valueAsText[0]=='_'):
                parameters[7].setErrorMessage(f"Error: Table name starts with an invalid character. Please change the table name to start with a letter.")

        # Validate gdb name
        if parameters[8].valueAsText:
            if not parameters[8].valueAsText.replace("_","").replace(".","").isalnum():
                parameters[8].setErrorMessage(
                    f"Error: GDB name has invalid characters." + \
                    "Please change the GDB name to use alpha, numeric, and underscore characters only.")
            if not (parameters[8].valueAsText[0].isalpha() or parameters[8].valueAsText[0]=='_'):
                parameters[8].setErrorMessage(f"Error: GDB name starts with an invalid character. Please change the GDB name to start with a letter.")
            if not Path(parameters[8].valueAsText).suffix == ".gdb":
                parameters[8].setErrorMessage("Error: Please provide a GDB name with a .gdb extension.")


        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        arcpy.AddMessage(f"Starting {self.label} tool.")
        
        params = {
            "p6_path":parameters[0].valueAsText,
            "p6link_field":parameters[1].valueAsText,
            "feat_class":parameters[2].valueAsText,
            "fc_link_field":parameters[3].valueAsText,
            "date_fields": set() if not (parameters[4].value) or len(parameters[4].value) == 0 else set([x[0] for x in parameters[4].value]),
            "date_format":parameters[5].valueAsText,
            "title":parameters[6].valueAsText,
            "table_name":parameters[7].valueAsText,
            "gdb_name":parameters[8].valueAsText,
            "folder":parameters[9].valueAsText,
            "tag":parameters[10].valueAsText,
            "relate_or_join":parameters[11].valueAsText
        }
        arcpy.AddMessage("Input parameters loaded.")

        with tempfile.TemporaryDirectory() as path:
            arcpy.AddMessage("Temporary directory created.")

            # Connect to gis
            g = GIS('pro')
            arcpy.AddMessage("Authentification complete.")
            
            # Set local variables
            gdb_path = os.path.join(path, params["gdb_name"])
            table_path = os.path.join(gdb_path,params["table_name"])
            source_fc_name = str(Path(params["feat_class"]).name)
            target_fc_path = os.path.join(gdb_path, source_fc_name)
            rel_path = os.path.join(gdb_path, source_fc_name+'_relate')
            title = params["title"]
            tag = params["tag"]
            folder_name = params["folder"]
            
            # create temp gdb
            arcpy.CreateFileGDB_management(path, params["gdb_name"])
            arcpy.env.workspace = gdb_path
            arcpy.AddMessage("Temporary GDB created.")
            
            # Read excel to table
            df = pd.read_excel(params["p6_path"], dtype=str)[:1]
            field_names = df.columns.to_list()
            field_names = cleanFieldNames(field_names)
            alias_names = df.iloc[0].to_list()[:len(field_names)]
            alias_names = cleanAliasNames(alias_names)
            fieldToAlias = {field:alias for field,alias in zip(field_names, alias_names)}
            arcpy.AddMessage("Loaded and cleaned table field names.")

            df = pd.read_excel(params["p6_path"], skiprows=[1])
            date_cols = {col:str for col in df.columns if col in params["date_fields"]}
            if date_cols:
                df = pd.read_excel(params["p6_path"], dtype=date_cols, skiprows=[1])
            arcpy.AddMessage("Schedule data loaded into dataframe.")

            # Convert date fields to milliseconds
            date_cols = [col for col in df.columns if col in params["date_fields"]]
            for col in date_cols:
                # for index, row in df.iterrows():
                #     print(row[col])
                # arcpy.AddMessage(df[col].astype(str))
                df[col] = df[col].astype(str).apply(lambda x: None if x=='nan' else int(datetime.datetime.strptime(x, params["date_format"]).timestamp() * 1000))
            arcpy.AddMessage("Datetime data converted to millisecond format.")

            df.spatial.to_table(table_path, overwrite=True, sanitize_columns=False)
            arcpy.AddMessage("Table created in GDB.")

            flds = arcpy.ListFields(table_path)
            for fld in flds:
                if fld.name in fieldToAlias:
                    fld.aliasName = fieldToAlias[fld.name]
                    arcpy.AlterField_management(in_table=table_path,
                                                field=fld.name,
                                                new_field_alias=fieldToAlias[fld.name])
            arcpy.AddMessage("All table alias names have been set.")

            for col in date_cols:
                arcpy.ConvertTimeField_management(in_table=table_path, 
                                                input_time_field=col, 
                                                input_time_format='unix_ms', 
                                                output_time_field=col+'_date', 
                                                output_time_format='DATE')
                arcpy.DeleteField_management(table_path, [col])
                arcpy.AlterField_management(table_path, col+'_date', col, col)
            arcpy.AddMessage("Table date columns converted to the Esri datetime format.")

            arcpy.FeatureClassToFeatureClass_conversion(params["feat_class"], 
                                                    gdb_path, 
                                                    source_fc_name)
            arcpy.AddMessage("Source feature class being copied into temporary GDB.")

            # Do relate
            createRelateOrJoin(table_path, target_fc_path, rel_path, params["p6link_field"], params["fc_link_field"], params["relate_or_join"])

            published_item = syncSchedule(gdb_path, path, params["gdb_name"], g, title, folder_name, tag)

            arcpy.AddMessage("Starting validation process.")
            validatePublishedTable(n_table_rows_source=len(df), published_item=published_item)

            # Validate published feature service data
            validatePublishedFeatureClass(source_fc_path=params["feat_class"], 
                                            published_item=published_item)

        return


    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return


class CsvTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Sync CSV Schedule"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        params = []

        # Get P6 excel schedule
        param0 = arcpy.Parameter(
            displayName="Schedule File",
            name="schedule_path",
            datatype="DEFile",
            parameterType="Required",
            direction="Input"
        )
        param0.filter.list = ["csv"]
        params.append(param0)

        # Get p6 join field
        param1 = arcpy.Parameter( 
            displayName="Schedule Link Field", 
            name="schedule_link_field", 
            datatype="GPString",
            parameterType="Required", 
            direction="Input")
        param1.filter.type = "ValueList"
        param1.value = ""
        params.append(param1)

        # Get source feature class
        param2 = arcpy.Parameter( 
            displayName="Feature Class", 
            name="feat_class", 
            datatype="DEFeatureClass",
            parameterType="Required", 
            direction="Input")
        params.append(param2)

        # Get feature class join field
        param3 = arcpy.Parameter( 
            displayName="Feature Class Link Field", 
            name="fc_link_field", 
            datatype="Field",
            parameterType="Required", 
            direction="Input")
        param3.parameterDependencies = [param2.name]
        param3.value = ""
        params.append(param3)

        # Get field date fields
        param4 = arcpy.Parameter( 
            displayName="Schedule Date Fields", 
            name="date_fields", 
            datatype="GPValueTable",
            parameterType="Optional", 
            direction="Input",
            multiValue=True)
        param4.columns = [['GPString', 'Statistic Type']]
        param4.filters[0].type = 'ValueList'
        params.append(param4)

        # Get input date format
        param5 = arcpy.Parameter( 
            displayName="Date Format String",
            name="date_format",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        params.append(param5)

        # Get hosted feature service title
        param6 = arcpy.Parameter( 
            displayName="Hosted Feature Service Title",
            name="title",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        params.append(param6)

        # Get hosted feature service title
        param7 = arcpy.Parameter( 
            displayName="Schedule Table Name",
            name="table_name",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        params.append(param7)

        # Get geodatabase name
        param8 = arcpy.Parameter( 
            displayName="Geodatabase Name",
            name="gdb_name",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        params.append(param8)

        # Get folder
        param9 = arcpy.Parameter( 
            displayName="Folder",
            name="folder",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        param9.value = "schedule_sync"
        params.append(param9)

        # Get tag
        param10 = arcpy.Parameter( 
            displayName="Tag",
            name="tag",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        param10.value = "schedule_sync"
        params.append(param10)

        # Get relate or join
        param11 = arcpy.Parameter( 
            displayName="Select Relate or Join", 
            name="relate_or_join", 
            datatype="GPString",
            parameterType="Required", 
            direction="Input")
        param11.filter.type = "ValueList"
        param11.filter.list = ["relate","join"]
        param11.value = "relate"
        params.append(param11)

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        # Check if we have excel file
        if parameters[0].valueAsText:
            # Get excel file columns
            cols = getColumns(parameters[0].valueAsText)
            # Set Schedule Link field col list
            parameters[1].filter.list = cols
            # Set fields with date datatype
            parameters[4].filters[0].list = cols

        if parameters[8].valueAsText and (not Path(parameters[8].valueAsText).suffix == ".gdb"):
            parameters[8].value = parameters[8].value + ".gdb"
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        # Validate P6 Excel file
        if parameters[0].valueAsText:
            if not Path(parameters[0].valueAsText).is_file():
                parameters[0].setErrorMessage("Error: File does not exist. Please select a csv file.")
            if not Path(parameters[0].valueAsText).suffix == ".csv":
                parameters[0].setErrorMessage("Error: Please select a csv file with a csv extension.")
            # Get excel file columns
            cols = getColumns(parameters[0].valueAsText)
            for col in cols:
                if not col.replace("_","").isalnum():
                    parameters[0].setErrorMessage(
                        f"Error: Column {col} has invalid characters." + \
                        "Please change the column name to use alpha, numeric, and underscore characters only.")
                if not (col[0].isalpha() or col[0]=='_'):
                    parameters[0].setErrorMessage(f"Error: Column {col} starts with an invalid character. Please change the column to start with a letter.")

        # Validate Table name
        if parameters[7].valueAsText:
            if not parameters[7].valueAsText.replace("_","").isalnum():
                parameters[7].setErrorMessage(
                    f"Error: Table name has invalid characters." + \
                    "Please change the table name to use alpha, numeric, and underscore characters only.")
            if not (parameters[7].valueAsText[0].isalpha() or parameters[7].valueAsText[0]=='_'):
                parameters[7].setErrorMessage(f"Error: Table name starts with an invalid character. Please change the table name to start with a letter.")

        # Validate gdb name
        if parameters[8].valueAsText:
            if not parameters[8].valueAsText.replace("_","").replace(".","").isalnum():
                parameters[8].setErrorMessage(
                    f"Error: GDB name has invalid characters." + \
                    "Please change the GDB name to use alpha, numeric, and underscore characters only.")
            if not (parameters[8].valueAsText[0].isalpha() or parameters[8].valueAsText[0]=='_'):
                parameters[8].setErrorMessage(f"Error: GDB name starts with an invalid character. Please change the GDB name to start with a letter.")
            if not Path(parameters[8].valueAsText).suffix == ".gdb":
                parameters[8].setErrorMessage("Error: Please provide a GDB name with a .gdb extension.")


        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        arcpy.AddMessage(f"Starting {self.label} tool.")
        
        params = {
            "p6_path":parameters[0].valueAsText,
            "p6link_field":parameters[1].valueAsText,
            "feat_class":parameters[2].valueAsText,
            "fc_link_field":parameters[3].valueAsText,
            "date_fields": set() if not (parameters[4].value) or len(parameters[4].value) == 0 else set([x[0] for x in parameters[4].value]),
            "date_format":parameters[5].valueAsText,
            "title":parameters[6].valueAsText,
            "table_name":parameters[7].valueAsText,
            "gdb_name":parameters[8].valueAsText,
            "folder":parameters[9].valueAsText,
            "tag":parameters[10].valueAsText,
            "relate_or_join":parameters[11].valueAsText
        }
        arcpy.AddMessage("Input parameters loaded.")

        with tempfile.TemporaryDirectory() as path:
            arcpy.AddMessage("Temporary directory created.")

            # Connect to gis
            g = GIS('pro')
            arcpy.AddMessage("Authentification complete.")
            
            # Set local variables
            gdb_path = os.path.join(path, params["gdb_name"])
            table_path = os.path.join(gdb_path,params["table_name"])
            source_fc_name = str(Path(params["feat_class"]).name)
            target_fc_path = os.path.join(gdb_path, source_fc_name)
            rel_path = os.path.join(gdb_path, source_fc_name+'_relate')
            title = params["title"]
            tag = params["tag"]
            folder_name = params["folder"]
            
            # create temp gdb
            arcpy.CreateFileGDB_management(path, params["gdb_name"])
            arcpy.env.workspace = gdb_path
            arcpy.AddMessage("Temporary GDB created.")
            
            # Read csv to table
            df = pd.read_csv(params["p6_path"], dtype=str)[:1]
            field_names = df.columns.to_list()
            field_names = cleanFieldNames(field_names)
            alias_names = df.iloc[0].to_list()[:len(field_names)]
            alias_names = cleanAliasNames(alias_names)
            fieldToAlias = {field:alias for field,alias in zip(field_names, alias_names)}
            arcpy.AddMessage("Loaded and cleaned table field names.")

            df = pd.read_csv(params["p6_path"], skiprows=[1])
            date_cols = {col:str for col in df.columns if col in params["date_fields"]}
            if date_cols:
                df = pd.read_csv(params["p6_path"], dtype=date_cols, skiprows=[1])
            arcpy.AddMessage("Schedule data loaded into dataframe.")

            # Convert date fields to milliseconds
            date_cols = [col for col in df.columns if col in params["date_fields"]]
            for col in date_cols:
                # for index, row in df.iterrows():
                #     print(row[col])
                # arcpy.AddMessage(df[col].astype(str))
                df[col] = df[col].astype(str).apply(lambda x: None if x=='nan' else int(datetime.datetime.strptime(x, params["date_format"]).timestamp() * 1000))
            arcpy.AddMessage("Datetime data converted to millisecond format.")

            df.spatial.to_table(table_path, overwrite=True, sanitize_columns=False)
            arcpy.AddMessage("Table created in GDB.")

            flds = arcpy.ListFields(table_path)
            for fld in flds:
                if fld.name in fieldToAlias:
                    fld.aliasName = fieldToAlias[fld.name]
                    arcpy.AlterField_management(in_table=table_path,
                                                field=fld.name,
                                                new_field_alias=fieldToAlias[fld.name])
            arcpy.AddMessage("All table alias names have been set.")

            for col in date_cols:
                new_name = col + '_date'
                if new_name in set([f.name for f in arcpy.ListFields(table_path)]):
                    arcpy.AddMessage(f"Field name {new_name} alread exists. Removing.")
                    arcpy.DeleteField_management(table_path, [new_name])
                arcpy.ConvertTimeField_management(in_table=table_path, 
                                                input_time_field=col, 
                                                input_time_format='unix_ms', 
                                                output_time_field=col+'_date', 
                                                output_time_format='DATE')
                
                arcpy.DeleteField_management(table_path, [col])
                arcpy.AlterField_management(table_path, col+'_date', col, col)
                arcpy.AddMessage(f"Created field name {new_name}")
                
            arcpy.AddMessage("Table date columns converted to the Esri datetime format.")

            arcpy.FeatureClassToFeatureClass_conversion(params["feat_class"], 
                                                    gdb_path, 
                                                    source_fc_name)
            arcpy.AddMessage("Source feature class being copied into temporary GDB.")

            # Do relate
            createRelateOrJoin(table_path, target_fc_path, rel_path, params["p6link_field"], params["fc_link_field"], params["relate_or_join"])

            published_item = syncSchedule(gdb_path, path, params["gdb_name"], g, title, folder_name, tag)

            arcpy.AddMessage("Starting validation process.")
            validatePublishedTable(n_table_rows_source=len(df), published_item=published_item)

            # Validate published feature service data
            validatePublishedFeatureClass(source_fc_path=params["feat_class"], 
                                            published_item=published_item)

        return


    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return


def getColumns(file_path):
    """
    function used to get list of column names
    file_path (str): path to the file
    return Python List of column names as strings
    """
    if file_path[-4:].lower() == ".csv":
        return pd.read_csv(file_path).columns.to_list()
    else:
        return pd.read_excel(file_path).columns.to_list()


def cleanName(name):
    assert name, f"Error: {name} is not a valid field name."
    
    out = name[0] if name[0].isalpha() else ''
    for i, char in enumerate(name[1:]):
        if char.isalnum() or char in {'_'}:
            out = out + char
    assert out, f"Error: {out} is not a valid clean field name."
    return out


def createRelateOrJoin(table_path, target_fc_path, rel_path, scheduleLinkFld, fcLinkFld, relateOrJoin):
    """
    function to create relationship between table and feature class
    table_path (str): the path to the origin table
    target_fc_path (str): the path to the feature class
    rel_path (str): the path to the output relationship class
    scheduleLinkFld (str): the table key
    fcLinkFld (str): the feature class key
    relateOrJoin (str): value either "relate" or "join"
    """
    if relateOrJoin == "relate":
        # Do relate
        arcpy.CreateRelationshipClass_management(
            origin_table=table_path,
            destination_table=target_fc_path,
            out_relationship_class=rel_path,
            relationship_type="SIMPLE",
            forward_label='P6',
            backward_label='FC',
            cardinality="ONE_TO_MANY",
            origin_primary_key=scheduleLinkFld,
            origin_foreign_key=fcLinkFld
            )
        arcpy.AddMessage("Relationship class created between table and feature class.")
    else:
        # Do join
        skip_cols = ['ObjectID', 'OBJECTID']

        schedule = "_s"

        for f in arcpy.ListFields(table_path):
            found = False
            for skip in skip_cols:
                if skip.lower() in f.name.lower():
                    found = True
            if found:
                continue

            newName = f.name + schedule
            newAlias = f.aliasName + schedule
            if len(newName) > 30:
                newName = f.name[:28] + schedule
            if len(newAlias) > 30:
                newAlias = f.aliasName[:28] + schedule
            # Check if field already exists
            names = set([x.name for x in arcpy.ListFields(table_path)])
            if newName not in names:
                arcpy.AlterField_management(
                    in_table=table_path, 
                    field=f.name, 
                    new_field_name=newName
                    )
        # Get new link field
        scheduleLinkFld = scheduleLinkFld + schedule
        if len(scheduleLinkFld) > 30:
            scheduleLinkFld = scheduleLinkFld[:28] + schedule
        arcpy.AddMessage("Table field names updated with _s ending.")

        keepFields = []
        for f in arcpy.ListFields(table_path):
            found = False
            for skip in skip_cols:
                if skip.lower() in f.name.lower():
                    found = True
            if not found:
                keepFields.append(f.name)
        arcpy.AddMessage("Table fields to keep have been collected for join.")

        arcpy.DeleteField_management(target_fc_path, keepFields)
        arcpy.AddMessage("Conflicting fields removed from feature class.")

        arcpy.JoinField_management(
            in_data=target_fc_path, 
            in_field=fcLinkFld, 
            join_table=table_path, 
            join_field=scheduleLinkFld,
            fields=keepFields
            )
        arcpy.AddMessage("Schedule table joined to feature class.")
    return


def syncSchedule(gdb_path, out_folder_path, out_name, g, title, folder_name, tag):
    """
    function to sync a file gdb to an ArcGIS Enterpise or ArcGIS Online organization
    gdb_path (str): the path to the gdb to sync
    out_folder_path (str): the path to the out folder to hold the zipped gdb
    out_name (str): the gdb name  
    g (arcgis GIS): arcgis GIS instance logged in with read and write privilages
    title (str): a valid Feature service title
    folder_name (str): a valid folder name to sync to
    tag (str): a tag to apply to the contents when published
    return published_item (arcgis Item instance): the published item created.
    """
    make_archive(
        gdb_path, 
        'zip', 
        root_dir=out_folder_path,
        base_dir=out_name
    )
    arcpy.AddMessage("GDB compressed into zip for upload.")

    zip_path = gdb_path + '.zip'

    search_result = g.content.search(f'title:{title}', item_type='File Geodatabase')

    published_item = None

    if len(search_result) == 0:
        arcpy.AddMessage("No previous content with the same title has been found.")
        arcpy.AddMessage("A new feature service will be created.")
        g.content.create_folder(folder_name)

        arcpy.AddMessage("The destination folder has been created.")
        metadata = {"title":title}
        if tag:
            metadata['tag'] = tag

        item = g.content.add(
            item_properties= metadata, 
            data= zip_path,
            folder_name= folder_name
            )
        arcpy.AddMessage("GDB added to organization.")

        item.move(folder_name)
        arcpy.AddMessage("GDB item moved to target folder.")

        published_item = item.publish(file_type='fileGeodatabase')
        arcpy.AddMessage("New feature servicer published using GDB content.")

        published_item.move(folder_name)
        arcpy.AddMessage("Published feature service moved to target folder.")
        arcpy.AddMessage("Publishing of feature service complete.")
    else:
        item = search_result[0]
        metadata = {}
        item.update(
            item_properties= metadata, 
            data= zip_path
            )
        arcpy.AddMessage("Published GDB updated.")

        published_item = item.publish(file_type='fileGeodatabase',overwrite=True)
        arcpy.AddMessage("Feature service updated with new GDB content.")
        arcpy.AddMessage("Update of feature service complete.")
    return published_item


def validatePublishedTable(n_table_rows_source: int, published_item):
    """
    function to compare the number of rows in a source and a published tabel
    n_table_rows_source (int): the number of rows in the source
    published_item (arcgis Item): the arcgis item instance containing the table to validate.
    """
    arcpy.AddMessage("Starting published table validation process.")
    arcpy.AddMessage(f"Our source table data has {n_table_rows_source} rows.")
    n_table_rows_published = len(published_item.tables[0].query(as_df=True))
    arcpy.AddMessage(f"Our published table has {n_table_rows_published} rows.")
    if n_table_rows_source == n_table_rows_published:
        arcpy.AddMessage(f"All {n_table_rows_published} rows have been successfully published.")
    else:
        arcpy.AddWarning(f"Not all table rows have been published. We have {abs(n_table_rows_source - n_table_rows_published)} missing rows.")
    return


def validatePublishedFeatureClass(source_fc_path: str, published_item):
    """
    function to compare the number of rows in a source feature class and published feature service
    source_fc_path (str): path to source feature class
    published_item (arcgis Item): an arcgis Item instance that contains a feature service layer
    """
    n_fc_rows_source = len(GeoAccessor.from_featureclass(source_fc_path))
    arcpy.AddMessage(f"Our source feature class has {n_fc_rows_source} features.")
    n_fs_rows_published = len(published_item.layers[0].query(as_df=True))
    arcpy.AddMessage(f"Our published feature service layer has {n_fs_rows_published} features.")
    if n_fc_rows_source == n_fs_rows_published:
        arcpy.AddMessage(f"All {n_fs_rows_published} features have been successfully published.")
    else:
        arcpy.AddWarning(f"Not all featues have been published. We have {abs(n_fc_rows_source - n_fs_rows_published)} missing features.")
    arcpy.AddMessage("Validation complete.")
    return


def cleanAliasName(name):
    assert name, f"Error: {name} is not a valid field name."
    out = name[0] if name[0].isalpha() else ''
    for char in name[1:]:
        if char.isalnum() or char in {' ', '_'}:
            out = out + char
    assert out, "Error: not a valid clean alias name."
    return out


def cleanAliasNames(names):
    assert names, f"Error: {str(names)} is not a valid list of field names."
    
    for i, name in enumerate(names):
        names[i] = cleanAliasName(names[i])
    return names


def cleanFieldName(name):
    assert name, f"Error: {name} is not a valid field name."
    
    out = name[0] if name[0].isalpha() else ''
    for i, char in enumerate(name[1:]):
        if char.isalnum() or char in {'_'}:
            out = out + char
    assert out, f"Error: {out} is not a valid clean field name."
    return out


def cleanFieldNames(names):
    assert names, f"Error: {str(names)} is not a valid list of field names."
    
    for i, name in enumerate(names):
        names[i] = cleanFieldName(names[i])
    return names

