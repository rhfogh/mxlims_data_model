## Changes in version 0.6.7

- ExperimentData.priority added
- PinData.loopType added (NB should be made enum)
- PinData.holderLength added
- Puck.positionInDewar added
- Moved acronym from MacromoleculeSample to LogisticalSample
- Renamed MxExperiment.spaceGroupName to selectedSpaceGroupName
- Renamed MxExperiment.unitCell to selectedUnitCell
- Fixed field generation script to deal with overridden fields and 'annotation'
- Removed duplicate 'annotation' fields from subclasses
- Added docs/examples/mapping<version>.xlsx file
- Removed 'no-added-properties' from objects to avoid document breakage
- Refactored handling of numerical types (e.g. minimum 1->exclusiveMinimum 0)
  and list types, and changed code generation to improve Pydantic type annotations

## Changes in version 0.6.6

- Added rough-and-ready field list generation script
- Harmonised use of allOf in datatype attributes
- Corrected error in ReflectionSet.resolutionCutoffs and added new Datatype
- bug fix in missing 'array' type

# Changes in version 0.6.5

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