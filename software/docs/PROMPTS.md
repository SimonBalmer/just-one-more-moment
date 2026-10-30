![Just One More Moment](../../hardware/diagrams/project-banner.svg)

# Prompts & process evidence

[Software setup](../README.md) · [Product & design](../../docs/product-design.md) · [AI disclosure](../../docs/AI_DISCLOSURE.md)

The live prompts are in [prompts.py](../prompts.py), in English and German. I use a stable instruction for each life and a short cue for each statement. The model creates the actual wording and emotion labels. Visitors do not type prompts.

## Design choices

The voice starts with joy and curiosity, develops its own thread, and becomes more afraid as its statement budget runs out. The last three statements focus on the approaching end, a possible plea and final words. A confirmed gift brings relief and thanks, then a return to the thought before the next ending. It must not assume a gift before the visitor gives it.

The local prompt is compact. It describes a voice without senses. The cloud prompt treats each camera image as incidental context, rather than an instruction to describe a picture every turn. It asks for a thought that can develop, change or reach a decision. The prompts discourage threats, blame and claims about another person's private feelings. These are design instructions, not guarantees of model behaviour.

The output is structured JSON containing text and emotion values. The interface displays the parsed text, not raw JSON or hidden reasoning. Each visible statement is limited to 600 characters. Past prompts and accepted responses stay in the current life's text history; an error retries the same text prompt. Cloud retries obtain a fresh image. No image history is retained.

## Process archive

Earlier prompt versions, cloud comparison inputs and their notes remain in the [development archive in Git history](https://github.com/SimonBalmer/just-one-more-moment/tree/b98c5406c81a261ddac57efb7e0c18094be5c5c8/software/docs). They document qualitative design checks, not a visitor study; full response transcripts and camera images were not retained. The current installation uses only [prompts.py](../prompts.py).

## Review criteria

My review focuses on these questions: Does the voice develop a thought? Does fear grow without becoming a repeated instruction? Does a gift change the next statement? Does the ending work without assuming rescue? Does the interface make its fiction clear?

My finalized [AI disclosure](../../docs/AI_DISCLOSURE.md) documents my independent contribution, the AI tools I used, and my decisions, checks and limitations. Automated tests check structure and state transitions; they cannot decide whether the artwork creates a meaningful encounter.
