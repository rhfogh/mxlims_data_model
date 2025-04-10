# mxlims_data_model
Data model / API for crystallography LIMS data
==============================================

Introduction
------------

The purpose of this project is to develop a data model describing the structure of scientific data needed for macromolecular crystallography. The data model can then be used to define an API for ingesting/storing/retrieving such data, for interaction with programs like beamline control systems, and for structuring viewers.

Initially this is an exploratory, developer-led, low-key endeavour. The first task it to find out what is already available, particularly from the participating developers. The second task is to agree on a data model that can represent and structure the relevant data. As a matter of professsionalism the model should of course be precisely defined, well structured, able to deal with predictable complications, capable of extension, etc. but the most important need at the beginning is to produce something that is useful in the relatively short term. This result might then later be formalised into a standard (or several), generalised, and/or ported to different formats etc, but it important that these aspects should *not* impede development at the start.

The main purpose of the model is to structure APIs rather than to serve as a basis for program internals (where each program might have its own specific needs). A well-defined model of the structure inherent in crystallography data would serve to structure data exchange between programs, and to specify a minimal degree of structure that any program wishing to collaborate would have to support. There are several known use cases that this model should address. 

  - MXCuBE has an immediate requirement for an abstract LIMS interface, to structure the data passed between MXCuBE and multiple LIMS systems.
  - Several participating developers already have aplications that make use of a similar structure, and would have interest in this being broadened to a more generally supported format.
  - The ISPyB collaboration is (in part) being reorganised around ICAT, and needs a data model to structure the metadata that are going to be stored within the (fairly high-level) ICAT objects. Other parts of ISPyB are considering other architectures, but an agreement at the level of data structure / API could allow a degree of collaboration that might otherwise be difficult to achieve.

Note that in the interest of smooth working, there is no obligation at the start for all participants to sign up to using the result of the exercise.
