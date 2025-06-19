## Changes in version 0.6.5

- Renamed PreparedSample to Sample
- Added LogisticalSample.name
- Added MxExperiment.experimentLocation  # (e.g. 'SOLEIL PX2')
- Put 'annotations' field into all objects, replacing 'comments'
- Added Puck.puck_type - so far just a string, an enum needs to be defined
- Added Sample.campaign_name
- Added MxExperiment.required_resolution
- Changed SampleComponent.role to enum, values are 'solvent', 'cryoprotectant', 'ligand', 'cofactor', 'buffer', 'target', 'other'
- Added ReflectionSet.twin_fraction and .possible_twinning
- Renamed ReflectionSet.unit_cell to .refined_unit_cell
- Added RFC4122-compliant Regex to all fields with `"format": "uuid"`
- Reorganised use of `additionalProperties": false` to appear only in classes that are not inherited
- Changed ReflectionStatistics and .resolution_cutoff from list of keyword-value pairs to a simple dictionary
- Added draft mapping files MXLIMS <--> shipping spreadsheet to docs/examples