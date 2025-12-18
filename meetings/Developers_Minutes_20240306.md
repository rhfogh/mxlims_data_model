## Participants

-   Rasmus Fogh, Peter Keller, Clemens Vonrhein (Global Phasing)

-   Kate Smith, Ezequiel Panepucci (Swiss Light Source)

-   Karl Levik, James Hall, (Diamond Light Source)

-   Daniel Eriksson, Jacob Oldfield (Australian Synchrotron)

-   Alberto Nardella (MAX IV)

-   Annie Heroux (ex Elettra)

    1.  ## Apologies

None

#  {#section .list-paragraph}

## OpenAPI

In discussing the adoption of OpenAPI, JO commented that pure JSON
Schema would be a better choice. OpenAPI is an extension of JSON Schema,
but OpenAPI is mainly intended for REST APIs, and the MXLIMS is not
particularly intended for this purpose. The meeting agreed to use JSON
Schema for the API specification.

The following links were proposed as a good source for JSON schema
examples and tools.

https://github.com/compose-spec/compose-spec

https://json-schema.org/implementations

https://github.com/compose-spec/compose-spec/blob/master/schema/compose-spec.json

https://www.schemastore.org/json/

## Guidelines and naming styles

The choice for naming variables and fields was between snake_case and
camelCase. Except for Diamond, all participants preferred snake_case
(all those Pythons around ;-) ). It was agreed to use snake_case for the
API.

For a reference see
https://www.freecodecamp.org/news/programming-naming-conventions-explained/

## API model structure

On the specific detail of core abstract classes the meeting agreed that
there was a need for at a minimum something like the complexity proposed
in
<https://github.com/rhfogh/mxlims_data_model/wiki/Initial-draft-proposal,-version-0.0.3>.
We would want to be able to support data provenance tracking and merging
individual scans into larger data sets, which would require tracking job
input and output, and the connections between individual data sets. RF
promised to write up a simpler version (version 0.0.4) which could then
be used unless problems developed. **ACTION: RF**.

More generally the meeting felt it was better to concentrate on the
concrete tasks we needed to support and use this as the starting point
for modeling. EP proposed to start with the end results (structures) and
work back from there, whereas PK pointed out that 'the' end results was
different for an experimentalist (acquired images), a Contract Research
Organisation (reflection files), or a PI / manager (structures). KS
underlined the need for tracking data provenance; the SLS explicitly
tracks merging (and re-merging) of data sets, for either SSX or
multi-sweep experiments, and uses a mergeId to identify the result. DE
agreed with this approach. KL reported that ISPyB had tables like
DataCollection, DataCollectionGroup, and ProcessingJob. JH quoted Alex
de Maria as saying that the ICAT LIMS being built by the ESRF had found
a way of holding links between different Datasets, even if the official
ICAT documentation does not seem to support them (RF). CV pointed to
JCSG as a very good example of modelling and displaying data provenance,
and promised to put the relevant data on to github -- the project web
site being dead and badly represented on the Wayback Machine **ACTION:
CV**. JO pointed out, to general agreement, that the purpose of the
project should be to make a general API that was system-agnostic, and to
identify common fields, rather than to make a complete and unavoidably
rigid representation (such as, for instance mmCIF).

# **Future work**

The next step should be to gather use cases to work from. For a start
there should be a specific location on Github to put them in (**ACTION:
RF, CV**). At the next meeting people from each site should present
their use cases in a 15min overview talk. **ACTIONS: KS** volunteered to
present the SLS, **JH and KL** would have someone from the Data Analysis
group present cases from Diamond, **DE** would present their in-progress
models, and **Global Phasing** would present use cases of
multi-orientation data collection and processing, and the summary pdf
used to present the results. RF would contact the ESRF to see if they
could make a presentation as well (**ACTION: RF**).

## Next Meeting

The next meeting should take place in late March at the same time and
meeting site. RF should send out an enquiry mail around March 13, and
then set up a Doodle pool for the meeting proper, when it was clear how
close people were to being ready. **ACTION**: **RF**
