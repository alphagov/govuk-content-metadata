from src.make_strata.preprocess_text import extract_text_from_content_details
from src.make_strata.preprocess_text import extract_text_from_html
from src.utils.helpers_arrays import flatten_list_of_lists
from src.utils.helpers_arrays import flatten_list_of_str_dict

from typing import List


def process_url_and_metadata(item):
    """

    :param item:
    :return:
    """

    if "expanded_links" in item.keys():
        if "organisations" in item["expanded_links"]:
            item["organisations"] = extract_organisations(item["expanded_links"])

        if "taxons" in item["expanded_links"]:
            taxon_list = []
            for taxon in item["expanded_links"]["taxons"]:
                taxon_chain = chain_taxons(taxon, [])
                taxon_list.append(taxon_chain)

            item["taxons"] = taxon_list

        del item["expanded_links"]

    item["withdrawn"] = (
        "withdrawn_notice" in item.keys() and not item["withdrawn_notice"] == {}
    )
    if item["withdrawn"]:
        item["withdrawn_at"] = item["withdrawn_notice"]["withdrawn_at"]
        item["withdrawn_explanation"] = extract_text_from_content_details(
            item["withdrawn_notice"]["explanation"]
        )

    return item


def process_content_item(item):
    """

    :param item:
    :return:
    """

    # main body of text from item['details']['body'] or item['details']['parts']['body'] etc
    item["text"] = resize_for_input_limits(
        extract_text_from_content_details(item["details"])
    )

    item["description"] = (
        item["description"]["value"] if "description" in item.keys() else ""
    )

    # contact details (1)
    if item["schema_name"] == "contact":
        item["contact_details"] = extract_details_from_contact_doctype(item)

    # slugs and titles from details.parts
    if "parts" in item["details"].keys():
        item["details_parts"] = extract_slug_title_from_details_parts(
            item["details"]["parts"]
        )

    if "expanded_links" in item.keys():
        # contact details (2)
        if "ordered_contacts" in item["expanded_links"]:
            item["contact_details"] = extract_contact_details_from_organisation(item)

        del item["expanded_links"]

    item["withdrawn"] = (
        "withdrawn_notice" in item.keys() and not item["withdrawn_notice"] == {}
    )
    if item["withdrawn"]:
        item["withdrawn_at"] = item["withdrawn_notice"]["withdrawn_at"]
        item["withdrawn_explanation"] = extract_text_from_content_details(
            item["withdrawn_notice"]["explanation"]
        )

    return item


# def extract_html_content(item):
#    if (
#        "body" in item["details"].keys()
#        and item["details"]["body"] is not None
#        and any(item["details"]["body"])
#    ):
#        html_content = list(
#            filter(
#                lambda content: "content_type" in content
#                and content["content_type"] == "text/html",
#                item["details"]["body"],
#            )
#        )
#
#        if any(html_content):
#            return html_content[0]["content"]
#
#    return ""


def extract_slug_title_from_details_parts(details_parts: List[dict]) -> List[dict]:
    """
    Args:
        details_parts: the item['details']['part'] field of a content item

    Returns:
        The extracted [{'title': str, 'slug': str}] from the item["details"]["parts"].
    """
    return [{key: part[key] for key in ["title", "slug"]} for part in details_parts]


def extract_details_from_contact_doctype(content_item: dict) -> str:
    """
    Extract the contact details and any text from the `details` field of contact document type.
    """
    assert (
        content_item["schema_name"] == "contact"
    ), f"`{content_item['_id']}` is not a document_type contact."

    elements_list = [
        v
        for k, v in content_item["details"].items()
        if k
        in [
            "title",
            "description",
            "phone_numbers",
            "post_addresses",
            "email_addresses",
        ]
    ]
    flat_elements_list = [x for xs in elements_list for x in xs]
    flat_list_of_strings = [
        extract_text_from_html(v)
        for elem in flat_elements_list
        for _, v in elem.items()
        if v != ""
    ]
    return " ".join(flat_list_of_strings).strip()


def extract_contact_details_from_organisation(content_item: dict) -> str:
    """
    Extract the contact details from document_type 'organisation'.
    Contact details are stored as a list of dictionaries in the page's
    expanded_links.ordered_contacts.

    Returns the contact details as string text.
    """
    elements_list = content_item["expanded_links"]["ordered_contacts"]
    details_list = [d.get("details") for d in elements_list]
    results = []
    for detail_dict in details_list:
        elements_list = [
            v
            for k, v in detail_dict.items()
            if k
            in [
                "title",
                "description",
                "phone_numbers",
                "post_addresses",
                "email_addresses",
            ]
            and v is not None
        ]
        flat_elements_list = flatten_list_of_lists(elements_list)
        flatten_detail = " ".join(flatten_list_of_str_dict(flat_elements_list)).strip()
        results.append(extract_text_from_html(flatten_detail))
    return " ".join(results).strip()


def extract_organisations(data):
    """

    :param data:
    :return:
    """
    return {
        key: [(v["content_id"], v["title"], v["analytics_identifier"]) for v in value]
        for key, value in data.items()
        if "org" in key
    }


def get_taxon_data(taxon_dict):
    """

    :param taxon_dict:
    :return:
    """
    return {
        "title": taxon_dict["title"],
        "content_id": taxon_dict["content_id"],
        "base_path": taxon_dict["base_path"],
        "document_type": taxon_dict["document_type"],
    }


def index_taxon_chain(taxon_list):
    """

    :param taxon_list:
    :return:
    """
    for i, taxon_dict in enumerate(taxon_list):
        taxon_dict["level"] = len(taxon_list) - i
    return taxon_list


def chain_taxons(taxon, taxon_list):
    """

    :param taxon:
    :param taxon_list:
    :return:
    """
    if "links" in taxon.keys():
        if "parent_taxons" in taxon["links"]:
            return chain_taxons(
                taxon["links"]["parent_taxons"][0], taxon_list + [get_taxon_data(taxon)]
            )
        elif "root_taxon" in taxon["links"]:
            return index_taxon_chain(taxon_list + [get_taxon_data(taxon)])


def resize_for_input_limits(text):
    """
    Neo4j has a max input size (by default) of 2MB for content item text - adhere to this to avoid import failures.
    Max input size is 2097152 bytes. This has been adjusted below to allow for the error message of 53 bytes.
    :param text:
    :return:
    """
    if len(text) > 2097152:
        return text[:2097099] + "... DATA HAS BEEN TRIMMED DUE TO SIZE CONSTRAINTS ..."

    return text
