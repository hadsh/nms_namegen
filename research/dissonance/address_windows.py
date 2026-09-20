"""Is dissonance an address window, the way purple is?

Purple is not drawn at all: it is the plain SSI range 0x3E9-0x429. That is
the one mechanism in this route that assigns a system-wide property straight
from the address, so if dissonance worked the same way the positives would
fall in a contiguous range of some address field. They do not.
"""
import sys

from trace import load, trace

sys.path.insert(0, "../..")
from nms_namegen.region import voxelAttributes


def fields(row):
    portal_code = int(row["sysaddress"], 16)
    ssi = (portal_code & 0xFFF00000000) >> 32
    voxel = voxelAttributes(portal_code & 0xFFFFFFFFFFF)
    traced = trace(portal_code, row["galaxy_namegen"])
    return dict(
        ssi=ssi,
        x=portal_code & 0xFFF,
        y=(portal_code & 0xFF000000) >> 24,
        z=(portal_code & 0xFFF000) >> 12,
        galaxy=row["galaxy_namegen"],
        ssi_mod8=ssi % 8,
        ssi_mod16=ssi % 16,
        ssi_high=ssi >> 4,
        renegade=voxel["guide_star_renegade_count"],
        star_type=traced["attrs"]["star_type"],
        bodies=len(traced["ps"]["planet_seeds"]),
    )


def best_window(values, labels):
    """Best agreement from "positive iff the value falls in [lo, hi]"."""
    n = len(values)
    counts = {}
    for value, label in zip(values, labels):
        counts.setdefault(value, [0, 0])
        counts[value][label] += 1
    unique = sorted(counts)
    npos = sum(labels)
    best = (max(npos, n - npos) / n, None)
    for i in range(len(unique)):
        inside_pos = inside_neg = 0
        for j in range(i, len(unique)):
            inside_pos += counts[unique[j]][1]
            inside_neg += counts[unique[j]][0]
            agreement = (inside_pos + (n - npos - inside_neg)) / n
            if agreement > best[0]:
                best = (agreement, (unique[i], unique[j]))
    return best


def main():
    rows = load()
    labels = [1 if row["label"] else 0 for row in rows]
    table = [fields(row) for row in rows]
    n = len(rows)
    npos = sum(labels)
    print("n=%d dissonant=%d majority=%.4f" % (n, npos, max(npos, n - npos) / n))
    for key in table[0]:
        agreement, window = best_window([f[key] for f in table], labels)
        print("  %-10s best window %-20s agreement %.4f"
              % (key, window, agreement))
    print("  --- single address bits ---")
    bits = []
    for bit in range(44):
        values = [(int(row["sysaddress"], 16) >> bit) & 1 for row in rows]
        agree = sum(1 for v, l in zip(values, labels) if v == l)
        bits.append((max(agree, n - agree) / n, bit))
    bits.sort(reverse=True)
    for agreement, bit in bits[:5]:
        print("    bit %2d  agreement %.4f" % (bit, agreement))


if __name__ == "__main__":
    main()
