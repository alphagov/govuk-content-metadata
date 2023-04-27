"""
SQL script to identify those GOV.UK pages that were either:
- significantly changed (major update)
- newly created
the day before ('yesterday').

Pages are further filtered to only include those whose:
- locale is English,
- status in beta or live
- document type indicates they do contain actual content.
"""

WITH filtered_urls AS (
    SELECT
        url,
        document_type,
        phase,
        locale,
        public_updated_at,
        first_published_at
    FROM `govuk-knowledge-graph.graph.page`
    WHERE locale='en'
    AND (DATE(public_updated_at) = DATE_ADD(CURRENT_DATE(), INTERVAL -1 DAY) OR DATE(first_published_at) = DATE_ADD(CURRENT_DATE(), INTERVAL -1 DAY))
    AND phase IN ('live', 'beta')
    AND document_type IS NOT NULL AND document_type NOT IN (
            'business_support_finder',
            'finder',
            'finder_email_signup',
            'gone',
            'licence_finder',
            'need',
            'placeholder',
            'placeholder_ministerial_role',
            'placeholder_person',
            'placeholder_policy_area',
            'placeholder_topical_event',
            'placeholder_world_location_news_page',
            'world_location_news',
            'redirect',
            'special_route')
    )
    SELECT
        *
    FROM filtered_urls
    ;
