from extractors import saatchi_artworks, saatchi_artists, artsy
from infra import gcp

saatchi_artworks.get_all_artworks_info('art_data_files', 'saatchi_artworks_links.txt', 'saatchi_artworks_info1.csv', 'saatchi_failed_artworks_urls.json')

# gcp.retrieve_file_from_gcs('art_data_files', 'saatchi_artworks_info.csv', 'saatchi_artworks_info.csv')

# saatchi_artists.get_all_artists_info('art_data_files', 'saatchi_artists_info.json', 'saatchi_artworks_info.csv')

# artsy.extract_artsy_data('artworks')
