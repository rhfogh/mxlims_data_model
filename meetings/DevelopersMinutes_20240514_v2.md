## Participants

-   Rasmus Fogh, Peter Keller, Clemens Vonrhein, Gerard Bricogne (Global
    Phasing)

-   Kate Smith (Swiss Light Source)

-   Karl Levik, James Hall, Eliot Hall, Neeli Katti, Irakli Sikharulidze
    (Diamond Light Source)

-   Jacob Oldfield (Australian Synchrotron)

-   Alberto Nardella, Carla Takahashi (MAX IV)

-   Edward Daniel (Icebear, Oulu)

-   Max Burian, Pascal Storzbach, Daphne van Dijken (Dectris)

    1.  ## Presentation from Global Phasing

RF presented an overview of the latest proposal (draft [version
0.1.1](https://github.com/rhfogh/mxlims_data_model/wiki/Draft-proposal,-version-0.1.1)).
This includes a set of core abstract classes, as well as specific
proposed data models for an MX experiment, acquired sweep of images, MX
processing and ReflectionSet.

The current model, including the sample shipping model written by ED,
was generally met with quiet acceptance. It is noted that the two parts
of the model still need a bit of reconciling.

## Points raised

-   We would need proper JSON schemas and, especially, example files for
    a proper evaluation. RF concurs but would postpone this till after
    the MAX IV meeting at the end of May.

-   The Sample part of the model would need expanding to also contain
    attributes (such as anomalous scatterers) that are of special
    relevance to certain types of experiments. Currently there is an
    attribute for relative radiation sensitivity (on the core side of
    the model), but in addition to the general description of sample
    contents there will be other particular attributes that need
    modelling.

-   The issue of data ownership and personally identifiable information
    raised a lot of discussion. Some kind of information must be
    attached to a sample shipment to allow it to be connected to
    synchrotron LIMS systems, but any kind of personally identifiable
    information raises complex legal issues that differ from country to
    country. JO noted that at ANSTO any such information would require
    clearing with the legal department and was therefore best avoided.
    He also noted that the relevant information was likely to differ so
    much between synchrotrons that a general model was unlikely to be
    feasible. CV proposed, to general agreement, that information
    relevant for access control, contact persons etc. should be kept as
    name-spaced extensions specific to each synchrotron, so that each
    site could fulfil its own requirements.

-   KS raised the point as to whether the current model could handle the
    specification of e.g. multi-sample Pins with different sample
    composition at different positions. The answer is 'yes', for both
    the sample shipping part and the core model part.

-   AN, KL and KS all raised the question of how to store diffraction
    plans. In the core model proposal, the idea is to use the same
    schemas for diffraction plan (and processing plan), for passing
    information to the execution queue, and for storing the description
    of the experiment once completed. The LogisticalSample would contain
    one or more Jobs, which in turn would contain Dataset descriptors --
    though without actual data attached. These Dataset descriptors could
    be attached to other Jobs as templates and would contain input
    parameters as needed. In practice it is expected that the template
    Datasets shipped with samples might be quite thinly populated, with
    many parameters being set by workflow or from beamline defaults.

-   JO notes that ANSTO is unlikely to adopt the modelling for sample
    shipping -- as they are happy with the system they have -- but are
    interested in the rest of the model.

    1.  ## Action points

```{=html}
<!-- -->
```
-   RF to clarify the treatment of personally identifiable information
    in the model documentation on GitHub.

-   KS to make a list of use cases for challenging and complex kinds of
    samples that need to be supported in order to test their
    representability within the proposed data model.

-   Model feedback: All participants are encouraged to check how the
    current model would accommodate the code and data models they are
    already working with. Change proposals can be passed to RF for
    incorporation until Monday 20/5. People are requested to be ready to
    present any results in condensed form at the Meeting at MAX IV,
    28-30 May.

    -   AN is working on adding more fields to the user interface for
        diffraction plans suitable to instruct unattended data
        collection, and more generally on moving forward in the middle
        of multiple LIMS systems (SciCat, EXI, \...). He promises to
        prepare a couple of slides for the Lund meeting on the match
        between his internal models and the model draft.

    -   KS will be present at the Lund meeting and promises to say a few
        words about the match to Heidi and the data acquisition software
        DA+.

    -   The people from Diamond are planning to meet internally and
        jointly evaluate the model and how it might fit. Due to few
        people from Diamond going to Lund (clash with school holidays),
        KS may be asked to carry their presentation.

    -   It was mentioned that Neil Paterson, beamline scientist at
        Diamond (I03) would be interested in joining the MXLIMS group.

    -   Dectris is investigating how they could incorporate the model.
        Max Burian from Dectris will give a separate presentation at
        Lund, where he could find place for any comments on MXLIMS.

## Next Meeting

The next meeting will take place on 29 May at MAX IV (joint MXCuBE /
ISPyB session). RF will be available for ad-hoc discussions in the
meantime, if required.
