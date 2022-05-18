from src.strata.preprocess_text import extract_text_from_content_details


def process_content_item(item):
    """

    :param item:
    :return:
    """

    if 'expanded_links' in item.keys():
        item['organisations'] = extract_organisations(item['expanded_links'])

        if 'taxons' in item['expanded_links']:
            taxon_list = []
            for taxon in item['expanded_links']['taxons']:
                taxon_chain = chain_taxons(taxon, [])
                taxon_list.append(taxon_chain)

            item['taxons'] = taxon_list

        del item['expanded_links']

    item['withdrawn'] = ('withdrawn_notice' in item.keys() and not item['withdrawn_notice'] == {})
    if item['withdrawn']:
        item['withdrawn_at'] = item['withdrawn_notice']['withdrawn_at']
        item['withdrawn_explanation'] = extract_text_from_content_details(item['withdrawn_notice']['explanation'])

    return item


def extract_html_content(item):
    if 'body' in item['details'].keys() and item['details']['body'] is not None and any(item['details']['body']):
        html_content = list(filter(lambda content: 'content_type' in content
                                   and content['content_type'] == 'text/html', item['details']['body']))

        if any(html_content):
            return html_content[0]['content']

    return ''


def extract_organisations(data):
    """

    :param data:
    :return:
    """
    return {key: [(v['content_id'], v['title'], v['analytics_identifier']) for v in value] for key, value in
            data.items() if "org" in key}


def get_taxon_data(taxon_dict):
    """

    :param taxon_dict:
    :return:
    """
    return {'title': taxon_dict['title'],
            'content_id': taxon_dict['content_id'],
            'base_path': taxon_dict['base_path'],
            'document_type': taxon_dict['document_type']}


def index_taxon_chain(taxon_list):
    """

    :param taxon_list:
    :return:
    """
    for i, taxon_dict in enumerate(taxon_list):
        taxon_dict['level'] = len(taxon_list) - i
    return taxon_list


def chain_taxons(taxon, taxon_list):
    """

    :param taxon:
    :param taxon_list:
    :return:
    """
    if 'links' in taxon.keys():
        if 'parent_taxons' in taxon['links']:
            return chain_taxons(taxon['links']['parent_taxons'][0], taxon_list + [get_taxon_data(taxon)])
        elif 'root_taxon' in taxon['links']:
            return index_taxon_chain(taxon_list + [get_taxon_data(taxon)])


def resize_for_input_limits(text):
    """
    Neo4j has a max input size (by default) of 2MB for content item text - adhere to this to avoid import failures.
    Max input size is 2097152 bytes. This has been adjusted below to allow for the error message of 53 bytes.
    :param text:
    :return:
    """
    if len(text) > 2097152:
        return text[:2097099] + '... DATA HAS BEEN TRIMMED DUE TO SIZE CONSTRAINTS ...'

    return text
