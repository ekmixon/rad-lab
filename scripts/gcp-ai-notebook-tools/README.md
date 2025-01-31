# Google cloud desktop script - ai notebook launch tool

## Overview

 A simple shell script for your desktop to `start | stop | status | url | describe`  AI Notebooks on Google Cloud

 pre-requisites would be to have `gcloud` setup with a GCP project configured already. Ref [Doc](https://cloud.google.com/sdk/docs/install)

`AI notebook API` needs to be enabled as well.

## Access RAD Lab Modules

1. Data Science RAD Lab Users will be provided a [Bash script](https://github.com/GPS-Demos/radlab/blob/312e841c4062c91b9450ad534623531f4f5d6f9f/gcp-ai-notebook-tools/ai-notebook-desktop-script.sh) - `ai-notebook-desktop-script.sh` which they can run on their cloudshell or localhost  terminals to fetch the Proxy URIs of the Notebooks Instance.

2. Navigate to the directory where the bash script is downloaded.

3. Update line 25 - 27 of `ai-notebook-desktop-script.sh` script based on the information provided by the _Cloud Admin_ in step 12 under [RADLab Readme](https://github.com/GPS-Demos/radlab/blob/bd749828f7fb105ed5d76f4f813c35a2bdce2d3a/README.md).
```
export INSTANCE_NAME="AI_NOTEBOOK_INSTANCE_NAME"
export PROJECT="PROJECT_ID"
export LOCATION="ZONE"
.
.
```

4. Execute the Bash script by running : 

    * `sh ai-notebook-desktop-script.sh` on Unix console or Mac terminal.
    *  Follow these [instructions](https://www.howtogeek.com/261591/how-to-create-and-run-bash-shell-scripts-on-windows-10/) for Windows 10.