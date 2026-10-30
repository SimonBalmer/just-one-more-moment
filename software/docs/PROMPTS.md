# Prompts & process evidence

[Software setup](../README.md) · [Product & design](../../docs/product-design.md) · [AI disclosure](../../docs/AI_DISCLOSURE.md)

The live prompts are in [prompts.py](../prompts.py), in English and German. I use a stable instruction for each life and a short cue for each statement. The model creates the actual wording and emotion labels. Visitors do not type prompts.

## Design choices

The voice starts with joy and curiosity, develops its own thread, and becomes more afraid as its statement budget runs out. The last three statements focus on the approaching end, a possible plea and final words. A confirmed gift brings relief and thanks, then a return to the thought before the next ending. It must not assume a gift before the visitor gives it.

The local prompt is compact. It describes a voice without senses. The cloud prompt treats each camera image as incidental context, rather than an instruction to describe a picture every turn. It asks for a thought that can develop, change or reach a decision. The prompts discourage threats, blame and claims about another person's private feelings. These are design instructions, not guarantees of model behaviour.

The output is structured JSON containing text and emotion values. The interface displays the parsed text, not raw JSON or hidden reasoning. Each visible statement is limited to 600 characters. Past prompts and accepted responses stay in the current life's text history; an error retries the same text prompt. Cloud retries obtain a fresh image. No image history is retained.

## Recorded iteration

The original development notes recorded a move from a simple display to a local web interface, physical button/selector control, synchronised light, statement gifts, optional cloud vision and the once-per-boot opening. Earlier long handover notes and obsolete setup pages are available in Git history rather than duplicated in the final reader path.

| Evidence | What it preserves |
| --- | --- |
| [Before local refinement](prompt-versions/prompts-before-local-refinement-2026-10-30.py.txt) | Earlier full prompt source |
| [Before cloud rollout](prompt-versions/prompts-before-cloud-rollout-2026-10-30.py.txt) | Prompt source immediately before cloud revision 04 |
| [Cloud comparison, 30 October 2026](prompt-experiments/cloud-2026-10-30/README.md) | Five recorded runs across four prompt versions; test inputs and comparison notes |
| [Original development record](https://github.com/SimonBalmer/just-one-more-moment/blob/22725495e9560f38ee870e9db9f0674f85ca5277/software/docs/DEVELOPMENT.md) | Historical implementation notes, including earlier behaviour |

These files are process evidence. The application does not load them. They contain no retained live camera frames or full response transcripts. The recorded comparisons are qualitative development checks, not blinded visitor research or proof of emotions.

## What I still need to judge myself

I must explain which outputs I accepted, changed or rejected and why. A useful review asks: Does the voice develop a thought? Does fear grow without becoming a repeated instruction? Does a gift change the next statement? Does the ending work without assuming rescue? Does the interface make its fiction clear?

The [AI disclosure template](../../docs/AI_DISCLOSURE.md) leaves my independent contribution and personal judgement for me to complete. Automated tests check structure and state transitions; they cannot decide whether the artwork creates a meaningful encounter.
