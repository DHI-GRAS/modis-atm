from earthdata_download import download as eddownload


def find_download_data(date, extent, credentials, download_dir):

    entries = retrieve_entries_all_short_names(date, extent)

    downloaded = {}
    for short_name in urls:
        local_files = []
        for url in urls[short_name]:
            local_file = eddownload.download_data(
                    url, download_dir=download_dir,
                    skip_existing=True,
                    **credentials)
            local_files.append(local_file)
        downloaded[short_name] = local_files

    return downloaded
