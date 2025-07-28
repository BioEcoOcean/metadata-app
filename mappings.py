schema_field_mapping = {
    "project_name": ("legalName", str),
    "shortname": ("name", str),
    "url": ("url", str),
    "description": ("description", str),
    "projid": ("identifier.url", str),
    "projid_type": ("identifier.description", str),
    "license": ("publishingPrinciples.name", str), #need to update this to publishingPrinciples
    
    # Temporal coverage
    "temporal_coverage_start": ("foundingDate", str), 
    "temporal_coverage_end": ("dissolutionDate", str),

    # Contact information
    "contact_names": ("contactPoint.name", list),
    "contact_emails": ("contactPoint.email", list),
    "contact_urls": ("contactPoint.url", list),
    "contact_types": ("contactPoint.contactType", list),
    
    # Spatial coverage
    "spatial_coverage_name": ("areaServed.name", str),
    "spatial_coverage_identifier": ("areaServed.identifier", str),
    "north": ("areaServed.geo.geosparql:asWKT.@value", str),
    "south": ("areaServed.geo.geosparql:asWKT.@value", str),
    "east": ("areaServed.geo.geosparql:asWKT.@value", str),
    "west": ("areaServed.geo.geosparql:asWKT.@value", str),

    # Keywords
    "selected-keywords-json": ("keywords", list),
    #"variables_measured": ("variableMeasured", list),

    # Funding information
    "funder_name": ("funding.funder.name", list),
    "funder_url": ("funding.funder.url", list),
    "funding_name": ("funding.name", list),
    "funding_identifier": ("funding.identifier", list),

    # Outputs
    "outputs": ("makesOffer", list),
}
actions_field_mapping = {
    # Actions: SOPs & platforms, sampling frequency
    "sops": ("actionProcess", list),
    "measurement_platforms": ("instrument", list),
    "sampling_frequency": ("frequency", str),
}
frequency_field_mapping = {
    # Only fields for metadata_frequency
    "frequency": ("frequency", str),
}