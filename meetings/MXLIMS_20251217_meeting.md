1.  MXLIMS web meeting

## Participants

Kate Smith, Daniel Ericsson (ANSTO)

Jose Brandao-Neto (Diamond)

Rasmus Fogh, Gerard Bricogne (Global Phasing)

Ezequiel Panepucci (MAX IV)

May Sharpe, Dennsi Stegmann (SLS)

## 

## Status

**RF**: MXLIMS has a complete model for single-crystal MX experiments
and processing. It is still being improved, which likely will continue
until it is implemented. The plan was for the next step to be a
proof-of-principle test passing a shipment MXLIMS document to a
synchrotron, ingesting it, and passing back an MXLIMS document with the
results, but this has not yet proved possible.

**DS, MS**: Shipment files for past projects to multiple synchrotrons
are ready for test runs, as it code for generating them. Apart from some
running improvements this is ready. Ingestion of results has not been
started. SLS generally reads back only raw data and runs the processing
in-house. SLS has a couple of new fragment screening shipments coming up
in 2026 that could be shipped to MAX IV and double as MXLIMS tests.

**EP**: MAX IV is still interested in runniong an MXLIMS test, but their
ISPyB developer is currently required on a different project. There are
rumours that he might become free by end January 2026. For now all that
can be done is to convert MXLIMS to csv files, which would still have to
be loaded in manually. MAX IV is now ingesting data into SciCAT.

**ED**: IceBear is ready to generate MXLIMS files for several
synchrotrons. Work on sending back results this would have to wait for
an MXLIMS file with the results to work on. Currently IceBear accesses
synchrotrons by interacting as a fake user -- which is a complex and
fragile arrangement.

J**B-N** is beamline scientist on DLS I04 and working on the upcoming
K04 which will be running ultra-high-throughput experiments. MXLIMS is
of interest as the high throughput on K04 will require well-organised
data handling to deal with the flood of data.

**KS, DE**: ANSTO has their new MX3 beamline up and running now, which
has taken all their energies until recently. There is a brand new
database structure also built. They are now interested in trying to
cross-pollinate and join into standards.

Guilherme de Freitas (DLS) could not make the meeting, but has made some
interesting contributions to the project model and plans. RF reported
that he was proposing a system where each synchrotron had a url with
standard structure so that you could interact programmatically and query
e.g. shipping requirements specification, projects for a user, sessions
for a project, an access token, ...

# Processed data

There was a discussion on the best way of handling processed data, in
the expectation that it might be possible to move ahead on preparing for
this while waiting for a shipping test. Ideally this should be done
upstream, by the synchrotrons. DLS, for instance, already have in-house
software to extract comparable data from the various pipelines they run.
One problem with this idea is that it depends entirely on the active
collaboration of resource-strapped synchrotrons. An alternative would be
to do this in the processing programs (e.g. autoPROC), but, again, this
would depend on cooperation between a number of often synchrotron-linked
developers. Another alternative would be to set up an application that
could re-calculate and extract the relevant metadata from processing
results, i.e. MTZ files. ANSTO has a program that starts with scaled,
unmerged data in MTZ files and uses ccTBX functions to recalculate
quality control metadata in a uniform manner. The GPhL program MRFANA
does something similar. Providing an application that synchrotrons (or
downstream users) could use to calculate and fill in the relevant values
for an MXLIMS file might speed up the uptake of MXLIMS and help produce
more complete metadata. The issue will be taken under advisement for the
next core MXLIMS meeting.

# MXLIMS model

RF raised a question of MXLIMS modeling details, specifically the best
way to model attributes like protein and DNA sequences, SMILES strings
(or alternatives) etc. which should no longer be kept in a data bucket
marked 'identifiers' as in the current model version. The question is
less critical, as shipments to and from synchrotrons generally do not
add much of this kind of information -- for confidentiality reasons.
Still, these data should be supported in the model for those who need
them, and for use in final deposition. From now some straightforward
modelling should do, with help from the schemas used in fragment
screening. Here RF already has the relevant SLS schema, and hopes for a
copy of the DLS one as well.

# Plans

The most imminent goal is to run a test of shipping, ingestion and
shipping back results using MXLIMS. The only synchrotron that is (close
to) ready at the moment is MAX IV, and it is hoped to do the test as
soon as developer resources become available. SLS proposes to coordinate
this with a new shipment of fragment screening crystals. JB-N and
(hopefully) Guilherme de Freitas will investigate the possibilities for
running a test at Diamond

Testing on returning acquisition and processing results will have to
wait till a shipping test has generated some results. In the meantime
all participants are asked to contribute relevant information on how
they repatriate data and extract data from various processing programs.

There is some model change work going on at the moment, based on input
from ED and Guilherme, mainly. RF plans on completing this, and
producing it with documentation, a rough MXCuBE export implementation,
example files and diagrams to be ready before a new test can be set up.
