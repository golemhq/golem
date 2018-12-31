Report
==================================================

## Modify Screenshot Format, Size, and Quality 

This helps reduce the size on disk of the generated screenshots and reports.

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
