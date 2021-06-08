Report
==================================================

## Default Report

When an execution is run a JSON report is generated in this location:

```
<golem_dir>/projects/<project_name>/reports/<execution_name>/<timestamp>/report.json
```

## Generate Reports After Execution

These are the available report types:

* html (single html file, screenshots included)
* html-no-images (single html file, without screenshots)
* json
* junit (XML compatible with Jenkins)

Example:
```
golem run project suite -r junit html html-no-images json
```

### Report Location

The location of the reports can be specified with the --report-folder argument:

```
golem run project suite -r html --report-folder /the/path/to/the/report
```

### Report Name

By default, the report name is 'report' ('report.xml', 'report.html', 'report-no-images.html' and 'report.json')

The name of the reports can be modified with the --report-name argument:

```
golem run project suite -r html --report-name report_name
```

## Modify Screenshot Format, Size, and Quality

The size and compression of the screenshots can be modified to reduce the size on disk.

For example:

Given the default settings (PNG image, no resize, no compression), a screenshot was ~**149kb**.

When these settings were applied:

```JSON
{
    "screenshots": {
        "format": "jpg",
        "quality": 50,
        "resize": 70
    }
}
```

Then the same screenshot takes ~**35kb**.

Experiment to find optimum settings. More info on screenshot formatting [here](settings.html#screenshots).
