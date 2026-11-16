"""CHEL hexagon linkage helpers (audits/wearables_chel.py)."""
import pandas as pd
import pytest

from audits import wearables_chel as ch
from audits import wearables_healthkit as hk
from audits import wearables_rare as dw
from audits import wearables_timing as wt

CH = "p.C_v9_R2_clad_chel_hex_offcycle"


def _schema():
    rows = [("p.cdr", "person", "person_id", "INT64"), ("p.cdr", "person", "location_id", "INT64"),
            ("p.cdr", "location", "location_id", "INT64"), ("p.cdr", "location", "zip", "STRING"),
            (CH, "participant_hex", "person_id", "INT64"), (CH, "participant_hex", "h3_id", "STRING"),
            (CH, "participant_hex", "start_date", "DATE"),
            (CH, "loc_history", "person_id", "INT64"), (CH, "loc_history", "location_id", "INT64"),
            (CH, "hex_location", "location_id", "INT64"), (CH, "hex_location", "hex_id", "INT64"),
            (CH, "chel_indicators", "h3_id", "STRING"), (CH, "chel_indicators", "pm25", "FLOAT64"),
            (CH, "readme", "text", "STRING"),
            (CH, "clad_location_history_hex3", "research_id", "INT64"),
            (CH, "clad_location_history_hex3", "start_date", "STRING"),
            (CH, "clad_location_history_hex3", "h3_id", "STRING"),
            (CH, "clad_chel_2024", "hex_id", "INT64"), (CH, "clad_chel_2024", "h3_id", "STRING")]
    return pd.DataFrame(rows, columns=["dataset", "table_name", "column_name", "data_type"])


def test_candidates_and_links():
    assert ch.chel_candidates(["p.cdr", CH, "p.C_V9_R6_offcycle_nlp", "p.C_V9_R3_aou_biospecimen"],
                              "p.cdr") == [CH]
    links, ind = ch.find_links(_schema())
    names = sorted(ch.link_name(k) for k in links)
    assert names == [f"{CH}.clad_location_history_hex3.h3_id",
                     f"{CH}.loc_history → {CH}.hex_location.hex_id",
                     f"{CH}.participant_hex.h3_id",
                     f"p.cdr.person → {CH}.hex_location.hex_id"]
    assert [(i["table"], i["hex_col"]) for i in ind] == [
        (f"{CH}.chel_indicators", "h3_id"), (f"{CH}.clad_chel_2024", "h3_id")]
    r = next(k for k in links if "clad_location" in k["table"])
    assert "SAFE_CAST(t.research_id AS INT64) AS person_id" in ch.link_sql(r)


def test_link_sql_formats_hex():
    links, _ = ch.find_links(_schema())
    d = next(k for k in links if k["kind"] == "direct")
    assert "LOWER(TRIM(t.h3_id)) AS h" in ch.link_sql(d)
    loc = next(k for k in links if k["table"] == "p.cdr.person")
    s = ch.link_sql(loc)
    assert "LOWER(FORMAT('%x', l.hex_id))" in s and "ON l.location_id = t.location_id" in s


def test_events_hex_and_cohort_rows():
    ev = pd.DataFrame([(pid, wt.ALL, 10, True, False, None, 20, pid < 25) for pid in range(30)]
                      + [(0, wt.ALL, -3, True, False, None, 20, True)],
                      columns=["pid", "mondo_id", "rel_day", "is_ed", "is_ip", "site",
                               "cov_days", "has_hex"])
    r = ch.events_hex(ev, min_cov=14).set_index("event_class").loc["ed_or_inpatient"]
    assert (r["cov"], r["cov_hex"], r["x_cov_nohex"], r["x_cov_nohex_p"]) == (30, 25, 5, 5)
    c = ch.cohort_rows(pd.DataFrame({"mondo_id": ["M:2", wt.ALL, "M:1"], "n_dx": [50, 300, 200],
                                     "n_wear": [10, 100, 90], "n_wear_hex": [9, 95, 86],
                                     "n_dx_hex": [40, 280, 190]}))
    assert list(c["mondo_id"]) == [wt.ALL, "M:1", "M:2"]
    assert c.iloc[0].x_wear_nohex == 5


def test_sql_parses():
    sqlglot = pytest.importorskip("sqlglot")
    from audits import wearables_events as we
    fb, _ = wt.typed_wear_sql("p.ds", {"activity_summary": {"date"}}, intraday=False)
    base = wt.timing_ctes("p.ds", fb) + we.events_ctes(None).replace("{cdr}", "p.ds").rstrip()
    links, ind = ch.find_links(_schema())
    for k in links:
        ctes = ch.cohort_ctes(base, k)
        for body in (ch.COHORT_HEX_SELECT, ch.SPREAD_SELECT, ch.HEX_EVENTS_SELECT,
                     ch.INDICATOR_SELECT.format(table=ind[0]["table"],
                                                hexpr=ch._hex_expr("i", "h3_id", "STRING"))):
            sqlglot.parse_one(ctes + body, read="bigquery")
        for body in (ch.LINK_ALL_SELECT, ch.LINK_RES_SELECT):
            sqlglot.parse_one(body.format(link=ch.link_sql(k)), read="bigquery")
    assert "has_hex" in ch.HEX_EVENTS_SELECT and "hx.person_id\n" in ch.HEX_EVENTS_SELECT


