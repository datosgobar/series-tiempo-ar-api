# elastic_spike contribution guide

## Submitting code

All the code submitted to the project must be associated with an issue.

If you need to do something and there's no issue for it, you should ask the team lead to create an issue for it or create it yourself.

When working on an issue, you must create a feature branch (by clicking on the "New branch" button), submit code to the branch, and then submit a merge request on gitlab.

## Issue kinds

To categorize issues we use labels. There are four kinds of issues:

* feature: Coarse-grained functionaities of the application.
* task: Fine-grained functionalities that together build up a feature.
* bug: bugs dscovered by devartis' team.
* bugUAT: bugs discovered by the customer's team.

## Internationalization

All external strings must be internationalized using `ugettext_lazy` or `{% trans %}`.
