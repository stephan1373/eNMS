# Changelog

## Overview

The eNMS changelog is found under `System / Changelog`

![Filtering System.](../_static/system/changelog.png)

Changelog contains the following searchable information:

-   Object creation, deletion, and modification activity.
-   Running of services / workflows; when they ran, who ran them.
-   Various administration logs, such as database migration,
    parameter updates, etc.
-   Custom logs, defined by users in services / workflows.

## Object Changelogs

Some changelogs are linked to specific objects, detailing how they were created, updated, or deleted.
In the changelogs table, you can enable the "target type" and "target name" columns to see which object each changelog pertains to.

A change linked to a specific object can sometimes be reverted or undone. The "Revert" icon on the right side of the changelogs table allows you to do this. If the icon is greyed out, the "Revert" action is not available.

## Filtering changelogs

