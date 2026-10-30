![Just One More Moment](../../../../hardware/diagrams/project-banner.svg)

# Cloud prompt comparison — 30 October 2026

[Prompt notes](../../PROMPTS.md)

This is a compact English account of the original development record. It describes earlier tests; the repository cleanup did not repeat live API or camera runs.

## Method and limits

The original record reports five camera/model runs of 10 statements plus one gift of 5: **75 successful inference requests**, using the project's cloud adapter and `gpt-6.1-terra`, reasoning `none`, temperature 1 and 1,024 output tokens. Each request used one fresh 320 × 240 camera image. Text history was fresh for each run. This was a model/camera comparison, not a complete exhibition test or visitor study.

The JSON files contain **test instructions**, not response transcripts or images. [manifest.json](manifest.json) records hashes from before the comparison. The [runner snapshot](evaluation-runner.py.txt) is historical evidence, not part of installation. The qualitative assessment was made during AI-assisted development, not through a blinded panel. Full generated outputs were not retained, so the observations cannot be independently re-scored from these files.

## Versions and observations recorded at the time

| Run / input | Change | Recorded strengths | Recorded limitations |
| --- | --- | --- | --- |
| [01 baseline](01-baseline.json) | Existing prompt | Understandable thoughts, fear and relief after a gift | Repeated visual motifs; endings felt routine |
| [02 field of view and fear](02-sichtfeld-und-angst.json) | Camera as background, developing thought, direct fear of ending | Less repeated visual description; clearer endings | General life advice; some pleas sounded like button instructions |
| [03 thought and plea](03-gedanke-und-bitte.json) | Everyday thought and a personal request | Thought developed after a gift; clearer fear | Repeated openings; thinking itself remained the main topic |
| [04 concrete thread](04-konkreter-faden.json) | A concrete preference, revision and immediate fear | Preference developed and changed after a gift | Narrow topic range; one unnecessary new-image confirmation |
| [05 repeat check](05-gegenprobe.json) | Same prompt as 04, new history | A wish developed into a decision; no constant picture description | A small object remained the subject for a long time |

The record states that **version 04** was selected and its German system/cues were copied into the live source; the English version was translated accordingly. Run 05 is a repeat check, not a fifth distinct prompt version. The previous source is preserved in [the pre-rollout file](../../prompt-versions/prompts-before-cloud-rollout-2026-10-30.py.txt).

The comparison guided a design choice. It does not prove that the selected prompt always performs better, that visitors felt more empathy, or that generated fear corresponds to experience. `store=false` and discarding local buffers also do not establish provider-side deletion.
