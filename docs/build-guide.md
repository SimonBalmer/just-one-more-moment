![Just One More Moment](../hardware/diagrams/project-banner.svg)

# My build guide

I am assembling a step-by-step guide for reproducing my installation. This page links the material I have documented so far. My [enclosure guide](../mechanical/README.md) provides 13 numbered STL files and illustrated geometric assembly views. Tested printer settings, fixings and the application setup are separate from that file set.

## 1. Gather the components

I list the parts in my [bill of materials](../hardware/BOM.md). I still need to complete exact switch details, fixings and some quantities.

## 2. Print the enclosure

Download my [complete enclosure print pack](../mechanical/enclosure-print-pack.zip), or select the [individual numbered STLs](../mechanical/stl/). Print each of the 13 parts once at 100% scale, interpreting the coordinates as mm. Centre, orient and place parts on the bed individually; the exports retain the CAD assembly coordinates.

Use my [six-page enclosure assembly guide](../mechanical/assembly/assembly-guide.pdf) for the part relationships. I include separate display, base and camera views. Purchased-component placeholders and the complete assembly mesh are excluded from the print pack. See the [mechanical notes](../mechanical/README.md) for scale checks, mesh validation and the limits of what the STL geometry specifies.

## 3. Assemble and wire

My [final wiring illustration and connection table](../hardware/WIRING.md) define the connections, including P4 / 5 V through the MIC 1N4001 diode and P34 / GND for the NeoPixel return. The [enclosure drawings](../mechanical/assembly/assembly-guide.pdf) identify the printed parts and their locations. Fit the purchased components and route cables before closing the shells; the drawings do not specify screw dimensions or an experimentally verified fixing sequence.

## 4. Install the software and local model

I will document my working installation process in the [software folder](../software/README.md) after uploading the application and exact environment. I have not included installation commands yet.

## 5. Check the installation

I am preparing a verification sequence for the display, button, button lighting, all 12 NeoPixels, both switches, camera context and countdown behavior. I will check it against my actual code and device.

## 6. Run the experience

I describe the interaction and remaining behavior details in my [operation notes](operation.md).

I track the remaining work in my [publication checklist](TODO.md).
