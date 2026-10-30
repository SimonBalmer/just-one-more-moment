![Just One More Moment](../hardware/diagrams/project-banner.svg)

# AI disclosure

**Simon Balmer · Just One More Moment · HSLU PHKI HS26**

I used generative AI throughout this project as a creative, technical and documentation assistant. The concept, physical construction and final design decisions are mine. I remain responsible for the submitted work and its limitations.

## My own contribution

I developed the central idea and philosophical question, chose the interaction and emotional progression across the ten sessions, and defined the device's visual identity and user experience. I designed **all CAD parts myself**, then 3D-printed, soldered, wired and assembled the physical device without generative AI. The enclosure evolved through practical decisions about component placement, connections, maintenance and repair. Pinterest moodboards were more useful for my final design than the AI-generated device mockups, which I largely rejected.

I specified the UI's appearance and behaviour, but **did not write its code myself**. I tested the hardware and software in person, tried to anticipate edge cases, and requested changes where necessary.

## AI tools and influence

| Tool | Use and influence on the final project |
| --- | --- |
| **ChatGPT (OpenAI), including image generation and Work** | Brainstorming and challenging project ideas; combining my ideas into a focused PHKI concept; researching hardware, local models and prompting approaches; creating exploratory device images, sticker artwork, assembly instructions and wiring diagrams. I selected, directed and reviewed the results. |
| **OpenAI Codex in VS Code over SSH** | Set up the Raspberry Pi, ran commands and hardware tests, implemented **all software and the UI**, and helped write and organize the GitHub documentation from my project knowledge and structural goals. This was an iterative process of testing, feedback and revision, not a single prompt. I wrote no code lines myself. Codex also created the SVG project banner. |
| **Ollama / `gemma4:e2b`** | Generates the device's live text locally. My system prompts and session-specific instructions steer its apparent emotions and the planned progression across ten sessions. |
| **OpenAI Responses API / GPT-6.1 Terra** | Generates live text in cloud mode using camera input. The same designed emotional and narrative framing influences its output. |
| **ChatGPT image generation** | Created the PNG project banner from images of my enclosure and my visual instructions. The banner is AI-generated artwork, not a photograph documenting the completed device. |

## Decisions, checks and limits

- **Accepted:** AI-assisted software and documentation when they matched my intended interaction and the device worked in practical tests. I also used generated stickers and illustrations where they suited the visual concept.
- **Changed:** I repeatedly asked Codex to revise UI details and technical behaviour after trying them on the Raspberry Pi. Prompt wording was also refined iteratively, informed in part by publicly available prompting guidance.
- **Rejected:** Most early AI-generated enclosure concepts. I developed the final shape directly in CAD based on available components, assembly needs and my own visual references.
- **Verified:** I checked the assembled hardware and software by using them and considering possible edge cases. **Limit:** Codex performed the implementation, and I could not independently review or fully understand every technical detail within the project timeframe. Functional tests do not guarantee that all code or edge cases are correct. The model's emotional language is deliberately prompted; it is not evidence of genuine feelings or consciousness.

## Process evidence and media

The repository contains the final [hardware files](../hardware), [software](../software) and [project documentation](README.md). Current prompts are described in [prompt notes](../software/docs/PROMPTS.md); earlier prompt material and iterations can also be traced through [Git history](https://github.com/SimonBalmer/just-one-more-moment/tree/b98c5406c81a261ddac57efb7e0c18094be5c5c8/software/docs). The project banner (`../media/project-banner.png` and `../hardware/diagrams/project-banner.svg`) is AI-assisted artwork; photographs of the built prototype are separate documentation. External visual inspiration included Pinterest moodboards; external hardware and prompting guidance informed development.

**Final review and responsibility: Simon Balmer · 30 October 2026**
