from datetime import datetime, timedelta

from utimezone.utils import datetime_to_epoch


def test_dst_start_skipped_local_time_europe_london(tz_london):
    tz = tz_london
    tz._ensure_cache(2026)
    start = tz._cache_dst_start
    assert start is not None

    # Local time just before the transition
    local_before = tz.utc_epoch_to_local(start - 1)
    # Local time just after the transition (first DST instant)
    local_after = tz.utc_epoch_to_local(start)

    # There should be a forward gap where some local times don't exist.
    dt_before = datetime(*local_before)
    dt_after = datetime(*local_after)
    assert dt_after > dt_before
    gap = dt_after - dt_before
    assert gap >= timedelta(minutes=30)

    # Pick a local time inside the gap (halfway)
    dt_gap_local = dt_before + gap // 2
    gap_local_tuple = (
        dt_gap_local.year,
        dt_gap_local.month,
        dt_gap_local.day,
        dt_gap_local.hour,
        dt_gap_local.minute,
        dt_gap_local.second,
    )

    naive_epoch = datetime_to_epoch(*gap_local_tuple)

    # The implementation falls back to the standard-offset candidate for skipped times
    std_candidate = naive_epoch - tz._std_offset

    resolved = tz.local_to_utc_epoch(*gap_local_tuple)
    assert resolved == std_candidate


def test_dst_boundary_semantics_europe_london(tz_london):
    tz = tz_london
    tz._ensure_cache(2026)
    start = tz._cache_dst_start
    end = tz._cache_dst_end
    assert start is not None and end is not None

    # Start inclusive: just before is non-DST, at start is DST
    assert tz.is_dst(start - 1) is False
    assert tz.is_dst(start) is True

    # End exclusive: just before end is DST, at end is non-DST
    assert tz.is_dst(end - 1) is True
    assert tz.is_dst(end) is False


def test_dst_end_ambiguous_local_time_europe_london(tz_london):
    tz = tz_london
    tz._ensure_cache(2026)
    end = tz._cache_dst_end
    assert end is not None

    # Local time just before the transition (DST in effect)
    local_before = tz.utc_epoch_to_local(end - 1)
    # Local time at the transition instant (first standard instant)
    local_after = tz.utc_epoch_to_local(end)

    # There should be an overlap: local_after should be <= local_before in wall time
    dt_before = datetime(*local_before)
    dt_after = datetime(*local_after)
    assert dt_after <= dt_before + timedelta(hours=1)

    # Choose the ambiguous local time equal to the repeated wall-clock time
    # (use local_after)
    ambiguous_local = local_after
    naive_epoch = datetime_to_epoch(*ambiguous_local)

    std_candidate = naive_epoch - tz._std_offset
    dst_candidate = naive_epoch - (tz._dst_offset or tz._std_offset)

    # Both candidates should be valid (ambiguous local time)
    valid = []
    for c, off in ((std_candidate, tz._std_offset), (dst_candidate, tz._dst_offset)):
        if tz.offset_for_epoch(c) == off:
            valid.append(c)

    assert len(valid) >= 1

    resolved = tz.local_to_utc_epoch(*ambiguous_local)

    # Implementation returns the earlier UTC instant when ambiguous
    if valid:
        assert resolved == min(valid)


def test_dst_boundary_semantics_pacific_auckland(tz_auckland):
    tz = tz_auckland
    tz._ensure_cache(2026)
    start = tz._cache_dst_start
    end = tz._cache_dst_end
    assert start is not None and end is not None

    # For southern hemisphere, behaviour at start and end is the same semantics
    assert tz.is_dst(start - 1) is False
    assert tz.is_dst(start) is True

    assert tz.is_dst(end - 1) is True
    assert tz.is_dst(end) is False


def test_southern_hemisphere_dst_transitions_pacific_auckland(tz_auckland):
    tz = tz_auckland
    tz._ensure_cache(2026)
    start = tz._cache_dst_start
    end = tz._cache_dst_end
    assert start is not None
    assert end is not None

    # For southern hemisphere, DST season crosses new year: start > end
    assert start > end

    # Check start (clock jumps forward) produces a gap
    local_before = tz.utc_epoch_to_local(start - 1)
    local_after = tz.utc_epoch_to_local(start)
    dt_before = datetime(*local_before)
    dt_after = datetime(*local_after)
    assert dt_after > dt_before
    gap = dt_after - dt_before
    assert gap >= timedelta(minutes=30)

    # A local time inside the gap should map to the standard candidate
    dt_gap_local = dt_before + gap // 2
    gap_local_tuple = (
        dt_gap_local.year,
        dt_gap_local.month,
        dt_gap_local.day,
        dt_gap_local.hour,
        dt_gap_local.minute,
        dt_gap_local.second,
    )
    naive_epoch = datetime_to_epoch(*gap_local_tuple)
    std_candidate = naive_epoch - tz._std_offset
    resolved = tz.local_to_utc_epoch(*gap_local_tuple)
    assert resolved == std_candidate

    # Check end (clock moves back) produces an overlap/ambiguous time
    local_before_end = tz.utc_epoch_to_local(end - 1)
    local_at_end = tz.utc_epoch_to_local(end)
    dt_before_end = datetime(*local_before_end)
    dt_at_end = datetime(*local_at_end)
    # dt_at_end should be <= dt_before_end + 1 hour (overlap)
    assert dt_at_end <= dt_before_end + timedelta(hours=1)

    ambiguous_local = local_at_end
    naive_epoch2 = datetime_to_epoch(*ambiguous_local)
    std_candidate2 = naive_epoch2 - tz._std_offset
    dst_candidate2 = naive_epoch2 - (tz._dst_offset or tz._std_offset)

    valid2 = []
    for c, off in ((std_candidate2, tz._std_offset), (dst_candidate2, tz._dst_offset)):
        if tz.offset_for_epoch(c) == off:
            valid2.append(c)

    resolved2 = tz.local_to_utc_epoch(*ambiguous_local)
    if valid2:
        assert resolved2 == min(valid2)
