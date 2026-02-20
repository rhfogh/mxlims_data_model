#  Known Issues

## Version 0.6.11

- The Pydantic code generation machinery has some bugs that cause incorrect
  import statements in a few rare cases. These have to be fixed by hand after 
  generation, before check-in. They appear in MxlimsMessageStrict.py,
  ReflectionSetData.py and VolumeScanData.py.
- The constraints in ShipmentMessage.json are not carried over into ShipmentMessage.py
  so that seemingly valid Pydantic structures for this class may not convert to 
  valid JSON. 
