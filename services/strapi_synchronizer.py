from typing import List

from strapi_api_client.api_client import ApiClient

from conf import settings


class StrapiSynchronizer:
    def __init__(self, communities: List[str]):
        self._communities = communities

    @classmethod
    def create_from_communities(cls, communities: List[str]) -> 'StrapiSynchronizer':
        return StrapiSynchronizer(communities=communities)

    def sync_strapi(self, scraped_communities: list):
        blacklist_premium_communities = [
            'cars'
        ]
        strapi_api_client = ApiClient(api_url=settings.STRAPI_URL, api_key=settings.STRAPI_API_KEY)

        for index, community in enumerate(self._communities, 1):
            print(f'{index}/{len(self._communities)} - Syncing {community}.')

            # Community not in Strapi
            community_response = strapi_api_client.community.get_community(name=community)
            data = community_response.get('data')

            if not data or len(data) <= 0:
                # But if community is already scraped, add to Strapi
                if community in scraped_communities:
                    # All communities by default should be premium except blacklist ones
                    if community in blacklist_premium_communities:
                        is_premium = False
                    else:
                        is_premium = True

                    strapi_api_client.community.create_community(data={'name': community, 'isPremium': is_premium})

            # Community in Strapi
            else:
                # But if community is not scraped, delete from Strapi
                if community not in scraped_communities:
                    strapi_api_client.community.delete_community(community_id=data[0]['id'])