def test_main_end_to_end_with_fake_bigquery(tmp_path, monkeypatch):
    sc = "biolink:subclass_of"
    nodes = pd.DataFrame(
        [("MONDO:0700096", "biolink:Disease", "human disease", None, None),
         ("MONDO:AI", "biolink:Disease", "autoimmune thing", None, None),
         ("MONDO:A", "biolink:Disease", "disease A",
          "http://identifiers.org/snomedct/123", "rare|orphanet_rare")],
        columns=["id", "category", "name", "same_as", "subsets"])
    edges = pd.DataFrame([("MONDO:AI", "MONDO:0700096", sc), ("MONDO:A", "MONDO:AI", sc)],
                         columns=["subject", "object", "predicate"])
    files = {"mondo_nodes.tsv": tmp_path / "n.tsv", "mondo_edges.tsv": tmp_path / "e.tsv"}
    nodes.to_csv(files["mondo_nodes.tsv"], sep="\t", index=False)
    edges.to_csv(files["mondo_edges.tsv"], sep="\t", index=False)
    concept = pd.DataFrame([(123, "Std A", "SNOMED", "Condition", "123", "S")],
                           columns=["concept_id", "concept_name", "vocabulary_id",
                                    "domain_id", "concept_code", "standard_concept"])
    s = _schema()
    seen = {"sql": []}

    def fake_query(client, sql, params=None):
        seen["sql"].append(sql)
        if "ordinal_position" in sql:
            ds = sql.split("`")[1].removesuffix(".INFORMATION_SCHEMA.COLUMNS")
            return s[s["dataset"] == ds].drop(columns="dataset").reset_index(drop=True)
        if "INFORMATION_SCHEMA" in sql:
            return pd.DataFrame({"table_name": ["activity_summary"], "column_name": ["date"]})
        if "n_multi" in sql and "n_hex_floor" not in sql:
            return pd.DataFrame({"n_persons": [300000], "n_hex": [900], "n_multi": [40000]})
        if "res_digit" in sql:
            return pd.DataFrame({"res_digit": ["3", "not a 15-digit H3 index"],
                                 "n_persons": [300000, 0], "n_hex": [900, 0]})
        if "n_hex_floor" in sql:
            return pd.DataFrame({"n_hex": [300], "n_hex_floor": [40], "n_in_floor_hex": [1500],
                                 "n_multi": [12]})
        if "ind.h" in sql:
            return pd.DataFrame({"n_persons": [2700]})
        if "n_wear_hex" in sql:
            return pd.DataFrame({"mondo_id": ["MONDO:A", wt.ALL], "n_dx": [300, 300],
                                 "n_wear": [100, 100], "n_wear_hex": [95, 95],
                                 "n_dx_hex": [290, 290]})
        if "has_hex" in sql:
            seen["ev"] = params
            return pd.DataFrame([(p, m, 10, True, False, None, 20, p < 25)
                                 for m in ("MONDO:A", wt.ALL) for p in range(30)],
                                columns=["pid", "mondo_id", "rel_day", "is_ed", "is_ip",
                                         "site", "cov_days", "has_hex"])
        if "SELECT * FROM mt" in sql:
            return pd.DataFrame({"concept_id_1": [123], "concept_id_2": [123],
                                 "relationship_id": ["Maps to"]})
        if "UNION DISTINCT" in sql:
            return concept
        return pd.DataFrame({"mondo_id": ["MONDO:A", wt.ALL], "n_dx": [300, 300]})

    monkeypatch.setenv("WORKSPACE_CDR", "p.cdr")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "bill")
    monkeypatch.setattr(ch, "bq_client", lambda billing: object())
    monkeypatch.setattr(ch, "query", fake_query)
    monkeypatch.setattr(ch, "dry_run_bytes", lambda c, q, p=None: 1e8)
    monkeypatch.setattr(dw, "query", fake_query)
    monkeypatch.setattr(dw, "download_cached", lambda v, f, c: files[f])
    out = tmp_path / "out"
    assert ch.main(["--out-dir", str(out), "--chel-dataset", CH, "--flags", "orphanet_rare",
                    "--under", "MONDO:AI", "--exact", "--tag", "ai", "--ip-overnight"]) == 0
    assert seen["ev"]["ip_overnight"] == ("BOOL", True)
    md = (out / "cdr" / "ai_chel-report.md").read_text()
    assert f"## 2. {CH}.participant_hex.h3_id" in md
    assert "All participants: 300,000 with a hexagon, in 900 hexagons" in md
    assert "| 3 | 300,000 | 900 |" in md
    assert f"**{hk.SUPPRESSED} with Fitbit and a hexagon**" in md      # 5 without
    assert "40 hexagons hold >= 20 of them (1,500 persons); <20 have more" in md
    assert f"| {CH}.chel_indicators | 2,700 |" in md
    assert f"| ed_or_inpatient | 30 (30) | {hk.SUPPRESSED} ({hk.SUPPRESSED}) |" in md
    assert (out / "cdr" / "ai_chel-schema.tsv").exists()


def test_main_stops_without_links(tmp_path, monkeypatch):
    monkeypatch.setenv("WORKSPACE_CDR", "p.cdr")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "bill")
    monkeypatch.setattr(ch, "bq_client", lambda billing: object())
    monkeypatch.setattr(ch, "query", lambda c, q, p=None: pd.DataFrame(
        {"table_name": ["person"], "column_name": ["person_id"], "data_type": ["INT64"]}))
    with pytest.raises(SystemExit, match="no table links a person"):
        ch.main(["--out-dir", str(tmp_path), "--chel-dataset", CH])
