def overpass_value(fp, date, aoi_geom_wgs, aoi_area, reference_date, max_diff_hours):

        diff_hours = abs((date - reference_date).total_seconds() / 3600)
        if diff_hours > max_diff_hours:
            return 0.0

        # 1 = perfect match, 0 = bad
        timepct = (max_diff_hours - diff_hours) / max_diff_hours

        intersection = aoi_geom_wgs.intersect(fp)

        # 1 = complete overlap, close to 0 = hardly any
        interpct = intersection.area / aoi_area

        if interpct == 0:
            return 0.0
        else:
            return interpct * timepct


def get_closest_overpass(parsed_entries, aoi_geom_wgs, reference_date, max_diff_hours=48):
    aoi_area = aoi_geom_wgs.area
    entry_values = []
    for e in parsed_entries:
        value = overpass_value(
                fp=e['footprint'],
                date=e['start_date'],
                aoi_geom_wgs=aoi_geom_wgs,
                aoi_area=aoi_area,
                reference_date=reference_date,
                max_diff_hours=max_diff_hours)
        entry_values.append(value)
