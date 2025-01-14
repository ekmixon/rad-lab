# How to Contribute

We'd love to accept your patches and contributions to this project. There are
just a few small guidelines you need to follow.

## Contributor License Agreement

Contributions to this project must be accompanied by a Contributor License
Agreement. You (or your employer) retain the copyright to your contribution;
this simply gives us permission to use and redistribute your contributions as
part of the project. Head over to <https://cla.developers.google.com/> to see
your current agreements on file or to sign a new one.

You generally only need to submit a CLA once, so if you've already submitted one
(even if it was for a different project), you probably don't need to do it
again.

## Repository Structure

The project has the following file structure:
- [/docs](../docs): Documentation about the repository.
- [/modules](../modules): Customisable modules to create Google Cloud Platform infrastructure.
- [/scripts](../scripts): RAD-Lab Installer and additional scripts to support the modules.

Every individual module is contained in it subdirectory and should follow these Terraform guidelines:

- Create at least a `versions.tf`, `main.tf`, `variables.tf` and `outputs.tf`.  It's ok to create additional files, to split resources between files and give them more meaningful names. 

NOTE: Make sure all the variables are in alphabetical order in `variables.tf`

- A README.md containing more information about the modules, required IAM permissions and any specific instructions to create the infrastructure.

NOTE: Add below 2 tags in the RAD-Lab module specific README.md for populating structured Variables and Outputs automatically via [tfdoc.py](../tools/tfdoc.py).

```
<!-- BEGIN TFDOC -->
<!-- END TFDOC -->
```

For every module, a base configuration is determined, which can be installed via the [radlab.py](../scripts/radlab-installer/README.md) installer.  The base configuration is reflected in the default values for all the variables, except for `organization_id`, `billing_account_id` and (optional) `folder_id`. 

## Installer
It should be possible for people with less experience in Infrastructure As Code to use every module.  The repository contains an installer for that purpose, which can be found in the [/scripts](../scripts) directory ([radlab.py](../scripts/radlab-installer/radlab.py)).  The installer needs to be updated whenever new modules are introduced to the repository.

## Cloud Foundation Toolkit
Where possible, use the open source [Cloud Foundation Toolkit](https://cloud.google.com/foundation-toolkit) modules to create Google Cloud infrastructure.

## Code Reviews

All submissions, including submissions by project members, require review. We use GitHub pull requests for this purpose. 
NOTE: Create a **seperate pull request** for every module you create or update. Do not include changes of multiple modules in the same pull request.  

Consult [GitHub Help](https://help.github.com/articles/about-pull-requests/) for more information on using pull requests.

## Community Guidelines

This project follows [Google's Open Source Community Guidelines](https://opensource.google/conduct/).