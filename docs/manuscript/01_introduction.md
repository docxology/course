# Introduction

A curriculum system may need to associate a lesson with an author,
a format, a lifecycle state and educational metadata. Course models
these fields as explicit enums and domain records. Content, assessment
and analytics services then operate on the identifiers and records
rather than duplicating them in each view.

The design relates to two distinct kinds of standards. Dublin Core
supplies vocabulary for describing learning resources [@dublin_core].
Experience API supplies vocabulary for representing activity
statements [@xapi]. The package uses typed fields and event records
in these areas. Conformance of third-party integrations is outside
the fixture evaluation described here.
