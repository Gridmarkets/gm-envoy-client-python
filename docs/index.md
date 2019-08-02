# Introduction

GridMarkets Envoy client is Python library which enables users to upload project files, submit the project for processing and lookup status of submissions by interfacing with the Envoy service.

## Concepts

### Envoy

Envoy is a tool which end users install on their machines to manage project files uploaded to GridMarkets, watch and download results.

Envoy consists of a user interface portion and an underlying local web service typically running at `http://localhost:8090`. Both Envoy user interface and the Envoy client library uses the web service to interact with GridMarkets system.

When the user opens the Envoy user interface, Envoy web service will automatically get started and keeps running in the background.

### Project

A project defines a group of one or more jobs which need to be processed together.

### Job

Job defines the product type, version and other parameters required for processing the same in GridMarkets. A job will be always be defined with a project.

## Installation

The library is available as a universal [Wheel package](https://gm-envoy-client-docs.netlify.com/downloads/gridmarkets_envoy_client-0.7.0-py2.py3-none-any.whl) for Python 2.6, 2.7 and 3.3+. Users can install it using `pip` or `easy_install` as a global module or to a specific folder path to use and package with product plugins.

### Pre-requisites
This has dependency on Python [future](https://pypi.org/project/future) and [requests 2.x](https://pypi.org/project/requests/) libraries. When using `pip` or `easy_install`, dependencies are automatically installed.

### Using in Python 2.6, 2.7 and 3.3+

```bash
# Install as python global module
pip install https://gm-envoy-client-docs.netlify.com/downloads/gridmarkets_envoy_client-0.7.0-py2.py3-none-any.whl
```

```bash
# Install to a folder location to package with plugin
pip install https://gm-envoy-client-docs.netlify.com/downloads/gridmarkets_envoy_client-0.7.0-py2.py3-none-any.whl -t <plugin_lib_folder_path>
```

## User Credentials

GridMarkets account email and access key are required for authentication and use by the Envoy client library. Note that the access key is available in the user's profile page in the GridMarkets portal.

## Creating an Envoy client instance

```python
from gridmarkets import EnvoyClient

# create an instance of Envoy client
client = EnvoyClient(email="EMAIL_ADDRESS", access_key="ACCESS_KEY")
```

| Name          | Description                                                       |
| ------------- | ----------------------------------------------------------------- |
| EMAIL_ADDRESS | Email address of the registered GridMarkets account               |
| ACCESS_KEY    | Access key from the user's profile page in the GridMarkets portal |

## Discovering product types and supported product type plugins

Envoy client provides a product resolver which enables the user to do the following:

- Get the list of all product types and their supported plugins.
- Get the list of versions for a specific product type or plugin
- Get compatible combination for one or more product types and/or plugins

Every product and product plugin has an associated code and version to identify a specific product. Few examples below:

- `hou` represents a Houdini product type
- `hou_redshift` represents a Houdini Redshift plugin
- `hou:17.0.459` represents Houdini version 17.0.459

Above formats can be used to perform searches using the methods available in product resolver.

## Get all product types using product resolver

```python
from gridmarkets import EnvoyClient

# create an instance of Envoy client
client = EnvoyClient(email="EMAIL_ADDRESS", access_key="ACCESS_KEY")

# get product resolver
resolver = client.get_product_resolver()

# get all products
products = resolver.get_all_types()
```

### Response

```json
{
  "hou": { "versions": ["17.5.173", "17.5.229"], "is_plugin": false },
  "hou_redshift": { "versions": ["2.6.38", "2.6.39"], "is_plugin": true }
}
```

## Get the list of versions by product type or plugin type

```python
from gridmarkets import EnvoyClient

# create an instance of Envoy client
client = EnvoyClient(email="EMAIL_ADDRESS", access_key="ACCESS_KEY")

# get product resolver
resolver = client.get_product_resolver()

# get products for Houdini product type
qry = 'hou'
products = resolver.get_versions_by_type(qry)

# get products supporting Houdini Redshift plugin
qry = 'hou_redshift'
products = resolver.get_versions_by_type(qry)
```

### Response

```json
["14.0.395", "15.0.459"]
```

## Get compatible combination for a specific product type and version

```python
from gridmarkets import EnvoyClient

# create an instance of Envoy client
client = EnvoyClient(email="EMAIL_ADDRESS", access_key="ACCESS_KEY")

# get product resolver
resolver = client.get_product_resolver()

# get compatible combinations for a specific Houdini version
qry = ('hou:17.5.173')
products = resolver.get_compatible_combinations(qry)
```

### Response

```json
{
  "hou_redshift": {
    "versions": ["2.6.37", "2.6.38", "2.6.39"],
    "is_plugin": true
  },
  "htoa": { "versions": ["4.0.1", "4.0.2"], "is_plugin": true }
}
```

## Get compatible combination for one or more product type and versions

```python
# get compatible combinations for Houdini versions 17.5.173 and 17.5.229
qry = ('hou:17.5.173', 'hou:17.5.229')
products = resolver.get_compatible_combinations(qry)
```

### Response

```json
{
  "hou_redshift": {
    "versions": ["2.6.37", "2.6.38", "2.6.39"],
    "is_plugin": true
  }
}
```

Note that the queries can be one or more product types or the shortcode which is a combination of product type and version.

## Uploading and submitting project together

Uploading for files and submission of the project for processing can be done together by following the steps below. This will be the common and most used method to send the project for processing in GridMarkets.

### Create `EnvoyClient` instance

```python
from gridmarkets import EnvoyClient
from gridmarkets import Project
from gridmarkets import Job
from gridmarkets import WatchFile

# create an instance of Envoy client
client = EnvoyClient(email="EMAIL_ADDRESS", access_key="ACCESS_KEY")
```

### Create a project

```python
# create a project
# project files root folder path
project_path = "c:\\sample_project"

# name of the project is optional, if not passed inferred from the project root folder
project_name = "sample project"

# download output results to local path
# this is optional to be passed, if not passed, by default results will get downloaded under `gm_results` folder under project files path
results_download_path = "c:\\sample_project\\my_results"

project = Project(project_path, project_name, results_download_path)
```

### Add project files for upload

```python
# add files to project
# only files and folders within the project path can be added, use relative or full path
# any other paths passed will be ignored
project.add_files('sample.c4d', 'another_file.ext')
project.add_folders('assets')
```

### Add job

```python
# define the jobs
# create a Cinema4D job
job = Job(
  "test job", # job name
  "c4d", # product/app type
  "R19", # product type version
  "render", # operation
  "test/test.c4d", # job file to be run, note that the path is relative to the project name which is also the remote folder name
  frames="0 0 1", # rest are all job specific params
  output_height=600,
  output_width=400,
  output_format='tiff'
)

# add job to project
project.add_jobs(job)
```

### Add watch files to auto download results

```python
# setting watch files to auto download results
# Note that if watch files are not set, by default, results will get downloaded to `gm_results` folder under the project path.

# results regex pattern to download
# `project.remote_output_folder` provides the remote root folder under which results are available
# below is the regex to look for all folders and files under `project.remote_output_folder`
output_pattern = '{0}/.+'.format(project.remote_output_folder)

# download path
download_path = 'c:\\sample_project\my_results'

# create a watch file
watch_file = WatchFile(output_pattern, download_path)

# add watch files, this will auto download results to the defined `download_path`
project.add_watch_files(watch_file)
```

### Submit project

```python
# submit project
resp = client.submit_project(project) # returns project name
```

## Uploading project files

There are cases where users might want to upload files and then run multiple submission based on the already uploaded files. The code below details the step to upload project files.

### Create `EnvoyClient` instance

```python
from gridmarkets import EnvoyClient
from gridmarkets import Project
from gridmarkets import WatchFile

# create an instance of Envoy client
client = EnvoyClient(email="EMAIL_ADDRESS", access_key="ACCESS_KEY")
```

### Add project files to upload

```python
# create a project
# project files root folder path
project_path = "c:\\sample_project"

# name of the project is optional, if not passed inferred from the project root folder
project_name = "sample project"

project = Project(project_path, project_name)

# add files to project
# only files and folders within the project path can be added, use relative or full path
# any other paths passed will be ignored
project.add_files('sample.c4d', 'another_file.ext')
project.add_folders('assets')
```

### Upload project files

```python
# upload files project
response = client.upload_project_files(project) # returns project name
```

## Submitting a project skipping upload of files

As indicated in the prior section, users can perform multiple submissions with different parameters based on the already uploaded files. Note that all project files should be available in GridMarkets system for running jobs successfully. Follow the steps below to submit a project for processing in GridMarkets system.

### create `EnvoyClient` instance

```python
from gridmarkets import EnvoyClient
from gridmarkets import Job

# create an instance of Envoy client
client = EnvoyClient(email="EMAIL_ADDRESS", access_key="ACCESS_KEY")
```

### Create a project

```python
# create a project
# User will need to create the project but does not need to add files or folders for just submission without uploading of files
# project files root folder path
project_path = "c:\\sample_project"

# name of the project is optional, if not passed inferred from the project root folder
project_name = "sample project"

project = Project(project_path, project_name)
```

### Add job

```python
# define the jobs
# create a Cinema4D job
job = Job(
  "test job", # job name
  "c4d", # product type
  "R19", # product version
  "render", # operation
  "{0}/sample.c4d".format(project_name), # job file to be run, note that the path is relative to the project name which is also the remote folder name
  frames="0 0 1", # rest are all job specific params for the Cinema4D job type
  output_height=600,
  output_width=400,
  output_format='tiff'
)

# add job to project
project.add_jobs(job)
```

### Add watch files to auto download results

```python
# setting watch files to auto download results
# Note that if watch files are not set, by default, results will get downloaded to `gm_results` folder under the project path.

# results regex pattern to download
# `project.remote_output_folder` provides the remote root folder under which results are available
# below is the regex to look for all folders and files under `project.remote_output_folder`
output_pattern = '{0}/.+'.format(project.remote_output_folder)

# download path
download_path = 'c:\\sample_project\my_results'

# create a watch file
watch_file = WatchFile(output_pattern, download_path)

# add watch files, this will auto download results to the defined `download_path`
project.add_watch_files(watch_file)
```

### Submit Project by skipping upload

```python
# submit project
skip_upload = True
client.submit_project(project, skip_upload)
```

## Submitting a project with job dependencies

Users can setup inter-job dependencies to enable GridMarkets system to pipeline the job processing accordingly.

```python
job1 = Job(...)
job2 = Job(...)
job3 = Job(...)

# setting up job1 and job2 as dependencies to job3
# GridMarkets system will process job1 and job2 followed by job3.
job3.add_dependencies(job1, job2)
```

## Fetching status of the project

```python
from gridmarkets import EnvoyClient

# create an instance of Envoy client
client = EnvoyClient(email="EMAIL_ADDRESS", access_key="ACCESS_KEY")

# project name
project_name = "sample project"

resp = client.get_project_status(project_name)
```

### Response

```json
{
  "Code": 200,
  "State": "Uploading",
  "Message": "File uploads in progress.",
  "BytesDone": 0,
  "BytesTotal": 2971998,
  "Details": {
    "/sample project/test.c4d": {
      "Name": "/sample project/test.c4d",
      "State": "Uploading",
      "BytesDone": 0,
      "BytesTotal": 2971998,
      "Speed": 0
    }
  },
  "Speed": 0
}
```

```json
{
  "Code": 200,
  "State": "Submitted",
  "Message": "Job submission successful.",
  "BytesDone": 2971998,
  "BytesTotal": 2971998,
  "Details": {
    "/sample project/test.c4d": {
      "Name": "/sample project/test.c4d",
      "State": "Completed",
      "BytesDone": 2971998,
      "BytesTotal": 2971998,
      "Speed": "0.00"
    }
  },
  "Speed": 0
}
```

## Error handling
This section outlines the possible error/exceptions thrown by `EnvoyClient` while instantiating and calling the methods on it. It is always a good idea to wrap the instantiation and call to `EnvoyClient` functions within a `try... except..` block.

### AuthenticationError 
This exception is thrown when user credentials are incorrect.

```python
from gridmarkets import EnvoyClient
from gridmarkets import AuthenticationError

try:
  # create an instance of Envoy client
  client = EnvoyClient(email="EMAIL_ADDRESS", access_key="ACCESS_KEY")

  # get product resolver
  resolver = client.get_product_resolver()

  # get all products
  products = resolver.get_all_types()

  # any other calls on Envoy client
except AuthenticationError as e:
  # handle the exception pertaining to AuthenticationError
```

### InsufficientCreditsError
```python
from gridmarkets import EnvoyClient
from gridmarkets import Project
from gridmarkets import Job
from gridmarkets import InsufficientCreditsError

try:
  # create an instance of Envoy client
  client = EnvoyClient(email="EMAIL_ADDRESS", access_key="ACCESS_KEY")

  # create the project and add jobs
  project = Project(...)

  # submit project
  # you can submit project only if the user has positive credits
  # otherwise InsufficientCreditsError error is thrown
  client.submit_project(project)  

  # any other calls on Envoy client
except InsufficientCreditsError as e:
  # handle the exception pertaining to InsufficientCreditsError
```

### InvalidRequestError
```python
from gridmarkets import EnvoyClient
from gridmarkets import Project
from gridmarkets import Job
from gridmarkets import InvalidRequestError

try:
  # create an instance of Envoy client
  client = EnvoyClient(email="EMAIL_ADDRESS", access_key="ACCESS_KEY")

  # create a project and add jobs
  project = Project(...)

  # submit project
  # If project params are incorrect or if some params are missing then InvalidRequestError is raised
  client.submit_project(project)  

  # any other calls on Envoy client
except InvalidRequestError as e:
  # handle the exception pertaining to InvalidRequestError
```

### APIError
This is a generic error/exception thrown when `EnvoyClient` is not able to communicate with Envoy service or any other errors.

```python
from gridmarkets import EnvoyClient
from gridmarkets import APIError

try:
  # create an instance of Envoy client
  client = EnvoyClient(email="EMAIL_ADDRESS", access_key="ACCESS_KEY")

  # get product resolver
  resolver = client.get_product_resolver()

  # get all products
  products = resolver.get_all_types()

  # any other calls on Envoy client
except ApIError as e:
  # handle the exception pertaining to APIError
```

### All exceptions in try..catch.. block
```python
from gridmarkets import EnvoyClient
from gridmarkets import Project
from gridmarkets import Job
from gridmarkets import *

try:
  # create an instance of Envoy client
  client = EnvoyClient(email="EMAIL_ADDRESS", access_key="ACCESS_KEY")

  # create a project and add jobs
  project = Project(...)

  # submit project
  # If project params are incorrect or if some params are missing then InvalidRequestError is raised
  client.submit_project(project)  

  # any other calls on Envoy client
except AuthenticationError as e:
  # handle the exception pertaining to AuthenticationError
except InsufficientCreditsError as e:
  # handle the exception pertaining to InsufficientCreditsError
except InvalidRequestError as e:
  # handle the exception pertaining to InvalidRequestError
except ApIError as e:
  # handle the exception pertaining to APIError
```

## Getting package version
Use the code below to get the current package version
```python
from gridmarkets import EnvoyClient

client = EnvoyClient(email="EMAIL_ADDRESS", access_key="ACCESS_KEY")

print(client.version)
```

## Validating authentication
For some cases like usage within a plugin, you would want to explicitly validate whether the user credentials are valid. You can use the code below to validate authentication

```python
from gridmarkets import EnvoyClient

client = EnvoyClient(email="EMAIL_ADDRESS", access_key="ACCESS_KEY")

try:
  is_auth_valid = client.validate_auth()
except AuthenticationError as e:
  # handle exception, this means that the user credentials are not valid
```

## Validating user credits
For some cases like usage within a plugin, you would want to explicitly validate user credits. You can use the code below.

```python
from gridmarkets import EnvoyClient

client = EnvoyClient(email="EMAIL_ADDRESS", access_key="ACCESS_KEY")

try:
  is_valid_credits = client.validate_credits()
except InsufficientCreditsError as e:
  # handle exception, this means that the user credits is not positive
```

## Cinema4D job

```python
from gridmarkets import Job

job = Job(
  JOB_NAME, # job name
  PRODUCT_TYPE, # product type
  PRODUCT_VERSION, # product version
  OPERATION, # operation
  RENDER_FILE, # job file to be run, note that the path is relative to the project name which is also the remote folder name
  frames=FRAMES, # rest are all job specific params
  output_height=OUTPUT_HEIGHT,
  output_width=OUTPUT_WIDTH,
  output_prefix=OUTPUT_PREFIX,
  output_format=OUTPUT_FORMAT
)

```

| Name     | Type   | Description                                           |
| -------- | ------ | ----------------------------------------------------- |
| `JOB_NAME` | `string` | Job name is the first argument passed to Job instance |
| `PRODUCT_TYPE` | `string` | `c4d` should be passed for Cinema4D
| `PRODUCT_VERSION` | `string` | Supported Cinema4D version should be passed fetched via product resolver |
| `OPERATION` | `string` | `render` is the only supported operation |
| `RENDER_FILE` | `string` | Path to `.c4d` file expressed relative to the remote project folder. If your project name is `sample_project` then remote root becomes `/sample project`. Render file path example is `/sample project/sample.c4d` |
| `FRAMES` | `string` | Defines the frame range in format `start [end] [step],[start [end] [step]],...` |
| `OUTPUT_WIDTH` | `number` | Defines the render output file width |
| `OUTPUT_HEIGHT` | `number` | Defines the render output file height |
| `OUTPUT_PREFIX` | `string` | Defines the render output file prefix |
| `OUTPUT_FORMAT` | `string` | Defines the render output file format |

<!-- ## MOE job

```python
from gridmarkets import Job

job = Job(
  JOB_NAME, # job name
  PRODUCT_TYPE, # product type
  PRODUCT_VERSION, # product version
  OPERATION, # operation
  SVL_FILE, # job file to be run, note that the path is relative to the project name which is also the remote folder name
  output_file=OUTPUT_FILE
)

```

| Name     | Type   | Description                                           |
| -------- | ------ | ----------------------------------------------------- |
| `JOB_NAME` | `string` | Job name is the first argument passed to Job instance |
| `PRODUCT_TYPE` | `string` | `moe` should be passed for MOE
| `PRODUCT_VERSION` | `string` | Supported MOE version should be passed fetched via product resolver |
| `OPERATION` | `string` | `simulation` is the only supported operation |
| `SVL_FILE` | `string` | Path to `.svl` input file expressed relative to the remote project folder. If your project name is `sample_project` then remote root becomes `/sample project`. Render file path example is `/sample project/sample.svl` |
| `OUTPUT_FILE` | `string` | Defines the output file. `sample.mdb` is an example | -->

## V-Ray job

```python
from gridmarkets import Job

job = Job(
  JOB_NAME, # job name
  PRODUCT_TYPE, # product type
  PRODUCT_VERSION, # product version
  OPERATION, # operation
  RENDER_FILE, # job file to be run, note that the path is relative to the project name which is also the remote folder name
  frames=FRAMES, # rest are all job specific params
  output_height=OUTPUT_HEIGHT,
  output_width=OUTPUT_WIDTH,
  output_prefix=OUTPUT_PREFIX,
  output_format=OUTPUT_FORMAT
)

```

| Name     | Type   | Description                                           |
| -------- | ------ | ----------------------------------------------------- |
| `JOB_NAME` | `string` | Job name is the first argument passed to Job instance |
| `PRODUCT_TYPE` | `string` | `vray` should be passed for V-Ray
| `PRODUCT_VERSION` | `string` | Supported V-Ray version should be passed fetched via product resolver |
| `OPERATION` | `string` | `render` is the only supported operation|
| `RENDER_FILE` | `string` | Path to `.vrscene` file expressed relative to the remote project folder. If your project name is `sample_project` then remote root becomes `/sample project`. Render file path example is `/sample project/sample.vrscene` |
| `FRAMES` | `string` | Defines the frame range in format `start [end] [step],[start [end] [step]],...` |
| `OUTPUT_WIDTH` | `number` | Defines the render output width |
| `OUTPUT_HEIGHT` | `number` | Defines the render output height |
| `OUTPUT_PREFIX` | `string` | Defines the render output file prefix |
| `OUTPUT_FORMAT` | `string` | Defines the render output format |

## Houdini Job

### Project level parameters

```python
# create a project
project = Project(SRC_PATH, PROJECT_NAME,
    project_summary_log_file=PROJECT_SUMMARY_LOG_FILE,
    project_param_output=PROJECT_PARAM_OUTPUT,
    project_param=PROJECT_PARAM,
    project_env=PROJECT_ENV)
```

Project level parameters are common and shared across all jobs in the project.

| Name     | Type   | Description                                           |
| -------- | ------ | ----------------------------------------------------- |
| `PROJECT_SUMMARY_LOG_FILE` | `string` | Defines the path of the summary log files generated by Houdini plugin |
| `PROJECT_PARAM_OUTPUT` | `list` | Defines the list of project output parameters |
| `PROJECT_PARAM` | `dict` | Defines the project output parameter mappings |
| `PROJECT_ENV` | `dict` | Defines the project level environment variable mappings |
| `PROJECT_PARAM` | `dict` | Defines the project parameters |


### Job level parameters

```python
# create Houdini job
job = Job(
  JOB_NAME, 
  "PRODUCT_TYPE, 
  PRODUCT_VERSION, 
  OPERATION,
  RENDER_FILE,
  PLUGINS,
  frames=FRAMES,
  take=TAKE,
  rop_nodetype=ROP_NODE_TYPE,
  rop_nodepath=ROP_NODE_PATH,
  output_upload=OUTPUT_UPLOAD,
  disk_output_ext=DISK_OUTPUT_EXT,
  disk_output_mode=DISK_OUTPUT_MODE,
  disk_output_parm=DISK_OUTPUT_PARM,
  disk_output_path=DISK_OUTPUT_PATH,
  disk_output_renderer=DISK_OUTPUT_RENDERER,
  disk_output_path_parm=DISK_OUTPUT_PATH_PARM
  gpu=GPU)
```

| Name     | Type   | Description                                           |
| -------- | ------ | ----------------------------------------------------- |
| `JOB_NAME` | `string` | Job name is the first argument passed to Job instance. |
| `PRODUCT_TYPE` | `string` | `hou` should be passed for Houdini.;
| `PRODUCT_VERSION` | `string` | Supported Houdini version should be passed fetched via product resolver. |
| `OPERATION` | `string` (optional) | `render`, `batch` are supported operations. Default is `render` if this parameter is not passed.|
| `RENDER_FILE` | `string` | Path to `.hip`, `.hipnc`, `.hiplc` file expressed relative to the remote project folder. If your project name is `sample_project` then remote root becomes `/sample project`. Render file path example is `/sample project/sample.hip`. |
| `PLUGINS` | `list` | Defines the list of plugins required for the job. Example: `['hou_redshift']` defines the Houdini Redshift plugin to be required for processing job.|
| `FRAMES` | `string` | Defines the frame range in format `start [end] [step],[start [end] [step]],...` |
| `ROP_NODE_TYPE` | `string` | Defines the render operation node type. |
| `ROP_NODE_PATH` | `string` | Defines the render operation node path.|
| `OUTPUT_UPLOAD` | `list` | Defines the output pattern to be uploaded to long time storage (LTS). |
| `DISK_OUTPUT_EXT` | `string` (optional) | Defines the disk output extension. |
| `DISK_OUTPUT_MODE` | `string` (optional) | Defines the disk output mode. |
| `DISK_OUTPUT_PARM` | `string` (optional) | Defines the disk output parameter. |
| `DISK_OUTPUT_PATH` | `string` (optional) | Defines the disk output path. |
| `DISK_OUTPUT_RENDERER` | `string` (optional) | Defines the disk output renderer. |
| `DISK_OUTPUT_PATH_PARM` | `string` (optional) | Defines the disk output path parameter. |
| `GPU` | `bool` (optional) | Defines if a GPU is required for running the job. |


## Nuke job

```python
# create Nuke job
job = Job(
  JOB_NAME, 
  "PRODUCT_TYPE, 
  PRODUCT_VERSION, 
  OPERATION,
  RENDER_FILE,
  PLUGINS,
  frames=FRAMES
```

| Name     | Type   | Description                                           |
| -------- | ------ | ----------------------------------------------------- |
| `JOB_NAME` | `string` | Job name is the first argument passed to Job instance. |
| `PRODUCT_TYPE` | `string` | `nuke` should be passed for Nuke.;
| `PRODUCT_VERSION` | `string` | Supported Nuke version should be passed fetched via product resolver. |
| `OPERATION` | `string` (optional) | `render` is the only supported operations. Default is `render` if this parameter is not passed.|
| `RENDER_FILE` | `string` | Path to `.nk` file expressed relative to the remote project folder. If your project name is `sample_project` then remote root becomes `/sample project`. Render file path example is `/sample project/sample.nk`. |
| `FRAMES` | `string` | Defines the frame range in format `start [end] [step],[start [end] [step]],...` |


## Blender job

```python
from gridmarkets import Job

job = Job(
  JOB_NAME, # job name
  PRODUCT_TYPE, # product type
  PRODUCT_VERSION, # product version
  OPERATION, # operation
  RENDER_FILE, # job file to be run, note that the path is relative to the project name which is also the remote folder name
  frames=FRAMES, # rest are all job specific params
  output_prefix=OUTPUT_PREFIX,
  output_format=OUTPUT_FORMAT,
  engine=RENDER_ENGINE # optional param
)

```

| Name     | Type   | Description                                           |
| -------- | ------ | ----------------------------------------------------- |
| `JOB_NAME` | `string` | Job name is the first argument passed to Job instance |
| `PRODUCT_TYPE` | `string` | `blender` should be passed for Blender
| `PRODUCT_VERSION` | `string` | Supported Blender version should be passed, fetched via product resolver |
| `OPERATION` | `string` | `render` is the only supported operation|
| `RENDER_FILE` | `string` | Path to `.blend` file expressed relative to the remote project folder. If your project name is `sample_project` then remote root becomes `/sample project`. Render file path example is `/sample project/sample.blend` |
| `FRAMES` | `string` | Defines the frame range in format `start [end] [step],[start [end] [step]],...` |
| `OUTPUT_PREFIX` | `string` | Defines the render output file prefix |
| `OUTPUT_FORMAT` | `string` | Defines the render output format |
| `RENDER_ENGINE` | `string` (optional) | Defines the render engine to be used |