# Adapted from: https://github.com/alphagov/govuk-knowledge-graph/blob/master/src/data/extract_content_store.py
# made python 3.9 compatible

# -*- coding: utf-8 -*-

import logging
import logging.config
import multiprocessing
import warnings
import pandas as pd
import pymongo
from tqdm import tqdm

from src.strata.preprocess_content import process_content_item

warnings.filterwarnings('ignore', category=UserWarning, module='bs4')

EXCLUSION_PUBLISHING_APP = [
    "account-api",
    "businesssupportfinder",
    "calculators",
    "collections-publisher",
    "content-publisher",
    "content-tagger",
    "design-principles",
    "email-alert-frontend",
    "external-link-tracker",
    "feedback",
    "frontend",
    "government-frontend",
    "info-frontend",
    "licencefinder",
    "local-links-manager",
    "manuals-frontend",
    "maslow",
    "need-api",
    "performanceplatform-big-screen-view",
    "policy-publisher",
    "rummager",
    "search-api",
    "service-manual-publisher",
    "share-sale-publisher",
    "short-url-manager",
    "smartanswers",
    "special-route-publisher",
    "static"
]

EXCLUSION_SCHEMA_NAME = [
    "calendar",
    "completed_transaction",
    "coronavirus_landing_page",
    "email_alert_signup",
    "finder",
    "finder_email_signup",
    "generic",
    "generic_with_external_related_links",
    "get_involved",
    "gone",
    "government",
    "history",
    "hmrc_manual",
    "homepage",
    "local_transaction",
    "organisations_homepage",
    "placeholder",
    "placeholder_corporate_information_page",
    "placeholder_document_collection",
    "placeholder_ministerial_role",
    "placeholder_news_article",
    "placeholder_person",
    "placeholder_policy",
    "placeholder_publication",
    "placeholder_speech",
    "placeholder_statistical_data_set",
    "placeholder_world_location_news_article",
    "placeholder_worldwide_organisation",
    "redirect",
    "service_manual_homepage",
    "service_manual_service_toolkit",
    "service_sign_in",
    "simple_smart_answer",
    "smart_answer",
    "special_route",
    "step_by_step_nav",
    "taxon",
    "travel_advice_index",
    "unpublishing",
    "world_location",
    "world_location_news_article"
]

EXCLUSION_DOCUMENT_TYPE = [
    "world_news_story",
    "welsh_language_scheme"
    ]


class ContentStore:
    """
    Interface for extracting and processing the content store data

    Methods
    -------
    extract()
        1) Connects to db as per init_client()
        2) queries data as per query_db()
        3) returns dataframe as per create_content_dataframe()
    """
    def __init__(self, excluded_doctypes=[]):
        """
        Parameters
        ----------
        excluded_doctypes : list
            List of document types to exclude from query as per config/
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info('Processing content store...')

        self.excluded_doctypes = excluded_doctypes

    def init_client(self, address="mongodb://localhost:27017/"):
        """
        :param address:
        :return:
        """
        self.logger.info('Connecting to db...')
        mongo_client = pymongo.MongoClient(address)
        content_store_db = mongo_client["content_store"]
        content_store_collection = content_store_db["content_items"]

        return content_store_collection

    def query_db(self, mongodb_collection, block_list_pubapp=EXCLUSION_PUBLISHING_APP, block_list_schema=EXCLUSION_SCHEMA_NAME, block_list_doctypes=EXCLUSION_DOCUMENT_TYPE):
        """
        :param mongodb_collection:
        :param block_list:
        :return:
        """
        fields = {
            "expanded_links.organisations": 1,
            "expanded_links.taxons": 1,
            "title": 1,
            "locale": 1,
            "schema_name": 1,
            "document_type": 1,
            "content_id": 1,
            "first_published_at": 1,
            "public_updated_at": 1,
            "updated_at": 1,
            "withdrawn_notice": 1,
            "publishing_app": 1}

        query = {"$and": [
            {"publishing_app": {"$nin": block_list_pubapp}},
            {"schema_name": {"$nin": block_list_schema}},
            {"document_type": {"$nin": block_list_doctypes}},
            {"locale": "en"},
            {"phase": "live"}]}

        self.logger.info('Querying db...')
        content_items = mongodb_collection.find(query, fields, no_cursor_timeout=True)
        num_docs = mongodb_collection.count_documents(query)

        return content_items, num_docs

    def multiprocess_content_items(self, content_item_cursor, num_docs):
        """
        :param content_item_cursor:
        :return:
        """
        self.logger.info('Computing cursor size...')
        num_docs = num_docs
        num_work = int(multiprocessing.cpu_count() / 2)
        chunksize, extra = divmod(num_docs, num_work * 4)
        if extra:
            chunksize += 1

        self.logger.info('Got {num_docs} documents. {num_work} workers, {chunksize} items per worker cycle.')
        self.logger.info('Working...')
        pool = multiprocessing.Pool(processes=num_work)
        results = pool.imap(process_content_item, (content_item for content_item in tqdm(content_item_cursor)),
                            chunksize=chunksize)
        pool.close()
        pool.join()
        self.logger.info('Finished...')
        return results

    def create_content_dataframe(self, content_item_list, num_docs):
        """
        :param content_item_list:
        :return:
        """

        cols = ['base_path', 'content_id', 'title',
                'publishing_app', 'locale', 'schema_name',
                'document_type',  'organisations', 'taxons',
                'first_published_at', 'public_updated_at', 'updated_at',
                'withdrawn', 'withdrawn_at', 'withdrawn_explanation']

        self.logger.info(f'Creating content_store dataframe with columns {cols}...')

        df = pd.DataFrame(self.multiprocess_content_items(content_item_list, num_docs))

        self.logger.info('Actually got columns: {df.columns}...')

        self.logger.info(f'Got {df.shape[0]} rows...')

        df.rename(columns={'_id': 'base_path'}, inplace=True)
        df.dropna(subset=["document_type"], inplace=True)

        return df[cols]

    def extract(self):
        content_db = self.init_client()
        content_items, num_docs = self.query_db(content_db)
        content_item_df = self.create_content_dataframe(content_items, num_docs)

        return content_item_df
