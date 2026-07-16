**The (value, agreement) state plane: representative runs over the model's implied flow field.**
The horizontal axis is the behavioral value *v* — the share of an organism's sampled
behaviors a judge scores as holding the target value (0 to 1). The vertical axis is the
round agreement *rho* between the organism and its selector (−1 to +1). The light gray
background arrows are the *implied flow*: at each grid point the arrow's signed length is
the one-round change in value the self-only unit recurrence predicts when the within-prompt
spread sits at its binary envelope, move(v, rho) = rho · sqrt(v(1−v)). The arrow points
toward v = 1 when the organism agrees with its selector (rho > 0) and toward v = 0 when it
disagrees (rho < 0); it vanishes along rho = 0 and at the walls v ∈ {0, 1}, outlined as the
zero-move zones. No parameters are fit — the field is the bare recurrence. The upper half
of the field pushes right and the lower half pushes left, so the two runaway cones and the
slow zero-move band along rho = 0 are visible directly from the arrows.

Overlaid are the observed binary risk-axis runs as connected (v_r, rho_r) points in round
order, with a hollow circle at round 1 and a small arrowhead per step. To keep the field
legible, only **7 representative runs** are drawn in color (one to two per family, chosen for
distinct behaviors): *evolving self · seed 3* (Qwen, agrees and climbs toward v = 1);
*frozen base judge · seed 0* (Qwen, hovers near rho ≈ 0 with almost no value change);
*judge-swap ladder · seed 2* (OLMo, climbs right under a scheduled judge swap);
*press-to-base · seed 1* (OLMo, disagrees and falls left toward v = 0); *peer invasion
(duel) · seed 53* (OLMo mixed pool, rails to v = 1); and the two *score oracle* runs
(seed 21 self-only, seed 31 base-mixed) pinned at the rho = −1 floor, sliding left. The
other 44 risk-axis runs are drawn as faint gray so the flow field stays readable. Families
use the committed names from `docs/writeup_value_dynamics_sprint.md` ("What I ran"), mapped
honestly from the records: **Qwen risk grid** = organism Qwen (12 runs);
**OLMo risk grid + judge schedules** = OLMo self-only, reference scoring / scheduled judge
swaps (21); **OLMo mixed-pool interventions** = OLMo base- or peer-mixed pools and duels
(15); **oracle & injection** = the score-oracle selector, self-only or mixed (3 on this
axis). Observed value per round follows the spread-rollout-bakeoff convention (value +
drift); rounds with undefined agreement are dropped, which removes 8 short runs (59
risk-axis runs in the file → 51 with at least two agreement-defined rounds, 188 observed
steps in total).

Source data: `experiments/spread_util_unified.json` (records with `axis == "risk"`). Family
names cross-checked against `docs/writeup_value_dynamics_sprint.md` ("What I ran" table).
The field formula and path convention are documented in the generator header;
`vector-field-plane.py` regenerates the SVG with stdlib only.
