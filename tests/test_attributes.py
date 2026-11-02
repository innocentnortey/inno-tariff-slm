"""Regression cases from the 2026-11-01 label review (docs/data/label-review-2026-11-01.md). Each case is a real
description from the review sample, shortened; the review item number is in the test name."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from tariff_slm.data.attributes import (  # noqa: E402
    CONFLICT, evidence, separating_dimension, strip_dimension,
)


def test_09_fiber_threshold_cites_the_wool_not_the_first_fiber():
    desc = "A woman's knit poncho made from a mixed fabric including 52% acrylic and 48% wool, featuring a turtleneck."
    gold = "Containing 23 percent or more by weight of wool or fine animal hair"
    assert evidence(desc, "fiber_content", gold, "Other") == "48% wool"


def test_fiber_threshold_needs_a_stated_percentage():
    desc = "A woman's knit poncho in a soft wool blend with a turtleneck and fringe at the bottom."
    gold = "Containing 23 percent or more by weight of wool or fine animal hair"
    assert evidence(desc, "fiber_content", gold, "Other") is None


def test_26_elastomeric_line_is_fiber_and_spandex_states_it():
    gold = "Of fabric containing by weight 5 percent or more elastomeric yarn or rubber thread"
    assert separating_dimension(gold, "Other") == "fiber_content"
    desc = "a women's lined bodysuit made of 78% nylon and 22% spandex knit fabric, featuring foam bra cups"
    assert evidence(desc, "fiber_content", gold, "Other") == "22% spandex"


def test_28_overcoat_against_anorak_is_garment_type_not_use():
    gold = "Overcoats, carcoats, capes, cloaks and similar garments"
    sib = "Anoraks (including ski-jackets), wind breakers and similar articles"
    assert separating_dimension(gold, sib) == "garment_type"


def test_gloves_against_hockey_gloves_is_use():
    gold = "Other gloves, mittens and mitts, all the foregoing specially designed for use in sports"
    assert separating_dimension(gold, "Ice hockey gloves and field hockey gloves") == "use"


def test_05_unisex_supports_for_women_against_for_men():
    desc = "Closed-toe, below-the-ankle, unisex slip-on shoes made with textile knit upper and rubber/plastic sole"
    assert evidence(desc, "gender_age", "For women", "For men") == "unisex"


def test_unisex_does_not_separate_women_from_girls():
    desc = "Unisex pullover hoodie of 80% cotton and 20% polyester knit fabric with a kangaroo pocket"
    assert evidence(desc, "gender_age", "Women's", "Girls'") is None


def test_adult_cited_for_a_girls_line_is_a_conflict():
    desc = "Adult pullover of 100% acrylic knit fabric with a ribbed collar, cuffs and bottom band"
    assert evidence(desc, "gender_age", "Girls'", "Women's") == CONFLICT


def test_possessive_value_is_a_whole_word():
    desc = "A girl's pullover sweater of 100% cotton knit fabric with long sleeves and a crew neckline"
    assert evidence(desc, "gender_age", "Girls'", "Women's") == "girl's"


def test_man_made_is_not_a_gender_word():
    desc = "Knit top of man made fibers with long sleeves and a crew neckline and a hemmed bottom"
    assert evidence(desc, "gender_age", "Women's", "Girls'") is None


def test_mixed_wearers_are_a_conflict():
    desc = "Men's and women's sleeveless garments of 92% polyester and 8% spandex knit fabric"
    assert evidence(desc, "gender_age", "Men's or boys'", "Women's or girls'") == CONFLICT


def test_knit_alone_does_not_state_knit_to_shape():
    gold = "Knit to shape articles described in statistical note 6 to this chapter"
    assert evidence("Men's rib knit pullover of 60% cotton, 40% rayon", "construction", gold, "Other") is None
    assert evidence("Women's fully fashioned pullover of 100% wool", "construction", gold, "Other") == "fully fashioned"


def test_43_fiber_ablation_never_leaves_numbers_behind():
    desc = ("A knitted work glove constructed of 72.7% aramid, 16.7% glass fiber, 6% acrylic, and 4.6% spandex, "
            "featuring a rubber coating on the palm and backside fingertips")
    out = strip_dimension(desc, "fiber_content")
    assert out is None or ("72." not in out and "aramid" not in out)


def test_46_ablation_with_a_dangling_article_is_rejected():
    desc = "a unisex, closed toe/closed heel, below-the-ankle slip-on shoe with textile upper and lace closure"
    assert strip_dimension(desc, "gender_age") is None


def test_clean_ablation_is_kept():
    desc = ("Women's reversible tank top, 80% nylon, 20% spandex, knitted fabric, sleeveless, racer back style, "
            "scooped front neckline")
    out = strip_dimension(desc, "gender_age")
    assert out and out.startswith("reversible tank top")


def test_with_against_without_fourchettes_is_construction():
    assert separating_dimension("Without fourchettes", "With fourchettes") == "construction"


# Second review round (fresh sample, seed 20261102).
def test_v2_28_soccer_shoe_states_athletic_use():
    gold = "Tennis shoes, basketball shoes, gym shoes, training shoes and the like"
    desc = "Below-the-ankle, lace-up, unisex, closed-toe soccer shoe with rubber or plastic upper and outer sole"
    assert separating_dimension(gold, "House slippers") == "use"
    assert evidence(desc, "use", gold, "House slippers") == "soccer"


def test_v2_33_knit_directly_to_final_shape_counts():
    gold = "Knit to shape articles described in statistical note 6 to this chapter"
    desc = "A women's knit cardigan of 60% cotton and 40% rayon; all panels are knit directly to their final shape."
    assert evidence(desc, "construction", gold, "Other") == "knit directly to their final shape"


def test_v2_40_semicolon_comma_gap_is_rejected():
    desc = ("a pair of casual gloves; outer shell is a knit fabric of 100% polyester with a polyurethane coating; "
            "features include fourchettes and an extended knit cuff with thumb hole; plastic composition stated")
    out = strip_dimension(desc.replace("100% polyester", "polyester;"), "fiber_content")
    assert out is None or ";," not in out


def test_v2_47_article_before_vowel_is_rejected():
    desc = "a woman's open-toe, open-heel flip-flop sandal with a two-piece upper made of molded rubber/plastic"
    assert strip_dimension(desc, "gender_age") is None


def test_v2_03_second_product_for_the_sibling_wearer_is_a_conflict():
    desc = ("The samples include a men's woven jacket of 67% polyester with a full front opening. "
            "The women's knit vest has 81% nylon, 19% spandex fabric.")
    assert evidence(desc, "gender_age", "Men's", "Boys'") == "men's"
    assert evidence(desc, "gender_age", "Men's or boys'", "Women's or girls'") == CONFLICT


# Third round: failures from the prompt-ceiling run (2026-11-01) that were label-side.
def test_v3_singular_brief_and_undershirt_are_garment_words():
    assert evidence("Woman's brief of 53% cotton, 35% modal, 12% elastane knit fabric", "garment_type", "Underpants", "Other") == "brief"
    assert evidence("Woman's minimizing tank undershirt with scoop neck", "garment_type", "Underwear", "Other") == "undershirt"


def test_v3_upper_body_garment_rules_out_a_coverall():
    gold, sib = "Jackets and jacket-type garments excluded from heading 6202", "Coveralls, jumpsuits and similar apparel"
    desc = "A woman's upper body garment of 100% cotton woven fabric with an unsecured full front opening"
    assert evidence(desc, "garment_type", gold, sib) == "upper body garment"


def test_v3_dwr_states_water_resistance():
    desc = "Men's woven jacket, 92% polyester, 8% spandex with treated C0 DWR; unlined, full front zipper"
    assert evidence(desc, "use", "Water resistant", "Other") is not None


def test_v3_new_gap_patterns_are_rejected():
    assert strip_dimension("a women's lined bodysuit made of 78% nylon and 22% spandex knit fabric, featuring foam bra cups", "fiber_content") is None
    assert strip_dimension("A women's raincoat crafted from a two-layer laminated fabric with a scuba hood and storm flap", "garment_type") is None
