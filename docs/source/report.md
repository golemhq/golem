Report
==================================================

## Generate Reports After Execution

Different reports can be generated after the execution of a suite.

### Report Types

The options are:

* html 
* html-no-images
* json
* junit

Example:
```bash
golem run project suite -r junit html html-no-images json
```

### Report Location

By default the reports are generated in ```/<testdir>/projects/<project>/reports/<suite>/<timestamp>```

The location of the reports can be modified with the --report-folder argument:

```bash
golem run project suite -r html --report-folder /the/path/to/the/report
```

### Report Name

By default the report name is 'report' ('report.xml' for *junit* reports, 'report.html' and 'report-no-images.html' for *html* reports)

The name of the reports can be modified with the --report-name argument:

```bash
golem run project suite -r html --report-name report_name
```

### JSON Report

The JSON report is always generated in the default location with the name 'report.json'.
It can be generated in a different location or with a different name by specifying the options explained above. 

## Modify Screenshot Format, Size, and Quality

The size and compression of the screenshots can be modified to reduce the size on disk.

For example:

When a screenshot with default settings (PNG image, no resize, no compression) takes ~**149kb** on disk.

Applying the following settings:

```JSON
{
    "screenshots": {
        "format": "jpg",
        "quality": 50,
        "resize": 70
    }
}
```

The new screenshot file takes ~**35kb**.

Experiment to find optimum settings. More info on screenshot manipulation [here](settings.html#screenshots).
